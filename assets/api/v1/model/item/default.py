from api.v1.model.item.common import default_asset, default_attribute, default_event, default_feed

feed = default_feed.inherit('Feed', {})


asset = default_asset.inherit('Asset', {})


attribute = default_attribute.inherit('Attribute', {})


event = default_event.inherit('Event', {})
