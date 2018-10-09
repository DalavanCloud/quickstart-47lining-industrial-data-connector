from api.v1.model.common import search_filter
from flask_restplus import fields, Model


def gen_search_feeds_request(feed):
    _search_feeds_request = Model('SearchFeedsRequest', {
        'page': fields.Integer(
            required=False,
            default=0,
            description='Page number in view'
        ),
        'page_size': fields.Integer(
            required=False,
            default=5,
            description='Number of items that can be displayed on single page'
        ),
        'query': fields.String(
            required=False,
            description='Search query'
        ),
        'feeds': fields.List(
            fields.Nested(
                feed,
                required=True
            ),
            required=False,
            description='If specified, search only among these feeds'
        ),
        'status': fields.String(
            required=False,
            enum=['all', 'subscribed', 'unsubscribed', 'pending'],
            description='Status of feeds to search'
        ),
        'use_regex': fields.Boolean(
            default=False,
            required=False,
            description='Indicates if search query should be treated as regular expression'
        )
    })
    return _search_feeds_request


def gen_search_feeds_response(feed):
    _search_feeds_response = Model('SearchFeedsResponse', {
        'feeds': fields.List(
            fields.Nested(
                feed,
                required=True,
                readonly=True
            ),
            required=True,
            description='Feeds matching search criteria'
        ),
        'total_count': fields.Integer(
            required=True,
            description='Total number of feeds'
        ),
        'subscribed_count': fields.Integer(
            required=True,
            description='Number of subscribed feeds'
        ),
        'unsubscribed_count': fields.Integer(
            required=True,
            description='Number of unsubscribed feeds'
        ),
        'pending_count': fields.Integer(
            required=True,
            description='Number of pending feeds'
        )
    })
    return _search_feeds_response


backfill_request = Model('BackfillRequest', {
    'feeds': fields.List(
        fields.String(
            required=True
        ),
        required=False,
        description='Feed names'
    ),
    'syntax': fields.Boolean(
        default=False,
        required=False,
        description='Use query syntax'
    ),
    'from': fields.DateTime(
        required=False,
        dt_format='iso8601',
        description='Start timestamp of interpolation'
    ),
    'to': fields.DateTime(
        required=False,
        dt_format='iso8601',
        description='End timestamp of interpolation'
    ),
    'name': fields.String(
        required=False,
        description='Name of action'
    ),
    'query': fields.String(
        required=False,
        description='Optional query'
    ),
    'only_searched_feeds': fields.Boolean(
        default=False,
        required=False,
        description='Request backfill for searched feeds only'
    ),
    'filters': fields.List(
        fields.Nested(
            search_filter,
            required=True
        ),
        required=False,
        description='Filter criteria for searched feeds'
    ),
    'search_pattern': fields.String(
        required=False,
        description='Search pattern for searched feeds'
    ),
    'search_status': fields.String(
        required=False,
        enum=['all', 'subscribed', 'unsubscribed', 'pending'],
        description='Status of searched feeds'
    ),
    'use_regex': fields.Boolean(
        default=False,
        required=False,
        description='Allow regex in search pattern'
    )
})

interpolate_request = Model('InterpolateRequest', {
    'feeds': fields.List(
        fields.String(
            required=True
        ),
        required=False,
        description='Feed names'
    ),
    'syntax': fields.Boolean(
        default=False,
        required=False,
        description='Use query syntax'
    ),
    'from': fields.DateTime(
        required=False,
        dt_format='iso8601',
        description='Start timestamp of interpolation'
    ),
    'to': fields.DateTime(
        required=False,
        dt_format='iso8601',
        description='End timestamp of interpolation'
    ),
    'name': fields.String(
        required=False,
        description='Name of action'
    ),
    'query': fields.String(
        required=False,
        description='Optional query'
    ),
    'interval_unit': fields.String(
        required=True,
        enum=['seconds', 'minutes', 'hours']
    ),
    'interval': fields.Integer(
        required=True,
        description='Interpolation interval'
    ),
    'only_searched_feeds': fields.Boolean(
        default=False,
        required=False,
        description='Interpolate searched feeds only'
    ),
    'filters': fields.List(
        fields.Nested(
            search_filter,
            required=True
        ),
        required=False,
        description='Filter criteria for searched feeds'
    ),
    'search_pattern': fields.String(
        required=False,
        description='Search pattern for searched feeds'
    ),
    'search_status': fields.String(
        required=False,
        enum=['all', 'subscribed', 'unsubscribed', 'pending'],
        description='Status of searched feeds'
    ),
    'use_regex': fields.Boolean(
        default=False,
        required=False,
        description='Allow regex in search pattern'
    )
})

subscribe_request = Model('SubscribeRequest', {
    'feeds': fields.List(
        fields.String(
            required=True
        ),
        required=False,
        description='Feed names'
    ),
    'name': fields.String(
        required=False,
        description='Name of action'
    ),
    'data_source': fields.String(
        required=False,
        enum=['snapshot', 'archive', 'all'],
        description='Data source'
    ),
    'only_searched_feeds': fields.Boolean(
        default=False,
        required=False,
        description='Subscribe searched feeds only'
    ),
    'filters': fields.List(
        fields.Nested(
            search_filter,
            required=True
        ),
        required=False,
        description='Filter criteria for searched feeds'
    ),
    'search_pattern': fields.String(
        required=False,
        description='Search pattern for searched feeds'
    ),
    'search_status': fields.String(
        required=False,
        enum=['all', 'subscribed', 'unsubscribed', 'pending'],
        description='Status of searched feeds'
    ),
    'use_regex': fields.Boolean(
        default=False,
        required=False,
        description='Allow regex in search pattern'
    )
})

unsubscribe_request = Model('UnsubscribeRequest', {
    'feeds': fields.List(
        fields.String(
            required=True
        ),
        required=False,
        description='Feed names'
    ),
    'name': fields.String(
        required=False,
        description='Name of action'
    ),
    'data_source': fields.String(
        required=False,
        enum=['snapshot', 'archive', 'all'],
        description='Data source'
    ),
    'only_searched_feeds': fields.Boolean(
        default=False,
        required=False,
        description='Unsubscribe searched feeds only'
    ),
    'filters': fields.List(
        fields.Nested(
            search_filter,
            required=True
        ),
        required=False,
        description='Filter criteria for searched feeds'
    ),
    'search_pattern': fields.String(
        required=False,
        description='Search pattern for searched feeds'
    ),
    'search_status': fields.String(
        required=False,
        enum=['all', 'subscribed', 'unsubscribed', 'pending'],
        description='Status of searched feeds'
    ),
    'use_regex': fields.Boolean(
        default=False,
        required=False,
        description='Allow regex in search pattern'
    )
})

reset_data_request = Model('ResetDataRequest', {
    'name': fields.String(
        required=True,
        description='Event name'
    )
})
