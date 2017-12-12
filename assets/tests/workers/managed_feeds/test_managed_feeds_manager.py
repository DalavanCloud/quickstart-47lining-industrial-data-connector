from io import BytesIO
from operator import itemgetter
from datetime import datetime

from freezegun import freeze_time

from tests.fixtures import *


@freeze_time('2016-01-02 12:00:00')
def test_get_recent_events(managed_feeds_manager, events_status_table):
    events_status_table.put_item(
        Item={
            "update_timestamp": '2016-01-02 11:12:13',
            'create_date': '2016-01-02',
            "pi_point": "point1",
            'event_type': 'backfill',
            "is_success": True,
            "id": "1",
            "message": "msg"
        }
    )
    events_status_table.put_item(
        Item={
            "update_timestamp": '2016-01-02 11:12:14',
            'create_date': '2016-01-02',
            "pi_point": "point1",
            'event_type': 'backfill',
            "is_success": True,
            "id": "2",
            "message": "msg"
        }
    )
    events_status_table.put_item(
        Item={
            "update_timestamp": '2016-01-01 11:12:14',
            'create_date': '2016-01-01',
            "pi_point": "point2",
            'event_type': 'backfill',
            "id": "3",
            "is_success": True,
            "message": "msg"
        }
    )
    events_status_table.put_item(
        Item={
            "update_timestamp": '2015-31-12 11:12:13',
            'create_date': '2015-31-12',
            "pi_point": "point1",
            'event_type': 'interpolate',
            "is_success": True,
            "id": "4",
            "message": "msg"
        }
    )
    events_status_table.put_item(
        Item={
            "update_timestamp": '2015-30-12 11:12:15',
            'create_date': '2015-30-12',
            "pi_point": "point2",
            'event_type': 'interpolate',
            "id": "5",
            "is_success": True,
            "message": "msg"
        }
    )
    retrieved_events_last_day = managed_feeds_manager.get_recent_events(1)

    assert len(retrieved_events_last_day) == 2
    assert retrieved_events_last_day == [
        {
            "update_timestamp": '2016-01-02 11:12:14',
            'create_date': '2016-01-02',
            "pi_point": "point1",
            'event_type': 'backfill',
            "id": "2",
            "is_success": True,
            "message": "msg"
        },
        {
            "update_timestamp": '2016-01-02 11:12:13',
            'create_date': '2016-01-02',
            "pi_point": "point1",
            'event_type': 'backfill',
            "id": "1",
            "is_success": True,
            "message": "msg"
        },
    ]

    retrieved_events_2_days = managed_feeds_manager.get_recent_events(2)

    assert len(retrieved_events_2_days) == 3
    assert retrieved_events_2_days == [
        {
            "update_timestamp": '2016-01-02 11:12:14',
            'create_date': '2016-01-02',
            "pi_point": "point1",
            'event_type': 'backfill',
            "id": "2",
            "is_success": True,
            "message": "msg"
        },
        {
            "update_timestamp": '2016-01-02 11:12:13',
            'create_date': '2016-01-02',
            "pi_point": "point1",
            'event_type': 'backfill',
            "id": "1",
            "is_success": True,
            "message": "msg"
        },
        {
            "update_timestamp": '2016-01-01 11:12:14',
            'create_date': '2016-01-01',
            "pi_point": "point2",
            'event_type': 'backfill',
            "is_success": True,
            "id": "3",
            "message": "msg"
        }
    ]


def test_list_pi_points(managed_feeds_manager, pi_points_dynamo_table):
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1', 'subscription_status': 'pending'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point2', 'subscription_status': 'subscribed'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point3'})

    points = managed_feeds_manager.get_pi_points()
    sorted_points = sorted(points, key=itemgetter('pi_point'))

    assert sorted_points == [
        {'pi_point': 'point1', 'subscription_status': 'pending'},
        {'pi_point': 'point2', 'subscription_status': 'subscribed'},
        {'pi_point': 'point3'}
    ]


