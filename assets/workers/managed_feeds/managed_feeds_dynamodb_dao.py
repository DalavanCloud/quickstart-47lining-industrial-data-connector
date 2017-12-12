import datetime
import functools
import os
import json
import logging
from time import sleep

import itertools
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

log = logging.getLogger(__name__)


def dynamo_throttle(min_sleep=0, max_sleep=120, collect_single_item=False, collect_many_items=False):
    DYNAMO_THROTTLING_ERROR_CODES = [
        'ProvisionedThroughputExceededException',
        'ThrottlingException'
    ]
    sleep_seconds = min_sleep
    current_action = None

    def handle_throttling_exception(exception):
        nonlocal sleep_seconds
        error_code = exception.response['Error']['Code']
        if error_code not in DYNAMO_THROTTLING_ERROR_CODES:
            raise exception
        sleep_seconds = min((sleep_seconds + 0.1) * 2, max_sleep)
        log.info('Throttling exception, sleeping for {} seconds'.format(sleep_seconds))
        sleep(sleep_seconds)

    def run_next_action(dynamo_actions_generator):
        nonlocal current_action
        nonlocal sleep_seconds
        if current_action is None:
            current_action = next(dynamo_actions_generator)
        response = current_action()
        if 'LastEvaluatedKey' in response:
            current_action = functools.partial(current_action, ExclusiveStartKey=response['LastEvaluatedKey'])
        else:
            current_action = None  # action is completed
        sleep_seconds = max(min_sleep, sleep_seconds // 2)
        return response

    def parse_responses(responses):
        if collect_single_item:
            assert len(responses) == 1
            return responses[0]['Item']
        if collect_many_items:
            return list(itertools.chain(*[response['Items'] for response in responses]))

    def outer(fun):

        @functools.wraps(fun)
        def inner(*args, **kwargs):
            generator_exhausted = False
            dynamo_actions_generator = fun(*args, **kwargs)
            responses = []
            while not generator_exhausted:
                try:
                    response = run_next_action(dynamo_actions_generator)
                    responses.append(response)
                except ClientError as exception:
                    handle_throttling_exception(exception)
                except StopIteration:
                    generator_exhausted = True
            return parse_responses(responses)
        return inner

    return outer


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

    @dynamo_throttle(collect_many_items=True)
    def recent_events(self, limit):
        current_date = datetime.datetime.utcnow()
        dates = (current_date - datetime.timedelta(days=x) for x in range(0, limit))
        for date in dates:
            yield functools.partial(
                self.events_status_table.query,
                IndexName='EventDateIndex',
                KeyConditionExpression=Key('create_date').eq(date.strftime('%Y-%m-%d')),
                ScanIndexForward=False
            )

    @dynamo_throttle(collect_single_item=True)
    def get_event_by_id(self, event_id):
        yield functools.partial(self.events_status_table.get_item, Key={'id': event_id})

    @dynamo_throttle(collect_many_items=True)
    def list_pi_points(self):
        yield functools.partial(self.pi_points_table.scan)

    @dynamo_throttle(collect_many_items=True)
    def _get_af_sync_events(self, database):
        yield functools.partial(
            self.events_status_table.query,
            IndexName='EventTimestampIndex',
            KeyConditionExpression=Key('event_type').eq('sync_af'),
            FilterExpression='#DB = :db AND #STATUS = :success',
            ExpressionAttributeNames={"#DB": "database", "#STATUS": "status"},
            ExpressionAttributeValues={":db": database, ":success": "success"},
            ScanIndexForward=False
        )

    def get_latest_af_structure(self, database):
        all_items = self._get_af_sync_events(database)

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

    @dynamo_throttle()
    def update_pi_points(self, pi_points):
        all_pi_points = set([point['pi_point'] for point in self.list_pi_points()])
        pi_points = set(pi_points)
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

    @dynamo_throttle()
    def update_pi_points_status(self, pi_points, status):
        assert status in ['pending', 'subscribed', 'unsubscribed']
        for pi_point in pi_points:
            yield functools.partial(
                self.pi_points_table.update_item,
                Key={'pi_point': pi_point},
                UpdateExpression="SET subscription_status = :subscription_value, update_timestamp = :timestamp",
                ExpressionAttributeValues={
                    ":subscription_value": status,
                    ":timestamp": self.get_current_timestamp()
                }
            )

    @dynamo_throttle()
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
        yield functools.partial(
            self.events_status_table.update_item,
            ExpressionAttributeNames={
                "#STATUS": "status"
            },
            Key={'id': id},
            UpdateExpression=update_expressions,
            ExpressionAttributeValues=expression_attributes
        )

    @dynamo_throttle()
    def create_sync_pi_points_event(self, id, s3_bucket, s3_key):
        yield functools.partial(
            self.events_status_table.put_item,
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

    @dynamo_throttle()
    def create_assets_sync_event(self, id, database, s3_bucket, s3_key):
        yield functools.partial(
            self.events_status_table.put_item,
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

    @dynamo_throttle()
    def create_backfill_event(self, id, pi_points, status, name):
        yield functools.partial(
            self.events_status_table.put_item,
            Item={
                'id': id,
                'pi_points': pi_points,
                'event_type': 'backfill',
                'create_date': self.get_current_date(),
                'update_timestamp': self.get_current_timestamp(),
                'status': status,
                'name': name
            }
        )

    @dynamo_throttle()
    def create_interpolation_event(self, id, pi_points, name, status):
        yield functools.partial(
            self.events_status_table.put_item,
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

    @dynamo_throttle()
    def create_event(self, id, pi_points, event_type):
        yield functools.partial(
            self.events_status_table.put_item,
            Item={
                'id': id,
                'pi_points': pi_points,
                'event_type': event_type,
                'create_date': self.get_current_date(),
                'update_timestamp': self.get_current_timestamp(),
                'status': 'pending'
            }
        )
