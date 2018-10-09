from flask_restplus import fields, Model

from api.v1.model.item.common import feed_group

list_events_request = Model('ListEventsRequest', {
    'from': fields.DateTime(
        required=False,
        dt_format='iso8601',
        description='No events will be listed that happened before this timestamp'
    ),
    'to': fields.DateTime(
        required=False,
        dt_format='iso8601',
        description='No events will be listed that happened after this timestamp'
    ),
    'status': fields.String(
        required=False,
        enum=['all', 'success', 'failure', 'pending'],
        description='Status of events to be listed'
    ),
    'type': fields.String(
        required=False,
        enum=['all', 'sync_feeds', 'sync_as', 'interpolate', 'backfill', 'subscribe', 'unsubscribe'],
        description='Type of event to be listed'
    ),
    'page': fields.Integer(
        required=False,
        default=0,
        description='Page number in view'
    ),
    'page_size': fields.Integer(
        required=False,
        default=5,
        description='Number of items that can be displayed on single view page'
    ),
    'username': fields.String(
        required=False,
        description='Name of a user who created this event'
    )
})


def gen_list_events_response(event):
    _list_events_response = Model('ListEventsResponse', {
        'total_count': fields.Integer(
            required=True,
            description='Total count of events'
        ),
        'events': fields.List(
            fields.Nested(
                event,
                required=True
            ),
            required=True,
            description='List of events'
        )
    })
    return _list_events_response


get_event_feed_groups_request = Model('GetEventFeedGroupsRequest', {
    'page': fields.Integer(
        required=False,
        default=0,
        description='Page number in view'
    ),
    'page_size': fields.Integer(
        required=False,
        default=5,
        description='Number of items that can be displayed on single view page'
    )
})


get_event_feed_groups_response = Model('GetEventFeedGroupsResponse', {
    'total_count': fields.Integer(
        required=True,
        description='Total count of events'
    ),
    'feed_groups': fields.List(
        fields.Nested(
            feed_group,
            required=True
        ),
        required=True,
        description='List of events'
    ),
})
