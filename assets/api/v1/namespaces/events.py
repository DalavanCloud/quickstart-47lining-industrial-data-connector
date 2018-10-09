from flask import request
from flask_restplus import Namespace
from injector import inject

from api.api_utils import raise_backend_exception
from api.v1.ApiResource import ApiResource
from api.v1.authentication.utils import login_required
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager


def create_events_namespace(api, **kwargs):
    events_ns = Namespace('events', description='Fetch historical and current events that were triggered by API')

    @events_ns.route('/list', methods=['POST'])
    class ListEvents(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot fetch events')
        @api.expect(kwargs['list_events_request'])
        @api.marshal_with(kwargs['list_events_response'], code=200, description='System events are returned')
        @login_required
        def post(self):
            """
            Fetch historical and current events that were triggered by API
            """
            data = request.get_json()
            page = int(data['page']) if 'page' in data else None
            page_size = int(data['page_size']) if 'page_size' in data else None
            result = self._feed_manager.get_events(
                type=data.get('type'),
                status=data.get('status'),
                timestamp_from=data.get('from'),
                timestamp_to=data.get('to'),
                page=page,
                page_size=page_size
            )
            return result

    @events_ns.route('/<string:event_id>', methods=['POST'])
    class GetEventFeedGroups(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot fetch events')
        @api.expect(kwargs['get_event_feed_groups_request'])
        @api.marshal_with(kwargs['get_event_feed_groups_response'], code=200, description='System events are returned')
        @login_required
        def post(self, event_id):
            """
            Fetch feed groups associated with an event
            """
            data = request.get_json()
            page = int(data['page']) if 'page' in data else None
            page_size = int(data['page_size']) if 'page_size' in data else None
            result = self._feed_manager.get_event_feed_groups(
                event_id=event_id,
                page=page,
                page_size=page_size
            )
            return result

    return events_ns
