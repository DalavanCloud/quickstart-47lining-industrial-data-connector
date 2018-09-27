from model.wonderware.models import (
    SyncAsEvent,
    Feed,
    Event,
    SyncFeedsEvent,
    BackfillEvent,
    InterpolateEvent,
    SubscribeEvent,
    UnsubscribeEvent,
    ResetEvent,
    Asset,
    Attribute,
    Settings,
    FeedGroup,
    DATA_SOURCES
)
from workers.managed_feeds.dao.managed_feeds_postgres_dao import ManagedFeedsPostgresDao


class ManagedFeedsPostgresDaoWonderware(ManagedFeedsPostgresDao):
    def _get_settings_model(self):
        return Settings

    def _get_attribute_model(self):
        return Attribute

    def _get_sync_as_event_model(self):
        return SyncAsEvent

    def _get_sync_feeds_event_model(self):
        return SyncFeedsEvent

    def _get_asset_model(self):
        return Asset

    def _get_subscribe_event_model(self):
        return SubscribeEvent

    def _get_unsubscribe_event_model(self):
        return UnsubscribeEvent

    def _get_backfill_event_model(self):
        return BackfillEvent

    def _get_interpolate_event_model(self):
        return InterpolateEvent

    def _get_reset_event_model(self):
        return ResetEvent

    def _get_feed_group_model(self):
        return FeedGroup

    def _get_feed_model(self):
        return Feed

    def _get_event_model(self):
        return Event

    def _get_data_sources(self):
        return DATA_SOURCES

    def _get_query_filters(self):
        query_filters = {
            'asset': {
                'name': lambda filter_value: Asset.name.like(filter_value),
                'path': lambda filter_value: Asset.id.like(filter_value.replace('\\', '\\\\')),
            },
            'attribute': {
                'name': lambda filter_value: Attribute.name.like(filter_value),
                'feed': lambda filter_value: Attribute.feed.like(filter_value),
                'description': lambda filter_value: Attribute.description.like(filter_value),
                'type': lambda filter_value: Attribute.type.like(filter_value),
                'uom': lambda filter_value: Attribute.uom.like(filter_value),
                'item_name': lambda filter_value: Attribute.item_name.like(filter_value),
            }
        }

        return query_filters

    def create_asset(self, node, parent_id):
        asset = {
            'id': node['path'],
            'name': node['name'],
            'parent_id': parent_id,
            'is_leaf': len(node.get('assets', [])) == 0,

            'description': node.get('description'),
        }
        return asset

    def create_attribute(self, node, attribute):
        feed = attribute['feed']['name'] if attribute['feed'] is not None else None
        attribute = {
            'id': "{}!{}/{}".format(node['path'], attribute.get('item_name', ''), attribute.get('name')),
            'asset_id': node['path'],
            'name': attribute.get('name'),
            'feed': feed,

            'description': attribute.get('description'),
            'type': attribute.get('type'),
            'uom': attribute.get('uom'),
            'item_name': attribute.get('item_name')
        }
        return attribute