@freeze_time('2016-01-02 11:12:13')
def test_send_subscribe_request(managed_feeds_manager, pi_points_dynamo_table, incoming_queue,
                                sqs_uuid4, events_status_table):
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1', 'asset': 'asset1'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point2', 'asset': 'asset2'})
    sqs_uuid4.return_value = '1'

    managed_feeds_manager.send_subscribe_request(['point1', 'point2'])

    points = pi_points_dynamo_table.scan()['Items']
    sorted_points = sorted(points, key=itemgetter('pi_point'))
    events = events_status_table.scan()['Items']

    assert sorted_points == [
        {'pi_point': 'point1', 'subscription_status': 'pending',
         'update_timestamp': '2016-01-02T11:12:13', 'asset': 'asset1'},
        {'pi_point': 'point2', 'subscription_status': 'pending',
         'update_timestamp': '2016-01-02T11:12:13', 'asset': 'asset2'}
    ]
    assert events == [
        {'status': 'pending', 'event_type': 'subscribe', 'update_timestamp': '2016-01-02T11:12:13',
         'id': '1', 'pi_points': ['point1', 'point2'], 'create_date': '2016-01-02'}
    ]
    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'subscribe',
            'created_at': '2016-01-02T11:12:13',
            'payload': {'points': ['point1', 'point2']}
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_subscribe_request(managed_feeds_manager, pi_points_dynamo_table, events_status_table):
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point2'})
    events_status_table.put_item(Item={'id': '1', 'status': 'pending', 'pi_points': ['point1', 'point2'], 'create_date': '2016-01-02'})
    payload = {'points': ['point1', 'point2']}

    managed_feeds_manager.handle_subscribe_request('1', payload)

    points = pi_points_dynamo_table.scan()['Items']
    sorted_points = sorted(points, key=itemgetter('pi_point'))
    events = events_status_table.scan()['Items']

    assert sorted_points == [
        {'pi_point': 'point1', 'subscription_status': 'subscribed', 'update_timestamp': '2016-01-02T11:12:13'},
        {'pi_point': 'point2', 'subscription_status': 'subscribed', 'update_timestamp': '2016-01-02T11:12:13'}
    ]
    assert events == [
        {'id': '1', 'update_timestamp': '2016-01-02T11:12:13', 'pi_points': ['point1', 'point2'], 'status': 'success',
         'create_date': '2016-01-02'}
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_failed_subscribe_request(managed_feeds_manager, pi_points_dynamo_table, events_status_table):
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1', 'subscription_status': 'pending'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point2', 'subscription_status': 'pending'})
    events_status_table.put_item(Item={'id': '1', 'status': 'pending', 'pi_points': ['point1', 'point2'], 'create_date': '2016-01-02'})
    payload = {'points': ['point1'], 'error_message': 'point2 failed'}

    managed_feeds_manager.handle_subscribe_request('1', payload)

    points = pi_points_dynamo_table.scan()['Items']
    sorted_points = sorted(points, key=itemgetter('pi_point'))
    events = events_status_table.scan()['Items']

    assert sorted_points == [
        {'pi_point': 'point1', 'subscription_status': 'subscribed', 'update_timestamp': '2016-01-02T11:12:13'},
        {'pi_point': 'point2', 'subscription_status': 'unsubscribed', 'update_timestamp': '2016-01-02T11:12:13'}
    ]
    assert events == [
        {'id': '1', 'update_timestamp': '2016-01-02T11:12:13', 'pi_points': ['point1', 'point2'],
         'status': 'failure', 'error_message': 'point2 failed', 'create_date': '2016-01-02'}
    ]


