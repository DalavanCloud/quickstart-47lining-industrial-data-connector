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
        description='Kepware asset description'
    )
})

attribute = default_attribute.inherit('Attribute', {
    'value': fields.String(
        required=True,
        description='Attribute\'s value'
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
