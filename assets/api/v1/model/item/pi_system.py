from flask_restplus import fields, Model

from api.v1.model.item.common import default_event, default_attribute, default_feed, default_asset

subscription_status = Model('SubscriptionStatus', {
        'archive': fields.String(
            required=True,
            description='Archive subscription status'
        ),
        'snapshot': fields.String(
            required=True,
            description='Snapshot subscription status'
        )
})


feed = default_feed.inherit('Feed', {
    'subscription_status': fields.Nested(subscription_status)
})


asset = default_asset.inherit('Asset', {
    'description': fields.String(
        required=True,
        description='OSISoft asset description'
    ),
    'template': fields.String(
        required=True,
        description='OSISoft asset\'s template name'
    ),
    'categories': fields.List(
        fields.String(
            required=True
        ),
        required=True,
        description='List of OSISoft asset\'s categories'
    )
})


attribute = default_attribute.inherit('Attribute', {
    'description': fields.String(
        required=True,
        description='Attribute description'
    ),
    'type': fields.String(
        required=True,
        description='OSISoft attribute type'
    ),
    'categories': fields.List(
        fields.String(
            required=True
        ),
        required=True,
        description='List of OSISoft attribute categories'
    ),
    'uom': fields.String(
        required=True,
        description='Unit of measure'
    ),
    'subscription_status': fields.Nested(subscription_status)
})


event = default_event.inherit('Event', {
    "data_source": fields.String(
        required=False,
        enum=['archive', 'snapshot', 'all'],
        description='Data source of event'
    )
})
