import argparse
import logging
import os
import sys
from configparser import ConfigParser
from functools import wraps

import boto3
from flask import (
    Flask,
    request,
    session,
    jsonify,
    render_template
)
from flask_sqlalchemy import SQLAlchemy
from osisoft_pi2aws_root import PROJECT_DIR
from scheduling_manager.scheduling_manager import SchedulingManager, NoSuchRuleException
from sqlalchemy import create_engine
from webapp_management_console.json_encoder import CustomJSONEncoder
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
            raise BackendException("Not logged in", status_code=400)
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


@app.route('/favicon/<path>')
def favicon(path):
    return app.send_static_file('favicon/{}'.format(path))


def _save_settings(settings):
    feed_manager = _create_managed_feeds_manager(app.config)
    feed_manager.save_settings(settings)
    _load_settings()


@app.route('/settings/save', methods=['POST'])
@raise_backend_exception('Unable to save settings')
@login_required
def save_settings():
    _save_settings(request.json['settings'])
    return 'ok'


@app.route('/settings', methods=['GET'])
@raise_backend_exception('Unable to load settings')
@login_required
def load_settings():
    settings = _get_settings()
    # overwrite afDbName in case it is not present in database
    settings['afDbName'] = app.config['af_structure_database']
    return jsonify(settings)


@app.route('/structure/asset-children', methods=['POST'])
@raise_backend_exception('Unable to load assets')
@login_required
def get_asset_children():
    feed_manager = _create_managed_feeds_manager(app.config)
    data = feed_manager.get_asset_children(request.json['parentAssetId'])
    return jsonify(data)


@app.route('/structure/search', methods=['POST'])
@raise_backend_exception('Unable to search assets')
@login_required
def search_assets():
    feed_manager = _create_managed_feeds_manager(app.config)
    data = feed_manager.search_assets(
        filters=request.json['filters'],
        page=request.json.get('page', 0),
        page_size=request.json.get('pageSize', 5)
    )
    return jsonify(data)


@app.route('/structure/asset-attributes', methods=['POST'])
@raise_backend_exception('Unable to search assets')
@login_required
def asset_attributes():
    feed_manager = _create_managed_feeds_manager(app.config)
    data = feed_manager.search_asset_attributes(
        request.json['assetId'], request.json['filters'])
    return jsonify(data)


def _search_feeds(feed_manager, request_data):
    feeds = feed_manager.search_pi_points(
        filters=request_data.get('filters'),
        pattern=request_data.get('searchPattern'),
        pi_points=None,
        status=request_data.get('searchForStatus')
    )['pi_points']
    return [feed['pi_point'] for feed in feeds]


@app.route('/backfill', methods=['POST'])
@raise_backend_exception('Cannot send backfill request')
@login_required
def backfill():
    feed_manager = _create_managed_feeds_manager(app.config)
    if request.json.get('onlySearchedFeeds', False):
        points = _search_feeds(feed_manager, request.get_json())
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

    if request.json.get('onlySearchedFeeds', False):
        points = _search_feeds(feed_manager, request.get_json())
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


@app.route('/subscribe', methods=['POST'])
@raise_backend_exception('Cannot send subscribe request')
@login_required
def subscribe():
    feed_manager = _create_managed_feeds_manager(app.config)
    if request.json.get('onlySearchedFeeds', False):
        points = _search_feeds(feed_manager, request.get_json())
    else:
        points = request.json['feeds']

    feed_manager.send_subscribe_request(points)

    return 'OK'


@app.route('/subscribe/<limit>', methods=['GET'])
@raise_backend_exception('Cannot send subscribe request')
@login_required
def subscribe_with_limit(limit):
    feed_manager = _create_managed_feeds_manager(app.config)
    points = feed_manager.managed_feeds_dao.get_pi_points(limit)
    points = [point['pi_point'] for point in points]

    feed_manager.send_subscribe_request(points)

    return jsonify(points)


@app.route('/unsubscribe', methods=['POST'])
@raise_backend_exception('Cannot send unsubscribe request')
@login_required
def unsubscribe():
    feed_manager = _create_managed_feeds_manager(app.config)
    if request.json.get('onlySearchedFeeds', False):
        points = _search_feeds(feed_manager, request.get_json())
    else:
        points = request.json['feeds']

    feed_manager = _create_managed_feeds_manager(app.config)
    feed_manager.send_unsubscribe_request(points)

    return 'OK'


@app.route('/structure/sync', methods=['POST'])
@raise_backend_exception('Cannot send structure sync request')
@login_required
def request_af_structure_sync():
    feed_manager = _create_managed_feeds_manager(app.config)
    s3_bucket = app.config['curated_datasets_bucket_name']
    database = app.config['af_structure_database']
    feed_manager.send_sync_af_request(s3_bucket, database)
    return "OK"


@app.route('/feeds/search', methods=['POST'])
@raise_backend_exception('Cannot search PI Points list')
@login_required
def search_feeds():
    feed_manager = _create_managed_feeds_manager(app.config)
    data = request.get_json()
    page = int(data['page']) if 'page' in data else None
    page_size = int(data['page_size']) if 'page_size' in data else None
    feeds = feed_manager.search_pi_points(
        pattern=data.get('query'),
        pi_points=data.get('pi_points'),
        status=data.get('status'),
        use_regex=data.get('useRegex'),
        page=page,
        page_size=page_size
    )
    return jsonify(feeds)


