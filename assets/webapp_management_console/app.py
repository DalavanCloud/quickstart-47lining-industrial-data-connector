import argparse
import logging
import os
import sys
from configparser import ConfigParser
from functools import wraps

import boto3
import datetime

from flask import (
    Flask,
    request,
    session,
    redirect,
    jsonify,
    render_template,
    url_for
)
from osisoft_pi2aws_root import PROJECT_DIR
from service.publishing_manager import PublishingManager
from utils.piaf.af_structure_browser import AfStructureBrowser
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager

from webapp_management_console.app_exceptions import BackendException, raise_backend_exception


REACT_FOLDER = os.path.join(PROJECT_DIR, 'webapp_management_console/app/build')
app = Flask(
    __name__,
    template_folder=REACT_FOLDER,
    static_folder=os.path.join(REACT_FOLDER, 'static')
)
app.logger.setLevel(logging.ERROR)

log = logging.getLogger()


@app.errorhandler(BackendException)
def backend_exception_errorhandler(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


def login_required(fun):
    @wraps(fun)
    def wrapper(*args, **kwargs):
        if session.get('logged_in') is None:
            return redirect(url_for('login'))
        return fun(*args, **kwargs)

    return wrapper


@app.route('/isloggedin', methods=['POST'])
def is_logged_in():
    logged_in = False
    if session.get('logged_in'):
        logged_in = True
    return jsonify({'loggedIn': logged_in})


@app.route('/login', methods=['POST'])
@raise_backend_exception('Unable to log in')
def login():
    if request.json['password'] == app.config['webapp_password'] \
            and request.json['username'] == app.config['webapp_username']:
        session['logged_in'] = True
        session['username'] = request.json['username']
    return is_logged_in()


@app.route('/logout', methods=['POST'])
def logout():
    session['logged_in'] = None
    return is_logged_in()


@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
@raise_backend_exception('Unable to load page')
def any_root_path(path):
    return render_template('index.html')


@app.route('/favicon.ico')
def favicon():
    return app.send_static_file('favicon.ico')


@app.route('/af-structure/view', methods=['POST'])
@raise_backend_exception('Unable to load AF structure')
@login_required
def af_view():
    feed_manager = _create_managed_feeds_manager(app.config)
    structure = feed_manager.get_latest_af_structure(database=app.config['af_structure_database'])

    if structure is None:
        log.error("Cannot acquire AF structure")
        result = {}
    else:
        result = {
            'menu': _get_menu_tree([structure]),
            'nodes': _flatten_tree([structure])
        }
    return jsonify(result)


def _get_menu_tree(nodes):
    tree = {}
    if nodes is None:
        return tree
    else:
        for node in nodes:
            tree[node['path']] = {
                'name': node['name'],
                'assets': _get_menu_tree(node.get('assets'))
            }
    return tree


def _flatten_tree(nodes):
    flat_nodes = {}
    if nodes is None:
        return flat_nodes
    else:
        for node in nodes:
            flat_nodes[node['path']] = {
                'name': node['name'],
                'description': node['description'],
                'attributes': node['attributes'],
                'template': node['template'],
                'categories': node['categories']
            }
            flat_nodes.update(_flatten_tree(node.get('assets')))
    return flat_nodes


@app.route('/backfill', methods=['POST'])
@raise_backend_exception('Cannot send backfill request')
@login_required
def backfill():
    feed_manager = _create_managed_feeds_manager(app.config)
    if request.json.get('allPoints', False):
        points = _get_all_pi_points(feed_manager)
    else:
        points = request.json['feeds']

    query_syntax = request.json.get('syntax', False)

    feed_manager.send_backfill_request(
        query_syntax=query_syntax,
        query=request.json.get('query'),
        feeds=points,
        request_to=request.json.get('to'),
        request_from=request.json.get('from'),
        name=request.json.get('name')
    )

    return 'OK'


@app.route('/interpolate', methods=['POST'])
@raise_backend_exception('Cannot send interpolate request')
@login_required
def interpolate():
    feed_manager = _create_managed_feeds_manager(app.config)
    query_syntax = request.json.get('syntax', False)

    if request.json.get('allPoints', False):
        points = _get_all_pi_points(feed_manager)
    else:
        points = request.json['feeds']

    feed_manager.send_interpolate_request(
        query_syntax=query_syntax,
        feeds=points,
        interval=request.json['interval'],
        interval_unit=request.json['intervalUnit'],
        query=request.json.get('query'),
        request_from=request.json.get('from'),
        request_to=request.json.get('to'),
        name=request.json.get('name')
    )

    return 'OK'


@app.route('/publish', methods=['POST'])
@raise_backend_exception('Cannot send publish request')
@login_required
def publish():
    from_datetime = datetime.datetime.strptime(request.json.get('from'), "%Y-%m-%dT%H:%M:%S")
    to_datetime = datetime.datetime.strptime(request.json.get('to'), "%Y-%m-%dT%H:%M:%S")
    publishing_manager = PublishingManager.create_manager()
    publishing_manager.publish_firehose_data(
        from_datetime=from_datetime,
        to_datetime=to_datetime,
        curated_bucket_name=app.config['curated_datasets_bucket_name'],
        publishing_bucket_name=app.config['published_datasets_bucket_name'],
        data_prefix='data'
    )
    return 'OK'


@app.route('/af-structure/sync', methods=['POST'])
@raise_backend_exception('Cannot send AF-strucutre sync request')
@login_required
def request_af_structure_sync():
    feed_manager = _create_managed_feeds_manager(app.config)
    s3_bucket = app.config['curated_datasets_bucket_name']
    database = app.config['af_structure_database']
    feed_manager.send_sync_af_request(s3_bucket, database)
    return "OK"


@app.route('/pi-point/subscribe', methods=['POST'])
@raise_backend_exception('Cannot subscribe to PI Point')
@login_required
def subscribe_to_pi_point():
    points = request.get_json()
    feed_manager = _create_managed_feeds_manager(app.config)
    feed_manager.send_subscribe_request(points)
    return "OK"


@app.route('/pi-point/unsubscribe', methods=['POST'])
@raise_backend_exception('Cannot unubscribe PI Point')
@login_required
def unsubscribe_from_pi_point():
    points = request.get_json()
    feed_manager = _create_managed_feeds_manager(app.config)
    feed_manager.send_unsubscribe_request(points)
    return "OK"


@app.route('/pi-point/subscribe/all', methods=['POST'])
@raise_backend_exception('Cannot subscribe to PI Point')
@login_required
def subscribe_to_all_pi_point():
    feed_manager = _create_managed_feeds_manager(app.config)
    points = _get_all_pi_points(feed_manager)
    feed_manager.send_subscribe_request(points)
    return "OK"


@app.route('/pi-point/unsubscribe/all', methods=['POST'])
@raise_backend_exception('Cannot unubscribe PI Point')
@login_required
def unsubscribe_from_all_pi_point():
    feed_manager = _create_managed_feeds_manager(app.config)
    points = _get_all_pi_points(feed_manager)
    feed_manager.send_unsubscribe_request(points)
    return "OK"


@app.route('/pi-point/get-subscribed', methods=['GET'])
@raise_backend_exception('Cannot get subscribed PI Points')
@login_required
def get_subscribed_pi_points_names():
    feed_manager = _create_managed_feeds_manager(app.config)
    feeds = feed_manager.get_managed_feeds()

    pi_points = [feed['pi_point'] for feed in feeds]
    return jsonify(sorted(pi_points))


@app.route('/pi-point/list', methods=['GET'])
@raise_backend_exception('Cannot get PI Points list')
@login_required
def list_pi_points():
    feed_manager = _create_managed_feeds_manager(app.config)
    pi_points = feed_manager.get_pi_points()
    return jsonify(pi_points)


@app.route('/pi-point/sync', methods=['POST'])
@raise_backend_exception('Cannot send PiPoints sync request')
@login_required
def sync_pi_points():
    feed_manager = _create_managed_feeds_manager(app.config)
    feed_manager.send_sync_pi_points_request(s3_bucket=app.config['curated_datasets_bucket_name'])
    return "OK"


@app.route('/af-structure/search', methods=['POST'])
@raise_backend_exception('Cannot search AF-structure')
@login_required
def search_af_structure():
    search_json = request.get_json()

    assets_query = search_json['assetsQuery'].replace('*', '.*')
    asset_field = search_json['assetsField'] if search_json['assetsField'] != "" else "name"
    attributes_query = search_json['attributesQuery'].replace('*', '.*') if search_json['attributesQuery'] != "" else ".*"
    attributes_field = search_json['attributesField'] if search_json['attributesField'] != "" else "name"

    if asset_field == 'path':
        assets_query = ".*" + assets_query

    browser = AfStructureBrowser(
        assets_query=assets_query,
        assets_field=asset_field,
        attributes_query=attributes_query,
        attributes_field=attributes_field
    )
    feed_manager = _create_managed_feeds_manager(app.config)
    structure = feed_manager.get_latest_af_structure(database=app.config['af_structure_database'])
    result = browser.search_assets([structure])
    return jsonify(result)


@app.route('/events/get-recent', methods=['POST'])
@raise_backend_exception('Cannot get recent events')
@login_required
def get_recent_events():
    limit = int(request.json['limit'])
    feed_manager = _create_managed_feeds_manager(app.config)
    events = feed_manager.get_recent_events(limit)

    return jsonify(events)


def _format_cron_expression(cron_expr):
    return 'cron({})'.format(cron_expr)


@app.route('/athena-info')
@raise_backend_exception('Cannot get athena table name')
@login_required
def get_athena_info():
    athena_database = app.config['athena_database_name']
    athena_table_name = app.config['athena_table_name']
    athena_url = "https://{}.console.aws.amazon.com/athena/home?region={}".format(app.config['region'], app.config['region'])
    return jsonify({
        'athena_url': athena_url,
        'athena_database': athena_database,
        'athena_table_name': athena_table_name
    })


def _get_all_pi_points(feed_manager):
    pi_points = feed_manager.get_pi_points()
    return [pi_point['pi_point'] for pi_point in pi_points]


def _create_managed_feeds_manager(config):
    return ManagedFeedsManager.create_manager(
        aws_region=config['region'],
        pi_points_table_name=config['pi_points_table_name'],
        events_status_table_name=config['events_status_table_name'],
        incoming_queue_name=config['incoming_queue_name']
    )


def _read_config(config_path):
    parser = ConfigParser()
    parser.read(config_path)
    config = {}
    for section in parser.sections():
        for (config_key, config_value) in parser.items(section):
            config[config_key] = config_value
    return config


def _parse_command_line_args():
    parser = argparse.ArgumentParser(description='Webapp Management Console')
    parser.add_argument('--config', required=True, help='Configuration')
    return parser.parse_args()


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.INFO)
    app.secret_key = os.urandom(47)
    args = _parse_command_line_args()
    config = _read_config(args.config)
    app.config.update(config)
    app.run(host='0.0.0.0', port=int(config['port']), threaded=True)
