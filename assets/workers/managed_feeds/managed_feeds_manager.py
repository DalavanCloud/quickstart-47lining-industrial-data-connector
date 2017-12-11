import datetime
import logging
import os
import tempfile
import json

import boto3

from service.sqs_service import SQSService
from utils.pi_points_s3 import iter_list_chunks
from workers.managed_feeds.managed_feeds_dynamodb_dao import ManagedFeedsDynamodbDao

log = logging.getLogger(__name__)


class ManagedFeedsManager:

    FEED_GROUP_SIZE = 100

    def __init__(self, s3_resource, sqs_service, managed_feeds_dao):
        self.s3_resource = s3_resource
        self.sqs_service = sqs_service
        self.managed_feeds_dao = managed_feeds_dao

    @staticmethod
    def create_manager(aws_region, pi_points_table_name, events_status_table_name,
                       incoming_queue_name=None, outgoing_queue_name=None):
        queues = dict()
        boto_session = boto3.session.Session()
        if incoming_queue_name is not None:
            queues["incoming_queue"] = boto_session.resource('sqs', region_name=aws_region).get_queue_by_name(QueueName=incoming_queue_name)
        if outgoing_queue_name is not None:
            queues["outgoing_queue"] = boto_session.resource('sqs', region_name=aws_region).get_queue_by_name(QueueName=outgoing_queue_name)

        sqs_service = SQSService(**queues)
        dynamodb_resource = boto_session.resource('dynamodb', region_name=aws_region)
        s3_client = boto_session.client('s3', region_name=aws_region)

        dynamodb_dao = ManagedFeedsDynamodbDao(
            dynamodb_resource,
            pi_points_table_name,
            events_status_table_name,
            s3_client
        )

        s3_resource = boto_session.resource('s3', region_name=aws_region)
        return ManagedFeedsManager(s3_resource, sqs_service, dynamodb_dao)

    @staticmethod
    def _make_unique_s3_key(prefix, file_name):
        date_str = datetime.datetime.utcnow().strftime('%Y%m%d_%H%M%S')
        return os.path.join(prefix, date_str, file_name)

    def get_latest_af_structure(self, database):
        return self.managed_feeds_dao.get_latest_af_structure(database)

    def get_recent_events(self, limit):
        return self.managed_feeds_dao.recent_events(limit)

    def get_pi_points(self):
        return self.managed_feeds_dao.list_pi_points()

    def get_managed_feeds(self):
        return self.managed_feeds_dao.list_managed_feeds()

    # Subscribe/unsubscribe

    def send_subscribe_request(self, pi_points, pi_points_assets=None):
        assert pi_points_assets is None or len(pi_points) == len(pi_points_assets)

        for feed_group in iter_list_chunks(pi_points, ManagedFeedsManager.FEED_GROUP_SIZE):
            msg_id = self.sqs_service.send_structured_message(
                payload={"points": feed_group},
                action='subscribe'
            )
            self.managed_feeds_dao.create_event(msg_id, feed_group, 'subscribe')
            self.managed_feeds_dao.update_pi_points_status(feed_group, 'pending')

    def send_unsubscribe_request(self, pi_points):
        for feed_group in iter_list_chunks(pi_points, ManagedFeedsManager.FEED_GROUP_SIZE):
            msg_id = self.sqs_service.send_structured_message(
                payload={"points": feed_group},
                action='unsubscribe'
            )
            self.managed_feeds_dao.create_event(msg_id, feed_group, 'unsubscribe')
            self.managed_feeds_dao.update_pi_points_status(feed_group, 'pending')

    def handle_subscribe_request(self, id, payload):
        subscribed_points = set(payload.get('points', []))
        event = self.managed_feeds_dao.get_event_by_id(id)
        failed_points = set(event['pi_points']) - subscribed_points
        self.managed_feeds_dao.update_pi_points_status(subscribed_points, 'subscribed')
        self.managed_feeds_dao.update_pi_points_status(failed_points, 'unsubscribed')
        self.managed_feeds_dao.update_event_status(id, payload.get('error_message'))

    def handle_unsubscribe_request(self, id, payload):
        unsubscribed_points = set(payload.get('points', []))
        event = self.managed_feeds_dao.get_event_by_id(id)
        failed_points = set(event['pi_points']) - unsubscribed_points
        self.managed_feeds_dao.update_pi_points_status(unsubscribed_points, 'unsubscribed')
        self.managed_feeds_dao.update_pi_points_status(failed_points, 'subscribed')
        self.managed_feeds_dao.update_event_status(id, payload.get('error_message'))

    # Syncing Pi points

    def send_sync_pi_points_request(self, s3_bucket):
        payload = {
            's3_bucket': s3_bucket,
            's3_key': self._make_unique_s3_key('pi_points_sync', 'pi_points.json')
        }
        msg_id = self.sqs_service.send_structured_message(
            action='sync_pi_points',
            payload=payload
        )
        self.managed_feeds_dao.create_sync_pi_points_event(id=msg_id, **payload)

    def _synchronize_pi_points(self, s3_bucket, s3_key):
        with tempfile.TemporaryFile() as file:
            self.s3_resource.Bucket(s3_bucket).download_fileobj(s3_key, file)
            file.seek(0)
            pi_points_json = file.read().decode('utf-8')
        pi_points = json.loads(pi_points_json)
        self.managed_feeds_dao.update_pi_points(pi_points)

    def handle_sync_pi_points(self, id, payload):
        error_message = payload.get('error_message')
        if error_message is None:
            try:
                event = self.managed_feeds_dao.get_event_by_id(id)
                self._synchronize_pi_points(event['s3_bucket'], event['s3_key'])
            except Exception as ex:
                error_message = str(ex)
        self.managed_feeds_dao.update_event_status(id, error_message)

    # Syncing AF structure

    def send_sync_af_request(self, s3_bucket, database):
        s3_key = self._make_unique_s3_key(
            'af_structure_sync/{}'.format(database),
            'af_structure.json'
        )
        payload = {
            'database': database,
            's3_bucket': s3_bucket,
            's3_key': s3_key
        }
        msg_id = self.sqs_service.send_structured_message(action='sync_af', payload=payload)
        self.managed_feeds_dao.create_assets_sync_event(id=msg_id, **payload)

    def handle_sync_af(self, id, payload):
        self.managed_feeds_dao.update_event_status(id, payload.get('error_message'))

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
        else:
            assert request_from is not None
            assert request_to is not None
            payload['from'] = request_from
            payload['to'] = request_to

        for feed_group in iter_list_chunks(feeds, ManagedFeedsManager.FEED_GROUP_SIZE):
            payload['points'] = feed_group

            msg_id = self.sqs_service.send_structured_message(payload=payload, action='backfill')

            self.managed_feeds_dao.create_backfill_event(
                id=msg_id,
                status='pending',
                pi_points=feed_group,
                name=name if name is not None else 'Backfill'
            )

    @staticmethod
    def _get_error_message(payload):
        failed_points = payload.get('failed_points')
        if failed_points is not None:
            return str({point['point']: point['error_message'] for point in failed_points})

    def handle_backfill_status(self, id, payload):
        self.managed_feeds_dao.update_event_status(id, self._get_error_message(payload))

    # Interpolation

    def send_interpolate_request(self, query_syntax, feeds, interval, interval_unit, name,
                                 query=None, request_from=None, request_to=None):
        interval_seconds = self._interval_seconds(interval, interval_unit)
        payload = {
            'use_date_query_syntax': False,
            'interval_seconds': interval_seconds,
            'interpolation_name': name
        }
        if query_syntax:
            payload['use_date_query_syntax'] = True
            payload['date_query'] = query
        else:
            payload['from'] = request_from
            payload['to'] = request_to

        for feed_group in iter_list_chunks(feeds, ManagedFeedsManager.FEED_GROUP_SIZE):
            payload['points'] = feed_group
            msg_id = self.sqs_service.send_structured_message(
                action='interpolate',
                payload=payload
            )
            self.managed_feeds_dao.create_interpolation_event(
                status='pending',
                pi_points=feed_group,
                id=msg_id,
                name=name if name is not None else 'Interpolate'
            )

    def handle_interpolation_status(self, id, payload):
        self.managed_feeds_dao.update_event_status(id, self._get_error_message(payload))

    def start_processing_requests(self):
        handlers = {
            'subscribe': self.handle_subscribe_request,
            'unsubscribe': self.handle_unsubscribe_request,
            'sync_af': self.handle_sync_af,
            'sync_pi_points': self.handle_sync_pi_points,
            'backfill': self.handle_backfill_status,
            'interpolate': self.handle_interpolation_status
        }
        while True:
            for uid, action, payload in self.sqs_service.iter_messages(long_polling_seconds=20):
                handler = handlers.get(action)
                if handler is None:
                    log.error('Invalid action {} received'.format(action))
                else:
                    try:
                        handler(uid, payload)
                    except Exception as e:
                        log.exception(e)

    def _interval_seconds(self, interval, interval_unit):
        interval_multiplier = {
            'seconds': 1,
            'minutes': 60,
            'hours': 60 * 60
        }
        return int(interval) * interval_multiplier[interval_unit]
