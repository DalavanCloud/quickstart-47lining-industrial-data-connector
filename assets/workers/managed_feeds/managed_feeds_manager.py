import datetime
import json
import logging
import os
import tempfile
import time
from itertools import chain

import boto3

from service.iot_service import IoTService
from service.sqs_service import SQSService
from utils.feeds_s3 import iter_list_chunks
from workers.managed_feeds.dao.managed_feeds_postgres_dao_kepware import ManagedFeedsPostgresDaoKepware
from workers.managed_feeds.dao.managed_feeds_postgres_dao_pi import ManagedFeedsPostgresDaoPi
from workers.managed_feeds.dao.managed_feeds_postgres_dao_wonderware import ManagedFeedsPostgresDaoWonderware
from workers.managed_feeds.user_provider.UserProvider import AnonymousUserProvider
from workers.managed_feeds.utils import get_feed_group_message_id

log = logging.getLogger(__name__)


class ManagedFeedsManager:

    PURGING_QUEUES_DELAY = 60
    TIMESTAMP_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"
    PAYLOAD_SKIP_SOURCES = ['default']

    def __init__(self, s3_resource, sqs_service, managed_feeds_dao, iot_service, user_provider):
        self.s3_resource = s3_resource
        self.sqs_service = sqs_service
        self.managed_feeds_dao = managed_feeds_dao
        self.iot_service = iot_service
        self.user_provider = user_provider

    @staticmethod
    def create_manager(aws_region, postgres_session, incoming_queue_name=None, backfill_queue_name=None,
                       interpolation_queue_name=None, subscription_queue_name=None, outgoing_queue_name=None,
                       use_iot=False, connector_type=None, user_provider=None):
        queues = dict()
        boto_session = boto3.session.Session()
        if incoming_queue_name is not None:
            queues["incoming_queue"] = boto_session.resource(
                'sqs',
                region_name=aws_region
            ).get_queue_by_name(QueueName=incoming_queue_name)
        if backfill_queue_name is not None:
            queues["backfill_queue"] = boto_session.resource(
                'sqs',
                region_name=aws_region
            ).get_queue_by_name(QueueName=backfill_queue_name)
        if interpolation_queue_name is not None:
            queues["interpolation_queue"] = boto_session.resource(
                'sqs',
                region_name=aws_region
            ).get_queue_by_name(QueueName=interpolation_queue_name)
        if subscription_queue_name is not None:
            queues["subscription_queue"] = boto_session.resource(
                'sqs',
                region_name=aws_region
            ).get_queue_by_name(QueueName=subscription_queue_name)
        if outgoing_queue_name is not None:
            queues["outgoing_queue"] = boto_session.resource(
                'sqs',
                region_name=aws_region
            ).get_queue_by_name(QueueName=outgoing_queue_name)

        sqs_service = SQSService(**queues)
        s3_client = boto_session.client('s3', region_name=aws_region)

        if connector_type == 'PI':
            postgres_dao = ManagedFeedsPostgresDaoPi(postgres_session, s3_client)
        elif connector_type == 'WONDERWARE':
            postgres_dao = ManagedFeedsPostgresDaoWonderware(postgres_session, s3_client)
        elif connector_type == 'KEPWARE':
            postgres_dao = ManagedFeedsPostgresDaoKepware(postgres_session, s3_client)
        else:
            raise NotImplementedError('Connector {} not supported'.format(connector_type))

        s3_resource = boto_session.resource('s3', region_name=aws_region)
        iot_client = boto_session.client('iot', region_name=aws_region)
        if use_iot:
            iot_service = IoTService(
                iot_client=iot_client,
                managed_feeds_dao=postgres_dao
            )
        else:
            iot_service = None

        if user_provider is None:
            user_provider = AnonymousUserProvider()
        return ManagedFeedsManager(s3_resource, sqs_service, postgres_dao, iot_service, user_provider)

    @staticmethod
    def _make_unique_s3_key(prefix, file_name):
        date_str = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return os.path.join(prefix, date_str, file_name)

    def get_events(self, type=None, status=None, timestamp_from=None, timestamp_to=None,
                   start_timestamp_from=None, start_timestamp_to=None,
                   page=None, page_size=None):
        return self.managed_feeds_dao.get_events(
            type=type,
            status=status,
            timestamp_from=timestamp_from,
            timestamp_to=timestamp_to,
            start_timestamp_from=start_timestamp_from,
            start_timestamp_to=start_timestamp_to,
            page=page,
            page_size=page_size
        )

    def get_event_feed_groups(self, event_id, page=None, page_size=None):
        return self.managed_feeds_dao.get_event_feed_groups(
            event_id=event_id,
            page=page,
            page_size=page_size
        )

    def get_feeds(self, page=None, page_size=None):
        return self.managed_feeds_dao.list_feeds(page=page, page_size=page_size)

    def get_settings(self):
        return self.managed_feeds_dao.get_settings()

    def save_settings(self, settings):
        return self.managed_feeds_dao.save_settings(settings)

    # Search

    def search_feeds(self, filters=None, pattern=None, feeds=None, status=None, use_regex=False, page=None,
                     page_size=None):
        return self.managed_feeds_dao.search_feeds(
            filters=filters,
            pattern=pattern,
            feeds=feeds,
            status=status,
            use_regex=use_regex,
            page=page,
            page_size=page_size
        )

    def search_assets(self, filters, page=None, page_size=None):
        return self.managed_feeds_dao.search_assets(
            filters=filters,
            page=page,
            page_size=page_size
        )

    def search_asset_attributes(self, asset_id, filters):
        return self.managed_feeds_dao.search_asset_attributes(
            asset_id=asset_id,
            filters=filters
        )

    # Feeds actions

    def _send_feeds_action_request(self, feeds, event_type, payload, name=None, username=None):
        event_id = self.sqs_service.generate_unique_id()
        self.managed_feeds_dao.create_event(
            id=event_id,
            name=name if name is not None else event_id,
            number_of_feeds=len(feeds),
            event_type=event_type,
            data_source=payload.get('data_source'),
            username=username if username else self.user_provider.get_username()
        )

        # If there are no feeds (e.g. subscription request with already subscribed feeds)
        # nothing can later update event so it should be set as success here.
        # Opposite way to deal with this corner case could be not creating event at all
        # but that silent processing is bad practice.
        if not feeds:
            self.managed_feeds_dao.update_event_status(event_id)

        feed_group_size = int(self.get_settings()['feed_group_size'])
        for i, feed_group in enumerate(iter_list_chunks(feeds, feed_group_size)):
            self.managed_feeds_dao.create_feed_group(i, event_id, feed_group)
            self.sqs_service.send_message(
                id=get_feed_group_message_id(i, event_id),
                action=event_type,
                payload={**payload, 'feeds': feed_group}
            )

    def _iter_time_chunks(self, timestamp_from, timestamp_to):
        """Generator to iterate over time chunks in range timestamp_from, timestamp_to
        with respect to time window defined in settings.
        Yields tuples (timestamp_from, timestamp_to) of current time chunk.
        """
        date_delta = datetime.timedelta(days=int(self.get_settings()['time_window_days']))

        datetime_from = datetime.datetime.strptime(timestamp_from, ManagedFeedsManager.TIMESTAMP_FORMAT)
        datetime_to = datetime.datetime.strptime(timestamp_to, ManagedFeedsManager.TIMESTAMP_FORMAT)

        date_iterator = datetime_from
        while date_iterator + date_delta < datetime_to:
            yield (
                date_iterator.strftime(ManagedFeedsManager.TIMESTAMP_FORMAT),
                (date_iterator + date_delta).strftime(ManagedFeedsManager.TIMESTAMP_FORMAT)
            )
            date_iterator = date_iterator + date_delta

        yield (
            date_iterator.strftime(ManagedFeedsManager.TIMESTAMP_FORMAT),
            datetime_to.strftime(ManagedFeedsManager.TIMESTAMP_FORMAT)
        )

    # Subscribe/unsubscribe

    def _get_data_source_list(self, data_source):
        return self.managed_feeds_dao.get_data_sources()\
            if data_source == 'all' or data_source is None\
            else [data_source]

    def send_subscribe_request(self, feeds, data_source=None, name=None):
        filtered_feeds = {}
        data_sources_list = self._get_data_source_list(data_source)
        for data_src in data_sources_list:
            filtered_feeds[data_src] = set(feeds) - set(
                self.managed_feeds_dao.filter_feeds(feeds, 'subscribed', data_src)
            )
        for data_src in data_sources_list:
            self.managed_feeds_dao.update_feeds_status(
                filtered_feeds[data_src], 'pending', data_source=data_src
            )
        for data_src in data_sources_list:
            payload = {'data_source': data_src}
            self._send_feeds_action_request(
                feeds=filtered_feeds[data_src],
                event_type='subscribe',
                payload=payload,
                name=name if name is not None else 'Subscribe'
            )

    def send_unsubscribe_request(self, feeds, data_source=None, name=None, username=None):
        filtered_feeds = {}
        data_sources_list = self._get_data_source_list(data_source)
        for data_src in data_sources_list:
            filtered_feeds[data_src] = set(feeds) - set(
                self.managed_feeds_dao.filter_feeds(feeds, 'unsubscribed', data_src)
            )
        for data_src in data_sources_list:
            self.managed_feeds_dao.update_feeds_status(
                filtered_feeds[data_src], 'pending', data_source=data_src
            )
        for data_src in data_sources_list:
            payload = {'data_source': data_src}
            self._send_feeds_action_request(
                feeds=filtered_feeds[data_src],
                event_type='unsubscribe',
                payload=payload,
                name=name if name is not None else 'Unsubscribe',
                username=username
            )

    def handle_subscribe_request(self, id, payload):
        subscribed_feeds = set(payload.get('feeds', []))
        data_source = payload.get('data_source')
        feed_group = self.managed_feeds_dao.get_feed_group_by_id(id)
        failed_feeds = set(feed_group['feeds']) - subscribed_feeds
        self.managed_feeds_dao.update_feeds_status(
            subscribed_feeds, 'subscribed', data_source)
        self.managed_feeds_dao.update_feeds_status(
            failed_feeds, 'unsubscribed', data_source)
        self.managed_feeds_dao.update_feed_group_status(
            id, payload.get('error_message'))
        if self.iot_service is not None:
            self.iot_service.create_things(subscribed_feeds)

    def handle_unsubscribe_request(self, id, payload):
        unsubscribed_feeds = set(payload.get('feeds', []))
        data_source = payload.get('data_source')
        feed_group = self.managed_feeds_dao.get_feed_group_by_id(id)
        failed_feeds = set(feed_group['feeds']) - unsubscribed_feeds
        self.managed_feeds_dao.update_feeds_status(
            unsubscribed_feeds, 'unsubscribed', data_source)
        self.managed_feeds_dao.update_feeds_status(
            failed_feeds, 'subscribed', data_source)
        self.managed_feeds_dao.update_feed_group_status(
            id, payload.get('error_message'))

    # Syncing feeds

    def send_sync_feeds_request(self, s3_bucket):
        payload = {
            's3_bucket': s3_bucket,
            's3_key': self._make_unique_s3_key('feeds_sync', 'feeds.json')
        }
        msg_id = self.sqs_service.send_message(
            action='sync_feeds',
            payload=payload
        )
        payload['username'] = self.user_provider.get_username()
        self.managed_feeds_dao.create_sync_feeds_event(
            id=msg_id, **payload)

    def _synchronize_feeds(self, s3_bucket, s3_key):
        with tempfile.TemporaryFile() as file:
            self.s3_resource.Bucket(s3_bucket).download_fileobj(s3_key, file)
            file.seek(0)
            feeds_json = file.read().decode('utf-8')
        feeds = json.loads(feeds_json)
        self.managed_feeds_dao.update_feeds(feeds)

    def handle_sync_feeds(self, id, payload):
        error_message = payload.get('error_message')
        if error_message is None:
            try:
                event = self.managed_feeds_dao.get_event_by_id(id)
                self._synchronize_feeds(
                    event['s3_bucket'], event['s3_key'])
            except Exception as ex:
                error_message = str(ex)
        self.managed_feeds_dao.update_event_status(id, error_message)

    # Syncing AS - asset structure

    def send_sync_as_request(self, s3_bucket, database):
        s3_key = self._make_unique_s3_key(
            'as_structure_sync/{}'.format(database),
            'as_structure.json'
        )
        payload = {
            'database': database,
            's3_bucket': s3_bucket,
            's3_key': s3_key
        }
        msg_id = self.sqs_service.send_message(action='sync_as', payload=payload)
        payload['username'] = self.user_provider.get_username()
        self.managed_feeds_dao.create_assets_sync_event(id=msg_id, **payload)
        return msg_id

    def _synchronize_as(self, s3_bucket, s3_key):
        with tempfile.TemporaryFile() as file:
            self.s3_resource.Bucket(s3_bucket).download_fileobj(s3_key, file)
            file.seek(0)
            as_structure_json = file.read().decode('utf-8')
        as_structure = json.loads(as_structure_json)
        self.managed_feeds_dao.update_as_structure(as_structure)

    def handle_sync_as(self, id, payload):
        error_message = payload.get('error_message')
        if error_message is None:
            try:
                event = self.managed_feeds_dao.get_event_by_id(id)
                self._synchronize_as(event['s3_bucket'], event['s3_key'])
            except Exception as ex:
                error_message = str(ex)

        self.managed_feeds_dao.update_event_status(id, error_message)

    def get_asset_children(self, parent_asset_id):
        return self.managed_feeds_dao.get_asset_children(parent_asset_id)

    # Backfill

    def send_backfill_request(self, query_syntax, feeds, name, query=None, request_from=None, request_to=None):
        payload = {
            'use_query_syntax': False,
            'backfill_name': name
        }
        if query_syntax:
            assert query is not None
            payload['use_query_syntax'] = True
            payload['query'] = query
            self._send_feeds_action_request(
                feeds=feeds,
                event_type='backfill',
                payload=payload,
                name=name if name is not None else 'Backfill'
            )
        else:
            assert request_from is not None
            assert request_to is not None

            for timestamp_from, timestamp_to in self._iter_time_chunks(request_from, request_to):
                payload['from'] = timestamp_from
                payload['to'] = timestamp_to
                self._send_feeds_action_request(
                    feeds=feeds,
                    event_type='backfill',
                    payload=payload,
                    name=name if name is not None else 'Backfill'
                )

    @staticmethod
    def _get_error_message(payload):
        failed_feeds = payload.get('failed_feeds')
        if failed_feeds is not None:
            return str({feed['feed']: feed['error_message'] for feed in failed_feeds})

    def handle_backfill_status(self, id, payload):
        self.managed_feeds_dao.update_feed_group_status(
            id, self._get_error_message(payload))

    # Interpolation

    def send_interpolate_request(self, query_syntax, feeds, interval, interval_unit, name,
                                 query=None, request_from=None, request_to=None):
        interval_seconds = self._convert_interval_to_seconds(interval, interval_unit)
        payload = {
            'use_date_query_syntax': False,
            'interval_seconds': interval_seconds,
            'interpolation_name': name
        }
        if query_syntax:
            assert query is not None
            payload['use_date_query_syntax'] = True
            payload['date_query'] = query
            self._send_feeds_action_request(
                feeds=feeds,
                event_type='interpolate',
                payload=payload,
                name=name if name is not None else 'Interpolate'
            )
        else:
            assert request_from is not None
            assert request_to is not None

            for timestamp_from, timestamp_to in self._iter_time_chunks(request_from, request_to):
                payload['from'] = timestamp_from
                payload['to'] = timestamp_to
                self._send_feeds_action_request(
                    feeds=feeds,
                    event_type='interpolate',
                    payload=payload,
                    name=name if name is not None else 'Interpolate'
                )

    def handle_interpolation_status(self, id, payload):
        self.managed_feeds_dao.update_feed_group_status(
            id, self._get_error_message(payload))

    def handle_get_subscribed(self, id, payload):
        all_feeds = [feed['name'] for feed in self.managed_feeds_dao.list_feeds()['feeds']]
        data_sources = self.managed_feeds_dao.get_data_sources()

        for data_source in data_sources:
            feeds = self.managed_feeds_dao.list_subscribed_feeds(data_source)
            self.managed_feeds_dao.update_feeds_status(all_feeds, 'unsubscribed', data_source)
            self.send_subscribe_request(
                feeds=feeds,
                data_source=data_source,
                name='Connector state sync after restart'
            )

    def start_processing_requests(self, message_body):
        handlers = {
            'subscribe': self.handle_subscribe_request,
            'unsubscribe': self.handle_unsubscribe_request,
            'sync_as': self.handle_sync_as,
            'sync_feeds': self.handle_sync_feeds,
            'backfill': self.handle_backfill_status,
            'interpolate': self.handle_interpolation_status,
            'get_subscribed': self.handle_get_subscribed
        }
        parsed_message = json.loads(message_body)
        uid = parsed_message['id']
        payload = parsed_message['payload']
        action = parsed_message['action']

        log.info('Handling {} action'.format(action))

        handler = handlers.get(action)
        if handler is None:
            log.error('Invalid action {} received'.format(action))
        else:
            try:
                handler(uid, payload)
                self.managed_feeds_dao.clean_session()
            except Exception as e:
                log.exception(e)
            finally:
                self.managed_feeds_dao.clean_session()

    def _convert_interval_to_seconds(self, interval, interval_unit):
        interval_multiplier = {
            'seconds': 1,
            'minutes': 60,
            'hours': 60 * 60
        }
        return int(interval) * interval_multiplier[interval_unit]

    # Events failures

    def handle_event_failure(self, event):
        error_message = 'Event not processed by Connector'
        self.managed_feeds_dao.update_event_status(
            id=event['id'],
            error_message=error_message
        )
        feed_groups = self.get_event_feed_groups(event['id'])['feed_groups']
        for feed_group in feed_groups:
            self.managed_feeds_dao.update_feed_group_status(
                msg_id=get_feed_group_message_id(feed_group['id'], event['id']),
                error_message=error_message,
                update_event=False
            )
        if event['type'] in ['subscribe', 'unsubscribe']:
            feeds = chain(*[feed_group['feeds'] for feed_group in feed_groups])
            pending_feeds = [feed['name'] for feed in self.managed_feeds_dao.filter_pending_feeds(
                feeds=feeds,
                data_source=event['data_source']
            )]
            self.managed_feeds_dao.update_feeds_status(
                feeds=pending_feeds,
                status='unknown',
                data_source=event['data_source']
            )

    def reset_database(self):
        return self.managed_feeds_dao.reset_data()

    def create_reset_event(self, status, username):
        event_id = self.sqs_service.generate_unique_id()
        self.managed_feeds_dao.create_reset_event(event_id, status, username)

    def purge_queues(self):
        self.sqs_service.purge_all_queues()
        self.wait_for_purging_queues()

    @staticmethod
    def wait_for_purging_queues():
        time.sleep(ManagedFeedsManager.PURGING_QUEUES_DELAY)