@app.route('/feeds/sync', methods=['POST'])
@raise_backend_exception('Cannot send PiPoints sync request')
@login_required
def sync_feeds():
    feed_manager = _create_managed_feeds_manager(app.config)
    feed_manager.send_sync_pi_points_request(
        s3_bucket=app.config['curated_datasets_bucket_name'])
    return "OK"


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
    athena_numeric_table_name = app.config['athena_numeric_table_name']
    athena_text_table_name = app.config['athena_text_table_name']
    athena_url = "https://{}.console.aws.amazon.com/athena/home?region={}".format(
        app.config['region'],
        app.config['region']
    )
    return jsonify({
        'athena_url': athena_url,
        'athena_database': athena_database,
        'athena_numeric_table_name': athena_numeric_table_name,
        'athena_text_table_name': athena_text_table_name
    })


@app.route('/scheduler/structure', methods=['POST'])
@raise_backend_exception('Cannot schedule structure sync')
@login_required
def schedule_structure_sync():
    scheduling_manager = _create_scheduling_manager()

    arguments = {
        'cron_expr': _format_cron_expression(request.json['cron']),
        'af_struct_manager_payload': {
            's3_bucket': app.config['curated_datasets_bucket_name'],
            'database': app.config['af_structure_database']
        },
        'rule_name': app.config['SYNC_AF_STRUCTURE_EVENT_NAME']
    }
    scheduling_manager.create_af_sync_schedule(**arguments)

    return 'ok'


@app.route('/scheduler/feeds', methods=['POST'])
@raise_backend_exception('Cannot schedule Feeds List sync')
@login_required
def schedule_feeds_sync():
    scheduling_manager = _create_scheduling_manager()

    arguments = {
        'cron_expr': _format_cron_expression(request.json['cron']),
        'pi_points_manager_payload': {
            's3_bucket': app.config['curated_datasets_bucket_name']
        },
        'rule_name': app.config['SYNC_PI_POINTS_EVENT_NAME']
    }
    scheduling_manager.create_pi_points_sync_schedule(**arguments)

    return 'ok'


@app.route('/scheduler/rules', methods=['GET'])
@login_required
def get_scheduler_rule():
    return jsonify({
        'structure': scheduler_rule(app.config['SYNC_AF_STRUCTURE_EVENT_NAME']),
        'feeds': scheduler_rule(app.config['SYNC_PI_POINTS_EVENT_NAME'])
    })


def scheduler_rule(rule_name):
    scheduling_manager = _create_scheduling_manager()

    try:
        rule = scheduling_manager.get_rule_parameters_by_rule_name(
            rule_name, fetch_feed=False)
    except NoSuchRuleException:
        return {
            'ruleName': rule_name,
            'cron': 'unknown'
        }

    rule = {
        'ruleName': rule_name,
        'query': rule.get('query'),
        'dbName': rule.get('database'),
        'cron': rule['schedule_expression'].replace('cron(', '').replace(')', ''),
        'interval': rule.get('interval'),
        'intervalUnit': rule.get('interval_unit')
    }

    return {k: v for k, v in rule.items() if v is not None}


def _create_managed_feeds_manager(config):
    return ManagedFeedsManager.create_manager(
        aws_region=config['region'],
        postgres_session=database.session,
        incoming_queue_name=config['incoming_queue_name']
    )


def _create_scheduling_manager():
    lambda_arns = {
        'AF_SYNC_LAMBDA_ARN': app.config['af_sync_lambda_arn'],
        'PI_POINTS_SYNC_LAMBDA_KEY': app.config['pi_points_sync_lambda_arn']
    }

    boto_session = boto3.session.Session()
    return SchedulingManager(
        boto_session.client('events', region_name=app.config['region']),
        lambda_arns,
        s3_resource=boto_session.resource('s3'),
        s3_rule_bucket=app.config['curated_datasets_bucket_name'],
        s3_rule_bucket_key_prefix=app.config['s3_rule_bucket_key_prefix']
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


def _get_settings():
    feed_manager = _create_managed_feeds_manager(app.config)
    return feed_manager.get_settings()


def _load_settings():
    feed_manager = _create_managed_feeds_manager(app.config)
    settings = feed_manager.get_settings()
    if 'afDbName' in settings.keys():
        app.config['af_structure_database'] = settings['afDbName']


if __name__ == "__main__":
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)
    app.secret_key = os.urandom(47)
    args = _parse_command_line_args()
    config = _read_config(args.config)
    app.config.update(config)
    app.config['SQLALCHEMY_DATABASE_URI'] = config['postgres_uri']
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SYNC_PI_POINTS_EVENT_NAME'] = "{}-sync-pi-points-{}".format(
        config['region'],
        config['account_id']
    )
    app.config['SYNC_AF_STRUCTURE_EVENT_NAME'] = "{}-sync-af-structure-{}".format(
        config['region'],
        config['account_id']
    )
    engine = create_engine(config['postgres_uri'], use_batch_mode=True)
    database = SQLAlchemy(app, session_options={'bind': engine})
    app.json_encoder = CustomJSONEncoder

    _load_settings()
    app.run(host='0.0.0.0', port=int(
        config['port']), threaded=True)
