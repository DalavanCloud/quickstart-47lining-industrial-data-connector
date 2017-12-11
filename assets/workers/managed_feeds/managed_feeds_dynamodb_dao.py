import datetime
import functools
import os
import heapq
import json
import logging
from time import sleep

from boto3.dynamodb.conditions import Attr, Key
from botocore.exceptions import ClientError

log = logging.getLogger(__name__)

DYNAMO_THROTTLING_ERROR_CODES = [
    'ProvisionedThroughputExceededException',
    'ThrottlingException'
]
MIN_DYNAMO_SLEEP_SECONDS = 0
MAX_DYNAMO_SLEEP_SECONDS = 120


def throttle_and_retry(fun):

    def wrapper(*args, **kwargs):
        sleep_seconds = MIN_DYNAMO_SLEEP_SECONDS
        end = False
        dynamo_actions_gen = fun(*args, **kwargs)
        dynamo_action = None
        while not end:
            try:
                if dynamo_action is None:
                    dynamo_action = next(dynamo_actions_gen)
                dynamo_action()
                dynamo_action = None
                sleep_seconds = max(MIN_DYNAMO_SLEEP_SECONDS, sleep_seconds // 2)
            except ClientError as e:
                error_code = e.response['Error']['Code']
                if error_code in DYNAMO_THROTTLING_ERROR_CODES:
                    sleep_seconds = min((sleep_seconds + 1) * 2, MAX_DYNAMO_SLEEP_SECONDS)
                else:
                    raise e
                sleep(sleep_seconds)
            except StopIteration:
                end = True
    return wrapper


class ManagedFeedsDynamodbDao:

    def __init__(self, dynamodb, pi_points_table_name, events_status_table, s3_client, cache_dir='/tmp/af_structure_cache'):
        self.pi_points_table = dynamodb.Table(pi_points_table_name)
        self.events_status_table = dynamodb.Table(events_status_table)
        self.s3_client = s3_client
        self.cache_dir = cache_dir

    @staticmethod
    def get_current_timestamp():
        return datetime.datetime.utcnow().isoformat()

    @staticmethod
    def get_current_date():
        return datetime.datetime.utcnow().strftime('%Y-%m-%d')

    def recent_events(self, limit):
        def get_events_for_date(date):
            return self.events_status_table.query(
                IndexName='EventDateIndex',
                KeyConditionExpression=Key('create_date').eq(date.strftime('%Y-%m-%d')),
                ScanIndexForward=False
            )['Items']
        current_date = datetime.datetime.utcnow()
        dates = [current_date - datetime.timedelta(days=x) for x in range(0, limit)]
        daily_events = [get_events_for_date(date) for date in dates]
        return [event for events in daily_events for event in events]

    def get_event_by_id(self, event_id):
        response = self.events_status_table.get_item(Key={'id': event_id})
        return response.get('Item')

    def list_managed_feeds(self):
        return self.pi_points_table.scan(
            FilterExpression=Attr('subscription_status').eq('subscribed')
        )['Items']

    def list_pi_points(self):
        return self.pi_points_table.scan()['Items']

    def get_latest_af_structure(self, database):
        all_items = self.events_status_table.query(
            IndexName='EventTimestampIndex',
            KeyConditionExpression=Key('event_type').eq('sync_af'),
            FilterExpression='#DB = :db AND #STATUS = :success',
            ExpressionAttributeNames={"#DB": "database", "#STATUS": "status"},
            ExpressionAttributeValues={":db": database, ":success": "success"},
            ScanIndexForward=False
        )['Items']

        if all_items:
            item = all_items[0]
            structure = self._find_in_cache(item['id'])
            if structure is None:
                response = self.s3_client.get_object(Bucket=item['s3_bucket'], Key=item['s3_key'])
                body_str = response['Body'].read().decode('utf-8')
                self._save_in_cache(body_str, item['id'])
                return json.loads(body_str)
            else:
                return structure

    def _find_in_cache(self, structure_id):
        file_path = os.path.join(self.cache_dir, structure_id + ".json")
        if os.path.isfile(file_path):
            with open(file_path) as json_file:
                return json.load(json_file)

    def _save_in_cache(self, structure, structure_id):
        file_path = os.path.join(self.cache_dir, structure_id + ".json")
        directory = os.path.dirname(file_path)
        if not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, "w") as f:
            f.write(structure)
            f.close()

    @throttle_and_retry
    def update_pi_points(self, pi_points):
        pi_points = set(pi_points)
        all_pi_points = set(item['pi_point'] for item in self.pi_points_table.scan()['Items'])
        pi_points_to_remove = all_pi_points - pi_points
        pi_points_to_add = pi_points - all_pi_points

        for pi_point in pi_points_to_remove:
            yield functools.partial(
                self.pi_points_table.delete_item,
                Key={'pi_point': pi_point}
            )

        for pi_point in pi_points_to_add:
            yield functools.partial(
                self.pi_points_table.put_item,
                Item={
                    'pi_point': pi_point,
                    'subscription_status': 'unsubscribed',
                    'update_timestamp': self.get_current_timestamp()
                }
            )

    def update_pi_points_status(self, pi_points, status):
        assert status in ['pending', 'subscribed', 'unsubscribed']
        for pi_point in pi_points:
            self.pi_points_table.update_item(
                Key={'pi_point': pi_point},
                UpdateExpression="SET subscription_status = :subscription_value, update_timestamp = :timestamp",
                ExpressionAttributeValues={
                    ":subscription_value": status,
                    ":timestamp": self.get_current_timestamp()
                }
            )

    def update_event_status(self, id, error_message=None):
        status = 'success' if error_message is None else 'failure'
        expression_attributes = {
            ":status": status,
            ":timestamp": self.get_current_timestamp(),
        }
        update_expressions = "SET #STATUS = :status, update_timestamp = :timestamp"
        if error_message is not None:
            expression_attributes[':message'] = error_message
            update_expressions += ', error_message = :message'
        self.events_status_table.update_item(
            ExpressionAttributeNames={
                "#STATUS": "status"
            },
            Key={'id': id},
            UpdateExpression=update_expressions,
            ExpressionAttributeValues=expression_attributes
        )

    def create_sync_pi_points_event(self, id, s3_bucket, s3_key):
        self.events_status_table.put_item(
            Item={
                'id': id,
                's3_bucket': s3_bucket,
                's3_key': s3_key,
                'create_date': self.get_current_date(),
                'update_timestamp': self.get_current_timestamp(),
                'status': 'pending',
                'event_type': 'sync_pi_points'
            }
        )

    def create_assets_sync_event(self, id, database, s3_bucket, s3_key):
        self.events_status_table.put_item(
            Item={
                'id': id,
                'database': database,
                's3_bucket': s3_bucket,
                's3_key': s3_key,
                'create_date': self.get_current_date(),
                'update_timestamp': self.get_current_timestamp(),
                'status': 'pending',
                'event_type': 'sync_af'
            }
        )

    def create_backfill_event(self, id, pi_points, status, name):
        item = {
            'id': id,
            'pi_points': pi_points,
            'event_type': 'backfill',
            'create_date': self.get_current_date(),
            'update_timestamp': self.get_current_timestamp(),
            'status': status,
            'name': name
        }
        self.events_status_table.put_item(
            Item=item
        )

    def create_interpolation_event(self, id, pi_points, name, status):
        self.events_status_table.put_item(
            Item={
                'id': id,
                'pi_points': pi_points,
                'event_type': 'interpolate',
                'create_date': self.get_current_date(),
                'update_timestamp': self.get_current_timestamp(),
                'status': status,
                'name': name
            }
        )

    def create_event(self, id, pi_points, event_type):
        self.events_status_table.put_item(
            Item={
                'id': id,
                'pi_points': pi_points,
                'event_type': event_type,
                'create_date': self.get_current_date(),
                'update_timestamp': self.get_current_timestamp(),
                'status': 'pending'
            }
        )
