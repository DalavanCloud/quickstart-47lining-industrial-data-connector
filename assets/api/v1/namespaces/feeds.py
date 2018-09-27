import datetime
import logging
import time
from threading import Thread

from flask import current_app, request
from flask_restplus import Namespace
from injector import inject

from api.api_utils import raise_backend_exception
from api.v1.ApiResource import ApiResource
from api.v1.authentication.utils import login_required
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager

logger = logging.getLogger(__name__)

CHECKING_STATUS_DELAY = 5
PURGING_QUEUES_DELAY = 60


def create_feeds_namespace(api, **kwargs):
    feeds_ns = Namespace('feeds', description='Operations related to feeds - synchronization, searching, subscription,'
                                              ' backfill and interpolation')

    @feeds_ns.route('/search', methods=['POST'])
    class SearchFeeds(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot get feeds')
        @api.expect(kwargs['search_feeds_request'])
        @api.marshal_with(kwargs['search_feeds_response'], code=200,
                          description='List of feeds matching criteria is returned')
        @login_required
        def post(self):
            """
            Fetch list of feeds matching criteria
            """
            data = request.get_json()
            page = int(data['page']) if 'page' in data else None
            page_size = int(data['page_size']) if 'page_size' in data else None
            feeds = self._feed_manager.search_feeds(
                pattern=data.get('query'),
                feeds=data.get('feeds'),
                status=data.get('status'),
                use_regex=data.get('use_regex'),
                page=page,
                page_size=page_size
            )
            return feeds

    @feeds_ns.route('/sync', methods=['POST'])
    class SyncFeeds(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot send feeds sync request')
        @api.response(200, 'Feeds synchronization request is sent')
        @login_required
        def post(self):
            """
            Send synchronization request for feeds
            """
            self._feed_manager.send_sync_feeds_request(
                s3_bucket=current_app.config['CURATED_DATASETS_BUCKET_NAME'])
            return 'OK', 200

    @feeds_ns.route('/backfill', methods=['POST'])
    class Backfill(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot send backfill request')
        @api.response(200, 'Backfill request is sent')
        @api.expect(kwargs['backfill_request'])
        @login_required
        def post(self):
            """
            Send backfill request for feeds matching search criteria or specified feeds
            """
            if request.json.get('only_searched_feeds', False):
                feeds = _search_feeds(self._feed_manager, request.get_json())
            else:
                feeds = request.json['feeds']

            query_syntax = request.json.get('syntax', False)

            self._feed_manager.send_backfill_request(
                query_syntax=query_syntax,
                query=request.json.get('query'),
                feeds=feeds,
                request_to=request.json.get('to'),
                request_from=request.json.get('from'),
                name=_get_event_name(request, 'backfill')
            )
            return 'OK', 200

    @feeds_ns.route('/interpolate', methods=['POST'])
    class Interpolate(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot send interpolate request')
        @api.response(200, 'Interpolate request is sent')
        @api.expect(kwargs['interpolate_request'])
        @login_required
        def post(self):
            """
            Send interpolation request for feeds matching search criteria or specified feeds
            """
            query_syntax = request.json.get('syntax', False)

            if request.json.get('only_searched_feeds', False):
                feeds = _search_feeds(self._feed_manager, request.get_json())
            else:
                feeds = request.json['feeds']

            self._feed_manager.send_interpolate_request(
                query_syntax=query_syntax,
                feeds=feeds,
                interval=request.json['interval'],
                interval_unit=request.json['interval_unit'],
                query=request.json.get('query'),
                request_from=request.json.get('from'),
                request_to=request.json.get('to'),
                name=_get_event_name(request, 'interpolate')
            )
            return 'OK', 200

    @feeds_ns.route('/subscribe', methods=['POST'])
    class Subscribe(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot send subscribe request')
        @api.response(200, 'Subscribe request is sent')
        @api.expect(kwargs['subscribe_request'])
        @login_required
        def post(self):
            """
            Send subscribe request for feeds matching search criteria or specified feeds
            """
            if request.json.get('only_searched_feeds', False):
                points = _search_feeds(self._feed_manager, request.get_json())
            else:
                points = request.json['feeds']

            self._feed_manager.send_subscribe_request(
                feeds=points,
                name=_get_event_name(request, 'subscribe'),
                data_source=request.json.get('data_source', 'all')
            )
            return 'OK', 200

    @feeds_ns.route('/unsubscribe', methods=['POST'])
    class Unsubscribe(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot send unsubscribe request')
        @api.response(200, 'Unsubscribe request is sent')
        @api.expect(kwargs['unsubscribe_request'])
        @login_required
        def post(self):
            """
            Send unsubscribe request for feeds matching search criteria or specified feeds
            """
            if request.json.get('only_searched_feeds', False):
                feeds = _search_feeds(self._feed_manager, request.get_json())
            else:
                feeds = request.json['feeds']

            self._feed_manager.send_unsubscribe_request(
                feeds=feeds,
                name=_get_event_name(request, 'unsubscribe'),
                data_source=request.json.get('data_source', 'all')
            )
            return 'OK', 200

    @feeds_ns.route('/reset', methods=['POST'])
    class ResetData(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot send reset data request')
        @api.response(200, 'Reset data request is sent')
        @api.expect(kwargs['reset_data_request'])
        @login_required
        def post(self):
            """
            Send reset data request for all feeds
            """
            logger.debug("Got reset data request")
            feeds = _search_feeds(self._feed_manager, request.get_json())
            event_name = _get_event_name(request, 'unsubscribe')
            thread = Thread(target=self.reset_all, args=(feeds, event_name, request.headers['username']))
            thread.start()

            return 'OK', 200

        def reset_all(self, feeds, event_name, username):
            self._feed_manager.create_reset_event('pending', username)

            # purge queues
            logger.info("Purging queues...")
            self._feed_manager.purge_queues()
            logger.info("All queues purged")

            # unsubscribe all feeds
            logger.info("Unsubscribing all the feeds")
            self._feed_manager.send_unsubscribe_request(
                feeds=feeds,
                name=event_name,
                data_source='all',
                username=username
            )
            self._wait_for_unsubscribed()
            logger.info("All feeds unsubscribed")

            # reset database
            logger.info("Resetting database")
            self._feed_manager.reset_database()

            self._feed_manager.create_reset_event('success', username)
            logger.info("Reset done")

        def _wait_for_unsubscribed(self):
            all_unsubscribed = False
            while not all_unsubscribed:
                logger.debug("Waiting...")
                points = self._feed_manager.search_feeds(status='subscribed')
                # Check if nothing found
                all_unsubscribed = points['feeds'] == []
                if not all_unsubscribed:
                    time.sleep(CHECKING_STATUS_DELAY)

    return feeds_ns


def _search_feeds(feed_manager, request_data):
    feeds = feed_manager.search_feeds(
        filters=request_data.get('filters'),
        pattern=request_data.get('search_pattern'),
        feeds=None,
        status=request_data.get('search_status'),
        use_regex=request_data.get('use_regex')
    )['feeds']
    return [feed['name'] for feed in feeds]


def _get_default_event_name(event_type):
    return '{} {}'.format(
        event_type,
        datetime.datetime.utcnow().strftime('%m/%d/%Y %I:%M %p')
    )


def _get_event_name(request, event_type):
    name = request.json.get('name')
    if name is not None and name != '':
        return name

    return _get_default_event_name(event_type)
