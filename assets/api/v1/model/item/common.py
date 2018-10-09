from flask_restplus import fields, Model

default_feed = Model('DefaultFeed', {
    'name': fields.String(
        required=True,
        description='Name of the feed'
    ),
    'update_timestamp': fields.DateTime(
        required=True,
        dt_format='iso8601',
        description='Timestamp of feed update'
    )
})


default_asset = Model('DefaultAsset', {
    'id': fields.String(
        required=True,
        description='Asset ID'
    ),
    'name': fields.String(
        required=True,
        description='Asset name'
    ),
    'parent_id': fields.String(
        required=True,
        description='Asset\'s parent ID'
    ),
    'is_leaf': fields.Boolean(
        required=True,
        description='Indicates if asset does not have any children'
    )
})


default_attribute = Model('DefaultAttribute', {
    'id': fields.String(
        required=True,
        description='Attribute ID'
    ),
    'asset_id': fields.String(
        required=True,
        description='Asset ID'
    ),
    'name': fields.String(
        required=True,
        description='Attribute name'
    ),
    'feed': fields.String(
        required=True,
        description='Attribute\'s feed name'
    )
})


feed_group = Model('FeedGroup', {
    "id": fields.Integer(
        required=True,
        description='Feed group ID'
    ),
    "event_id": fields.String(
        required=True,
        description='Event ID'
    ),
    "feeds": fields.List(
        fields.String(
            required=True
        ),
        required=False,
        description='Feeds names'
    ),
    "status": fields.String(
        required=True,
        description='Feed group status',
        attribute=lambda x: x['status'].value if x.get('status') is not None else None
    ),
    "error_message": fields.String(
        required=False,
        description='Optional event error message'
    )
})


default_event = Model('DefaultEvent', {
    "type": fields.String(
        required=True,
        enum=['sync_feeds', 'sync_as', 'interpolate', 'backfill', 'subscribe', 'unsubscribe'],
        description='Event type'
    ),
    "name": fields.String(
        required=False,
        description='Event name'
    ),
    "id": fields.String(
        required=True,
        description='Event ID'
    ),
    "error_message": fields.String(
        required=False,
        description='Optional event error message'
    ),
    "username": fields.String(
        required=False,
        description='Name of user who created this event'
    ),
    "s3_bucket": fields.String(
        required=False,
        description='S3 bucket path of file for sync events'
    ),
    "s3_key": fields.String(
        required=False,
        description='S3 key of file for sync event'
    ),
    "start_timestamp": fields.DateTime(
        required=True,
        dt_format='iso8601',
        description='Timestamp of event start'
    ),
    "status": fields.String(
        required=False,
        description='Event status',
        attribute=lambda x: x['status'].value if x.get('status') is not None else None
    ),
    "update_timestamp": fields.DateTime(
        required=True,
        dt_format='iso8601',
        description='Timestamp of event update'
    ),
    "number_of_feeds": fields.Integer(
        required=False,
        description='Number of feeds assosciated with event'
    )
})