@freeze_time('2016-01-02 11:12:13')
def test_send_unsubscribe_request(managed_feeds_manager, incoming_queue, sqs_uuid4,
                                  events_status_table, pi_points_dynamo_table):
    sqs_uuid4.return_value = '1'
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point2'})

    managed_feeds_manager.send_unsubscribe_request(['point1', 'point2'])

    points = pi_points_dynamo_table.scan()['Items']
    sorted_points = sorted(points, key=itemgetter('pi_point'))
    events = events_status_table.scan()['Items']

    assert sorted_points == [
        {'pi_point': 'point1', 'subscription_status': 'pending', 'update_timestamp': '2016-01-02T11:12:13'},
        {'pi_point': 'point2', 'subscription_status': 'pending', 'update_timestamp': '2016-01-02T11:12:13'}
    ]
    assert events == [
        {'status': 'pending', 'event_type': 'unsubscribe', 'update_timestamp': '2016-01-02T11:12:13',
         'id': '1', 'pi_points': ['point1', 'point2'], 'create_date': '2016-01-02'}
    ]
    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'unsubscribe',
            'created_at': '2016-01-02T11:12:13',
            'payload': {'points': ['point1', 'point2']}
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_unsubscribe_request(managed_feeds_manager, pi_points_dynamo_table, events_status_table):
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point2'})
    events_status_table.put_item(Item={'id': '1', 'status': 'pending', 'pi_points': ['point1', 'point2'], 'create_date': '2016-01-02'})
    payload = {'points': ['point1', 'point2']}

    managed_feeds_manager.handle_unsubscribe_request('1', payload)

    points = pi_points_dynamo_table.scan()['Items']
    sorted_points = sorted(points, key=itemgetter('pi_point'))
    events = events_status_table.scan()['Items']

    assert sorted_points == [
        {'pi_point': 'point1', 'subscription_status': 'unsubscribed', 'update_timestamp': '2016-01-02T11:12:13'},
        {'pi_point': 'point2', 'subscription_status': 'unsubscribed', 'update_timestamp': '2016-01-02T11:12:13'}
    ]
    assert events == [
        {'id': '1', 'update_timestamp': '2016-01-02T11:12:13', 'pi_points': ['point1', 'point2'], 'status': 'success',
         'create_date': '2016-01-02'}
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_failed_unsubscribe_request(managed_feeds_manager, pi_points_dynamo_table, events_status_table):
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1', 'subscription_status': 'pending'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point2', 'subscription_status': 'pending'})
    events_status_table.put_item(Item={'id': '1', 'status': 'pending', 'pi_points': ['point1', 'point2'], 'create_date': '2016-01-02'})
    payload = {'points': ['point1'], 'error_message': 'point2 failed', 'create_date': '2016-01-02'}

    managed_feeds_manager.handle_unsubscribe_request('1', payload)

    points = pi_points_dynamo_table.scan()['Items']
    sorted_points = sorted(points, key=itemgetter('pi_point'))
    events = events_status_table.scan()['Items']

    assert sorted_points == [
        {'pi_point': 'point1', 'subscription_status': 'unsubscribed', 'update_timestamp': '2016-01-02T11:12:13'},
        {'pi_point': 'point2', 'subscription_status': 'subscribed', 'update_timestamp': '2016-01-02T11:12:13'}
    ]
    assert events == [
        {'id': '1', 'update_timestamp': '2016-01-02T11:12:13', 'pi_points': ['point1', 'point2'],
         'status': 'failure', 'error_message': 'point2 failed', 'create_date': '2016-01-02'}
    ]


@freeze_time('2016-01-02 11:12:13')
def test_send_sync_pi_points_request(managed_feeds_manager, incoming_queue, sqs_uuid4, events_status_table):
    sqs_uuid4.return_value = '1'

    managed_feeds_manager.send_sync_pi_points_request('bucket')

    sync_pi_points = events_status_table.scan()['Items']

    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'sync_pi_points',
            'created_at': '2016-01-02T11:12:13',
            'payload': {
                's3_bucket': 'bucket',
                's3_key': 'pi_points_sync/20160102_111213/pi_points.json'
            }
        }
    ]

    assert sync_pi_points == [
        {
            'id': '1',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'event_type': 'sync_pi_points',
            'status': 'pending',
            's3_bucket': 'bucket',
            's3_key': 'pi_points_sync/20160102_111213/pi_points.json'
        }
    ]


@freeze_time('2017-01-02 11:12:13')
def test_handle_sync_pi_points(managed_feeds_manager, pi_points_dynamo_table, events_status_table, s3_resource):
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1', 'subscription_status': 'pending'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point2', 'subscription_status': 'pending'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point3', 'subscription_status': 'subscribed'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point4', 'subscription_status': 'subscribed'})
    events_status_table.put_item(
        Item={
            'id': '1',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'event_type': 'sync_pi_points',
            'status': 'pending',
            's3_bucket': 'bucket',
            's3_key': 'pi_points.json'
        }
    )
    s3_resource.Bucket('bucket').upload_fileobj(
        BytesIO(b'["point1","point3","point5"]'),
        'pi_points.json'
    )
    payload = {
        'is_success': True
    }

    managed_feeds_manager.handle_sync_pi_points('1', payload)

    points = pi_points_dynamo_table.scan()['Items']
    sorted_points = sorted(points, key=itemgetter('pi_point'))
    events = events_status_table.scan()['Items']

    assert events == [
        {
          'id': '1', 'update_timestamp': '2017-01-02T11:12:13', 'event_type': 'sync_pi_points',
          'status': 'success', 's3_bucket': 'bucket', 's3_key': 'pi_points.json', 'create_date': '2016-01-02'
        }
    ]
    assert sorted_points == [
        {'pi_point': 'point1', 'subscription_status': 'pending'},
        {'pi_point': 'point3', 'subscription_status': 'subscribed'},
        {'pi_point': 'point5', 'subscription_status': 'unsubscribed', 'update_timestamp': '2017-01-02T11:12:13'}
    ]


