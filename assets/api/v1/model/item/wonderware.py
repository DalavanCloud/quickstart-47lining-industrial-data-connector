from flask_restplus import fields, Model

from api.v1.model.item.common import default_attribute, default_asset, default_feed, default_event

subscription_status = Model('SubscriptionStatus', {
        'default': fields.String(
            required=True,
            description='Default subscription status'
        )
})

feed = default_feed.inherit('Feed', {
    'subscription_status': fields.Nested(subscription_status)
})

asset = default_asset.inherit('Asset', {
    'description': fields.String(
        required=True,
        description='OSISoft asset description'
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
    'uom': fields.String(
        required=True,
        description='Unit of measurement'
    ),
    'subscription_status': fields.Nested(subscription_status)
})

event = default_event.inherit('Event', {
    "data_source": fields.String(
        required=False,
        enum=['default', 'all'],
        description='Data source of event'
    )
})
