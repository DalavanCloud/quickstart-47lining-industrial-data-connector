from abc import ABCMeta, abstractmethod
from typing import List

from sqlalchemy import or_, and_
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql.expression import cast, func

from model.enums import SubscriptionStatus, EventStatus
from workers.managed_feeds.utils import split_feed_group_message_id


class ManagedFeedsPostgresDao:
    __metaclass__ = ABCMeta

    def __init__(self, session, s3_client, cache_dir='/tmp/as_structure_cache'):
        self.session = session
        self.s3_client = s3_client
        self.cache_dir = cache_dir

        self.data_sources = self._get_data_sources()
        self.query_filters = self._get_query_filters()

        self.Feed = self._get_feed_model()
        self.Event = self._get_event_model()
        self.FeedGroup = self._get_feed_group_model()
        self.Attribute = self._get_attribute_model()
        self.SyncAsEvent = self._get_sync_as_event_model()
        self.SyncFeedsEvent = self._get_sync_feeds_event_model()
        self.Asset = self._get_asset_model()
        self.Settings = self._get_settings_model()

        self.SubscribeEvent = self._get_subscribe_event_model()
        self.UnsubscribeEvent = self._get_unsubscribe_event_model()
        self.BackfillEvent = self._get_backfill_event_model()
        self.InterpolateEvent = self._get_interpolate_event_model()
        self.ResetEvent = self._get_reset_event_model()

    def get_events(self, type=None, status=None, timestamp_from=None, timestamp_to=None,
                   start_timestamp_from=None, start_timestamp_to=None,
                   page=None, page_size=None):
        query = self.session.query(self.Event).order_by(self.Event.update_timestamp.desc())
        if type is not None and type != 'all':
            query = query.filter(self.Event.type == type)
        if status is not None and status != 'all':
            query = query.filter(self.Event.status == status)
        if timestamp_from is not None and timestamp_from != '':
            query = query.filter(self.Event.update_timestamp >= timestamp_from)
        if timestamp_to is not None and timestamp_to != '':
            query = query.filter(self.Event.update_timestamp <= timestamp_to)
        if start_timestamp_from is not None and start_timestamp_from != '':
            query = query.filter(self.Event.start_timestamp >= start_timestamp_from)
        if start_timestamp_to is not None and start_timestamp_to != '':
            query = query.filter(self.Event.start_timestamp <= start_timestamp_to)

        paginated_query = self._paginate_query(query, page=page, page_size=page_size)
        events = paginated_query.all()
        total_count = query.count()

        return {
            'events': [event.as_dict() for event in events],
            'total_count': total_count
        }

    def get_event_feed_groups(self, event_id, page=None, page_size=None):
        query = self.session.query(self.FeedGroup).filter(self.FeedGroup.event_id == event_id).order_by(
            self.FeedGroup.id)
        paginated_query = self._paginate_query(query, page=page, page_size=page_size)
        feed_groups = paginated_query.all()
        total_count = query.count()

        return {
            'feed_groups': [feed_group.as_dict() for feed_group in feed_groups],
            'total_count': total_count
        }

    def get_feed_group_by_id(self, event_id):
        splitted_id = split_feed_group_message_id(event_id)
        feed_group = self.session.query(self.FeedGroup) \
            .get((splitted_id['id'], splitted_id['event_id']))
        if feed_group is not None:
            return feed_group.as_dict()

    @staticmethod
    def _paginate_query(query, page=None, page_size=None):
        if page_size:
            query = query.limit(page_size)
            if page:
                query = query.offset(page * page_size)
        return query

    def list_feeds(self, page=None, page_size=None):
        paginated_query = self.session.query(self.Feed).order_by(self.Feed.name)
        paginated_query = self._paginate_query(paginated_query, page=page, page_size=page_size)
        feeds = paginated_query.all()
        total_count = self.session.query(self.Feed).count()
        return {
            'feeds': [feed.as_dict() for feed in feeds],
            'total_count': total_count
        }

    def _get_not_none_data_source(self, data_source):
        """Returns default data source if data_source is None"""
        data_source = data_source if data_source is not None else self.data_sources[0]
        assert data_source in self.data_sources
        return data_source

    def list_subscribed_feeds(self, data_source=None):
        data_source = self._get_not_none_data_source(data_source)
        query = self.session.query(self.Feed)
        query = query.filter(
            self.Feed.subscription_status[data_source] == cast(SubscriptionStatus.subscribed.value, JSONB)
        )
        return [feed.as_dict()['name'] for feed in query.all()]

    def filter_feeds(self, feeds, status, data_source=None):
        data_source = self._get_not_none_data_source(data_source)
        query = self.session.query(self.Feed)
        query = query.filter(
            self.Feed.subscription_status[data_source] == cast(status, JSONB)
        )
        query = query.filter(self.Feed.name.in_(feeds))

        return [feed.as_dict()['name'] for feed in query.all()]

    def search_feeds(self, filters=None, pattern=None, feeds=None, status=None, use_regex=False, page=None,
                     page_size=None):
        if filters is not None:
            query = self.session.query(self.Attribute.feed)
            query = self._filter_query(query, filters)
            query = query.filter(self.Attribute.asset_id == self.Asset.id) \
                .filter(self.Attribute.feed.isnot(None)) \
                .distinct(self.Attribute.feed).subquery()
            query = self.session.query(self.Feed).filter(self.Feed.name.in_(query))
        else:
            query = self.session.query(self.Feed).order_by(self.Feed.name)
            if pattern is not None and pattern != '':
                if use_regex:
                    query = query.filter(self.Feed.name.op('~')(pattern))
                else:
                    query = query.filter(self.Feed.name.ilike(pattern.replace('*', '%')))
            if feeds is not None:
                query = query.filter(self.Feed.name.in_(feeds))
            if status is not None and status != 'all':
                query = query.filter(
                    or_(
                        self.Feed.subscription_status[source] == cast(status, JSONB)
                        for source in self.data_sources
                    )
                )

        paginated_query = self._paginate_query(query, page=page, page_size=page_size)
        feeds = paginated_query.all()
        total_count = query.count()

        subscribed_count = query.filter(
            or_(
                self.Feed.subscription_status[source] == cast(SubscriptionStatus.subscribed.value, JSONB)
                for source in self.data_sources
            )
        ).count()
        unsubscribed_count = query.filter(
            and_(
                self.Feed.subscription_status[source] == cast(SubscriptionStatus.unsubscribed.value, JSONB)
                for source in self.data_sources
            )
        ).count()
        pending_count = query.filter(
            or_(
                self.Feed.subscription_status[source] == cast(SubscriptionStatus.pending.value, JSONB)
                for source in self.data_sources
            )
        ).count()

        return {
            'feeds': [feed.as_dict() for feed in feeds],
            'total_count': total_count,
            'subscribed_count': subscribed_count,
            'unsubscribed_count': unsubscribed_count,
            'pending_count': pending_count
        }

    def filter_pending_feeds(self, feeds, data_source=None):
        data_source = self._get_not_none_data_source(data_source)
        query = self.session.query(self.Feed)
        query = query.filter(self.Feed.name.in_(feeds))
        query = query.filter(
            self.Feed.subscription_status[data_source] == cast(SubscriptionStatus.pending.value, JSONB)
        )

        feeds = query.all()
        return [feed.as_dict() for feed in feeds]

    def _replace_wildcard(self, query):
        return query.replace('.*', '%').replace('*', '%')

    def _filter_query(self, query, filters):
        for fil in filters:
            assert fil['type'] in ['asset', 'attribute']
            assert fil['parameter'] in self.query_filters[fil['type']].keys()

            if fil['type'] == 'attribute':
                query = query.filter(self.Attribute.asset_id == self.Asset.id)

            filter_value = self._replace_wildcard(fil['value'].strip())

            query_filter = self.query_filters[fil['type']][fil['parameter']](filter_value)

            query = query.filter(query_filter)

        return query

    def search_assets(self, filters, page=None, page_size=None):
        query = self.session.query(self.Asset)
        query = self._filter_query(query, filters)

        feeds_total_count = query.filter(self.Attribute.asset_id == self.Asset.id) \
            .filter(self.Attribute.feed.isnot(None)) \
            .distinct(self.Attribute.feed).count()

        query = query.group_by(self.Asset.id)
        query = query.order_by(self.Asset.id)
        paginated_query = self._paginate_query(query, page=page, page_size=page_size)
        assets = paginated_query.all()
        total_count = query.count()
        return {
            'assets': [asset.as_dict() for asset in assets],
            'total_count': total_count,
            'feeds_total_count': feeds_total_count
        }

    def search_asset_attributes(self, asset_id, filters):
        query = self.session.query(self.Attribute, self.Feed.subscription_status). \
            outerjoin(self.Feed, self.Attribute.feed == self.Feed.name). \
            filter(self.Attribute.asset_id == asset_id)

        query = self._filter_query(query, filters)

        feeds_total_count = query.filter(self.Attribute.feed.isnot(None)).distinct(self.Attribute.feed).count()

        attributes = query.all()
        total_count = query.count()

        return {
            'attributes': [
                {
                    **attribute[0].as_dict(),
                    'subscription_status': attribute[1]
                }
                for attribute in attributes
            ],
            'total_count': total_count,
            'feeds_total_count': feeds_total_count
        }

    def get_asset_children(self, parent_asset_id):
        assets = self.session.query(self.Asset.id, self.Asset.name, self.Asset.is_leaf). \
            filter(self.Asset.parent_id == parent_asset_id).all()

        assets = [{'id': asset[0], 'name': asset[1], 'is_leaf': asset[2]} for asset in assets]
        return assets

    def update_feeds(self, feeds: List[str]):
        all_feeds = set(feed[0] for feed in self.session.query(self.Feed.name).all())
        feeds = set(feeds)
        feeds_to_remove = all_feeds - feeds
        feeds_to_add = feeds - all_feeds

        self.session.query(self.Feed) \
            .filter(self.Feed.name.in_(feeds_to_remove)) \
            .delete(synchronize_session=False)

        self.session.bulk_insert_mappings(
            self.Feed,
            [{'name': feed} for feed in feeds_to_add]
        )
        self.session.commit()

    def _save_as_to_db(self, nodes, root_path):
        if nodes is None:
            return None
        else:
            for node in nodes:
                asset = self.create_asset(node, root_path)
                self.session.add(self.Asset(**asset))
                for attribute in node['attributes'] or []:
                    attribute = self.create_attribute(node, attribute)
                    self.session.add(self.Attribute(**attribute))

                self._save_as_to_db(
                    node.get('assets'), node['path']
                )
        return None

    def update_as_structure(self, as_structure):
        self.session.query(self.Attribute).delete()
        self.session.query(self.Asset).delete()

        self._save_as_to_db([as_structure], None)

        self.session.commit()

    def update_feeds_status(self, feeds, status, data_source=None):
        data_source = self._get_not_none_data_source(data_source)
        self.session.query(self.Feed) \
            .filter(self.Feed.name.in_(feeds)) \
            .update({
                self.Feed.subscription_status: cast(self.Feed.subscription_status, JSONB)
                .concat(func.jsonb_build_object(data_source, status))
            }, synchronize_session="fetch")
        self.session.commit()

    def update_event_status(self, id, error_message=None):
        status = EventStatus.success if error_message is None else EventStatus.failure
        self.session.query(self.Event) \
            .filter(self.Event.id == id) \
            .update({'status': status, 'error_message': error_message}, synchronize_session=False)
        self.session.commit()

    def update_feed_group_status(self, msg_id, error_message=None, update_event=True):
        status = EventStatus.success if error_message is None else EventStatus.failure
        msg_id_splitted = split_feed_group_message_id(msg_id)
        self.session.query(self.FeedGroup) \
            .filter(self.FeedGroup.event_id == msg_id_splitted['event_id']) \
            .filter(self.FeedGroup.id == msg_id_splitted['id']) \
            .update({'status': status, 'error_message': error_message}, synchronize_session=False)

        if update_event:
            if status == EventStatus.failure:
                event_update = {'status': EventStatus.failure.value}
            else:
                query = self.session.query(self.FeedGroup.status) \
                    .filter(self.FeedGroup.event_id == msg_id_splitted['event_id']) \
                    .filter(self.FeedGroup.id != msg_id_splitted['id'])

                other_feed_groups_status = [result[0] for result in query.all()]
                event_update = {
                    'status': EventStatus.failure
                    if EventStatus.failure in other_feed_groups_status
                    else EventStatus.success
                    if all([status == EventStatus.success for status in other_feed_groups_status])
                    else EventStatus.pending
                }

            self.session.query(self.Event) \
                .filter(self.Event.id == msg_id_splitted['event_id']) \
                .update(event_update, synchronize_session=False)
        self.session.commit()

    def create_sync_feeds_event(self, id, s3_bucket, s3_key, username):
        self.session.add(self.SyncFeedsEvent(id=id, s3_bucket=s3_bucket, s3_key=s3_key, username=username))
        self.session.commit()

    def create_assets_sync_event(self, id, database, s3_bucket, s3_key, username):
        self.session.add(self.SyncAsEvent(id=id, s3_bucket=s3_bucket, s3_key=s3_key, database=database,
                                          username=username))
        self.session.commit()

    def create_event(self, id, name, number_of_feeds, event_type, data_source=None, username=None):
        event_type_to_cls = {
            'subscribe': self.SubscribeEvent,
            'unsubscribe': self.UnsubscribeEvent,
            'backfill': self.BackfillEvent,
            'interpolate': self.InterpolateEvent
        }
        assert event_type in event_type_to_cls
        cls = event_type_to_cls[event_type]

        # probably not the best way to do it
        if data_source is None:
            self.session.add(cls(id=id, name=name, number_of_feeds=number_of_feeds, username=username))
        else:
            self.session.add(cls(id=id, name=name, number_of_feeds=number_of_feeds, data_source=data_source,
                                 username=username))
        self.session.commit()

    def create_reset_event(self, id, status, username):
        self.session.add(self.ResetEvent(id=id, status=status, username=username))
        self.session.commit()

    def create_feed_group(self, id, event_id, feeds):
        self.session.add(self.FeedGroup(id=id, event_id=event_id, feeds=feeds))
        self.session.commit()

    def reset_data(self):
        tables_to_truncate = [self.Asset, self.Attribute, self.FeedGroup, self.Event, self.Feed]
        [self.session.query(tbl).delete(synchronize_session=False) for tbl in tables_to_truncate]
        self.session.commit()

    def clean_session(self):
        self.session.remove()

    def get_event_by_id(self, event_id):
        event = self.session.query(self.Event).get(event_id)
        if event is not None:
            return event.as_dict()

    def get_settings(self):
        settings = self.session.query(self.Settings).all()
        return {setting.name: setting.value for setting in settings}

    def save_settings(self, settings):
        for name, value in settings.items():
            self.session.merge(self.Settings(name=name, value=value))
        self.session.commit()

    def get_data_sources(self):
        return self.data_sources

    @abstractmethod
    def _get_feed_model(self):
        pass

    @abstractmethod
    def _get_event_model(self):
        pass

    @abstractmethod
    def _get_feed_group_model(self):
        pass

    @abstractmethod
    def _get_attribute_model(self):
        pass

    @abstractmethod
    def _get_sync_as_event_model(self):
        pass

    @abstractmethod
    def _get_sync_feeds_event_model(self):
        pass

    @abstractmethod
    def _get_asset_model(self):
        pass

    @abstractmethod
    def _get_subscribe_event_model(self):
        pass

    @abstractmethod
    def _get_unsubscribe_event_model(self):
        pass

    @abstractmethod
    def _get_backfill_event_model(self):
        pass

    @abstractmethod
    def _get_interpolate_event_model(self):
        pass

    @abstractmethod
    def _get_reset_event_model(self):
        pass

    @abstractmethod
    def _get_settings_model(self):
        pass

    @abstractmethod
    def _get_data_sources(self):
        return {}

    @abstractmethod
    def _get_query_filters(self):
        return {}

    @abstractmethod
    def create_asset(self, node, parent_id):
        return {}

    @abstractmethod
    def create_attribute(self, node, attribute):
        return {}