@freeze_time('2016-01-02 11:12:13')
def test_send_sync_af_request(managed_feeds_manager, incoming_queue, events_status_table, sqs_uuid4):
    sqs_uuid4.return_value = '1'
    managed_feeds_manager.send_sync_af_request('bucket', 'database')

    af_structures = events_status_table.scan()['Items']

    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'sync_af',
            'created_at': '2016-01-02T11:12:13',
            'payload': {
                'database': 'database',
                's3_bucket': 'bucket',
                's3_key': 'af_structure_sync/database/20160102_111213/af_structure.json'
            }
        }
    ]

    assert af_structures == [
        {
            'id': '1',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'event_type': 'sync_af',
            'status': 'pending',
            's3_bucket': 'bucket',
            's3_key': 'af_structure_sync/database/20160102_111213/af_structure.json',
            'database': 'database'
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_sync_af(managed_feeds_manager, events_status_table):
    events_status_table.put_item(
        Item={
            'id': '1',
            'update_timestamp': '2015-11-02T22:22:22',
            'create_date': '2016-01-02',
            'status': 'pending',
            's3_bucket': 's3_bucket_name',
            's3_prefix': 's3_prefix',
            'database': 'db_name'
        }
    )
    payload = {
        "is_success": True
    }

    managed_feeds_manager.handle_sync_af('1', payload)

    af_structures = events_status_table.scan()['Items']

    assert af_structures == [
        {
            'id': '1',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'status': 'success',
            's3_bucket': 's3_bucket_name',
            's3_prefix': 's3_prefix',
            'database': 'db_name'
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_send_backfill_request(managed_feeds_manager, incoming_queue, events_status_table, sqs_uuid4):
    sqs_uuid4.return_value = 1

    managed_feeds_manager.send_backfill_request(
        query_syntax=False,
        feeds=['point1', 'point2'],
        request_from='2016-01-02T11:12:13',
        request_to='2016-01-02T11:12:13',
        name='name'
    )

    points = events_status_table.scan()['Items']

    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'backfill',
            'created_at': '2016-01-02T11:12:13',
            'payload': {
                'points': ['point1', 'point2'],
                'from': '2016-01-02T11:12:13',
                'to': '2016-01-02T11:12:13',
                'use_query_syntax': False,
                'backfill_name': 'name'
            }
        }
    ]

    assert points == [
        {
            'id': '1',
            'pi_points': ['point1', 'point2'],
            'event_type': 'backfill',
            'status': 'pending',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'name': 'name'
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_send_backfill_request_with_query(managed_feeds_manager, incoming_queue, events_status_table, sqs_uuid4):
    sqs_uuid4.return_value = 1

    managed_feeds_manager.send_backfill_request(
        query_syntax=True,
        feeds=['point1', 'point2'],
        query='-1d',
        name='name'
    )

    points = events_status_table.scan()['Items']

    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'backfill',
            'created_at': '2016-01-02T11:12:13',
            'payload': {
                'points': ['point1', 'point2'],
                'query': '-1d',
                'use_query_syntax': True,
                'backfill_name': 'name'
            }
        }
    ]

    assert points == [
        {
            'id': '1',
            'pi_points': ['point1', 'point2'],
            'event_type': 'backfill',
            'status': 'pending',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'name': 'name'
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_backfill(managed_feeds_manager, events_status_table):
    events_status_table.put_item(
        Item={
            'id': '1',
            'update_timestamp': '1999-11-11T22:22:22',
            'create_date': '2016-01-02',
            'pi_points': ['point1'],
            'event_type': 'backfill',
            'status': 'pending',
        }
    )

    managed_feeds_manager.handle_backfill_status('1', {})

    points = events_status_table.scan()['Items']

    assert points == [
        {
            "id": '1',
            "update_timestamp": '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'event_type': 'backfill',
            'pi_points': ['point1'],
            'status': 'success',
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_backfill_failed(managed_feeds_manager, events_status_table):
    events_status_table.put_item(
        Item={
            "id": '1',
            "update_timestamp": '1999-11-11T22:22:22',
            "pi_points": ["point1"],
            'event_type': 'backfill',
            'status': 'pending',
        }
    )
    payload = {
        'failed_points': [{
            'point': 'point1',
            'error_message': 'fail'
        }]
    }

    managed_feeds_manager.handle_backfill_status('1', payload)

    points = events_status_table.scan()['Items']

    assert points == [
        {
            "id": '1',
            "update_timestamp": '2016-01-02T11:12:13',
            "pi_points": ["point1"],
            'event_type': 'backfill',
            "error_message": "{'point1': 'fail'}",
            'status': 'failure',
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_send_interpolate_request(managed_feeds_manager, incoming_queue, events_status_table, sqs_uuid4):
    sqs_uuid4.return_value = 1

    managed_feeds_manager.send_interpolate_request(
        query_syntax=False,
        feeds=['point1', 'point2'],
        interval=1,
        interval_unit='seconds',
        request_from='2016-01-02T11:12:13',
        request_to='2016-01-02T11:12:13',
        name='name'
    )

    points = events_status_table.scan()['Items']

    assert incoming_queue.messages == [
        {
            "id": "1",
            "action": 'interpolate',
            'created_at': '2016-01-02T11:12:13',
            "payload": {
                "points": ['point1', 'point2'],
                'from': '2016-01-02T11:12:13',
                'to': '2016-01-02T11:12:13',
                'use_date_query_syntax': False,
                'interval_seconds': 1,
                'interpolation_name': 'name'
            }
        }
    ]

    assert points == [
        {
            'id': '1',
            'pi_points': ['point1', 'point2'],
            'event_type': 'interpolate',
            'status': 'pending',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'name': 'name'
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_send_interpolate_request_with_query(managed_feeds_manager, incoming_queue, events_status_table, sqs_uuid4):
    sqs_uuid4.return_value = 1

    managed_feeds_manager.send_interpolate_request(
        query_syntax=True,
        feeds=['point1', 'point2'],
        interval=1,
        interval_unit='seconds',
        query='-1d',
        name='name'
    )

    points = events_status_table.scan()['Items']

    assert incoming_queue.messages == [
        {
            "id": "1",
            "action": 'interpolate',
            'created_at': '2016-01-02T11:12:13',
            "payload": {
                "points": ['point1', 'point2'],
                'date_query': '-1d',
                'interval_seconds': 1,
                'use_date_query_syntax': True,
                'interpolation_name': 'name'
            }
        }
    ]

    assert points == [
        {
            'id': '1',
            'pi_points': ['point1', 'point2'],
            'event_type': 'interpolate',
            'status': 'pending',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02',
            'name': 'name'
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_interpolation(managed_feeds_manager, events_status_table):
    events_status_table.put_item(
        Item={
            'id': '1',
            'pi_points': ['point1'],
            'event_type': 'interpolate',
            'status': 'pending',
            'update_timestamp': '1999-01-02T11:12:13',
            'create_date': '2016-01-02'
        }
    )

    managed_feeds_manager.handle_interpolation_status('1', {})

    points = events_status_table.scan()['Items']

    assert points == [
        {
            'id': '1',
            'pi_points': ['point1'],
            'event_type': 'interpolate',
            'status': 'success',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02'
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_interpolation_with_failure(managed_feeds_manager, events_status_table):
    events_status_table.put_item(
        Item={
            'id': '1',
            'pi_points': ['point1', 'point2'],
            'event_type': 'interpolate',
            'status': 'pending',
            'update_timestamp': '1999-01-02T11:12:13',
            'create_date': '2016-01-02'
        }
    )

    payload = {
        "failed_points": [
            {
                "point": "point1",
                "error_message": "fail"
            }
        ]
    }

    managed_feeds_manager.handle_interpolation_status('1', payload)

    points = events_status_table.scan()['Items']

    assert points == [
        {
            'id': '1',
            'pi_points': ['point1', 'point2'],
            'error_message': "{'point1': 'fail'}",
            'event_type': 'interpolate',
            'status': 'failure',
            'update_timestamp': '2016-01-02T11:12:13',
            'create_date': '2016-01-02'
        }
    ]
