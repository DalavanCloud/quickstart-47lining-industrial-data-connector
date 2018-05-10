import datetime
import json
from io import BytesIO
from operator import itemgetter

from freezegun import freeze_time
from mock import call

from model.models import SyncAfEvent, EventStatus, PiPoint, SubscriptionStatus, Event, InterpolateEvent, \
    SyncPiPointsEvent, BackfillEvent, SubscribeEvent, UnsubscribeEvent, Settings
from tests.fixtures import *


def test_get_recent_events(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        SyncAfEvent(
            id='1',
            error_message='Fail',
            status=EventStatus.failure,
            update_timestamp=datetime.datetime(2017, 1, 4),
            s3_bucket='bucket',
            s3_key='key',
            database='database'
        ),
        SyncPiPointsEvent(
            id='2',
            status=EventStatus.success,
            update_timestamp=datetime.datetime(2017, 1, 3),
            s3_bucket='bucket',
            s3_key='key'
        ),
        InterpolateEvent(
            id='3',
            status=EventStatus.success,
            update_timestamp=datetime.datetime(2017, 1, 2),
            pi_points=['point1', 'point2'],
            name='name'
        ),
        BackfillEvent(
            id='4',
            status=EventStatus.success,
            update_timestamp=datetime.datetime(2017, 1, 1),
            pi_points=['point1', 'point2'],
        )
    ])

    events = managed_feeds_postgres_manager.get_recent_events(3)

    assert events == [
        {
            'database': 'database',
            'error_message': 'Fail',
            'id': '1',
            's3_bucket': 'bucket',
            's3_key': 'key',
            'status': EventStatus.failure,
            'event_type': 'sync_af',
            'update_timestamp': datetime.datetime(2017, 1, 4)
        },
        {
            'error_message': None,
            'id': '2',
            's3_bucket': 'bucket',
            's3_key': 'key',
            'status': EventStatus.success,
            'event_type': 'sync_pi_points',
            'update_timestamp': datetime.datetime(2017, 1, 3)
        },
        {
            'error_message': None,
            'name': 'name',
            'id': '3',
            'pi_points': ['point1', 'point2'],
            'status': EventStatus.success,
            'event_type': 'interpolate',
            'update_timestamp': datetime.datetime(2017, 1, 2)
        }
    ]


def test_get_settings(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        Settings(
            name='Setting1',
            value='value1'
        ),
        Settings(
            name='Setting2',
            value='value2'
        )
    ])

    settings = managed_feeds_postgres_manager.get_settings()

    assert settings == {
        'Setting1': 'value1',
        'Setting2': 'value2'
    }


def test_save_settings(managed_feeds_postgres_manager, postgres_session):
    settings = {
        'Setting1': 'value1',
        'Setting2': 'value2'
    }

    managed_feeds_postgres_manager.save_settings(settings)

    settings_from_db = managed_feeds_postgres_manager.get_settings()

    assert settings_from_db == settings


def test_get_pi_points(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        PiPoint(
            pi_point='point1',
            subscription_status=SubscriptionStatus.subscribed,
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        PiPoint(
            pi_point='point2',
            subscription_status=SubscriptionStatus.pending,
            update_timestamp=datetime.datetime(2017, 1, 2)
        ),
        PiPoint(
            pi_point='point3',
            subscription_status=SubscriptionStatus.unsubscribed,
            update_timestamp=datetime.datetime(2017, 1, 3)
        )
    ])

    points_data = managed_feeds_postgres_manager.get_pi_points()
    points_data['pi_points'] = sorted(points_data['pi_points'], key=itemgetter('pi_point'))

    assert points_data == {
        'pi_points': [
            {
                'pi_point': 'point1',
                'subscription_status': SubscriptionStatus.subscribed,
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            },
            {
                'pi_point': 'point2',
                'subscription_status': SubscriptionStatus.pending,
                'update_timestamp': datetime.datetime(2017, 1, 2, 0, 0)
            },
            {
                'pi_point': 'point3',
                'subscription_status': SubscriptionStatus.unsubscribed,
                'update_timestamp': datetime.datetime(2017, 1, 3, 0, 0)
            }
        ],
        'total_count': 3
    }


def test_get_pi_points_with_pagination(managed_feeds_postgres_manager, postgres_session):
    for i in range(10):
        pi_point = PiPoint(
            pi_point='point{}'.format(i),
            subscription_status=SubscriptionStatus.subscribed,
            update_timestamp=datetime.datetime(2017, 1, 1)
        )
        postgres_session.add(pi_point)

    points_data = managed_feeds_postgres_manager.get_pi_points(page=2, page_size=2)
    points_data['pi_points'] = sorted(points_data['pi_points'], key=itemgetter('pi_point'))

    assert points_data == {
        'pi_points': [
            {
                'pi_point': 'point4',
                'subscription_status': SubscriptionStatus.subscribed,
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            },
            {
                'pi_point': 'point5',
                'subscription_status': SubscriptionStatus.subscribed,
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            }
        ],
        'total_count': 10
    }


def test_search_pi_points_with_query(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        PiPoint(
            pi_point='name-test-name',
            subscription_status=SubscriptionStatus.subscribed,
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        PiPoint(
            pi_point='test-test-test',
            subscription_status=SubscriptionStatus.pending,
            update_timestamp=datetime.datetime(2017, 1, 2)
        )
    ])

    points_data = managed_feeds_postgres_manager.search_pi_points(pattern='name-*-name')

    assert points_data == {
        'pi_points': [
            {
                'pi_point': 'name-test-name',
                'subscription_status': SubscriptionStatus.subscribed,
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            }
        ],
        'total_count': 1
    }


def test_search_pi_points_using_regex(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        PiPoint(
            pi_point='test1',
            subscription_status=SubscriptionStatus.subscribed,
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        PiPoint(
            pi_point='Test12',
            subscription_status=SubscriptionStatus.pending,
            update_timestamp=datetime.datetime(2017, 1, 2)
        )
    ])

    points_data = managed_feeds_postgres_manager.search_pi_points(
        pattern='[A-Z]{1}[a-z]?[0-9]?',
        use_regex=True
    )

    assert points_data == {
        'pi_points': [
            {
                'pi_point': 'Test12',
                'subscription_status': SubscriptionStatus.pending,
                'update_timestamp': datetime.datetime(2017, 1, 2, 0, 0)
            }
        ],
        'total_count': 1
    }


def test_search_pi_points_with_pi_points(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        PiPoint(
            pi_point='name1',
            subscription_status=SubscriptionStatus.subscribed,
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        PiPoint(
            pi_point='name2',
            subscription_status=SubscriptionStatus.subscribed,
            update_timestamp=datetime.datetime(2017, 1, 2)
        ),
        PiPoint(
            pi_point='name3',
            subscription_status=SubscriptionStatus.subscribed,
            update_timestamp=datetime.datetime(2017, 1, 3)
        )
    ])

    points_data = managed_feeds_postgres_manager.search_pi_points(pi_points=['name1', 'name3'])
    points_data['pi_points'] = sorted(points_data['pi_points'], key=itemgetter('pi_point'))

    assert points_data == {
        'pi_points': [
            {
                'pi_point': 'name1',
                'subscription_status': SubscriptionStatus.subscribed,
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            },
            {
                'pi_point': 'name3',
                'subscription_status': SubscriptionStatus.subscribed,
                'update_timestamp': datetime.datetime(2017, 1, 3, 0, 0)
            }
        ],
        'total_count': 2
    }


def test_search_pi_points_with_status(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        PiPoint(
            pi_point='name1',
            subscription_status=SubscriptionStatus.subscribed,
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        PiPoint(
            pi_point='name2',
            subscription_status=SubscriptionStatus.pending,
            update_timestamp=datetime.datetime(2017, 1, 2)
        ),
        PiPoint(
            pi_point='name3',
            subscription_status=SubscriptionStatus.unsubscribed,
            update_timestamp=datetime.datetime(2017, 1, 3)
        )
    ])

    points_data = managed_feeds_postgres_manager.search_pi_points(status='subscribed')

    assert points_data == {
        'pi_points': [
            {
                'pi_point': 'name1',
                'subscription_status': SubscriptionStatus.subscribed,
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            }
        ],
        'total_count': 1
    }


@freeze_time('2016-01-02 11:12:13')
def test_send_subscribe_request(managed_feeds_postgres_manager, incoming_queue, sqs_uuid4, postgres_session):
    postgres_session.add_all([PiPoint(pi_point='point1'), PiPoint(pi_point='point2')])
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_subscribe_request(['point1', 'point2'])

    points = postgres_session.query(PiPoint).all()
    event = postgres_session.query(Event).get('1')

    assert all(point.subscription_status == SubscriptionStatus.pending for point in points)
    assert event.pi_points == ['point1', 'point2']
    assert event.event_type == 'subscribe'
    assert event.status == EventStatus.pending
    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'subscribe',
            'created_at': '2016-01-02T11:12:13',
            'payload': {'points': ['point1', 'point2']}
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_subscribe_request(managed_feeds_postgres_manager, postgres_session, iot_service):
    postgres_session.add_all([PiPoint(pi_point='point1'), PiPoint(pi_point='point2')])
    postgres_session.add(SubscribeEvent(id='1', status=EventStatus.pending, pi_points=['point1', 'point2']))
    payload = {'points': ['point1', 'point2']}

    managed_feeds_postgres_manager.handle_subscribe_request('1', payload)

    points = postgres_session.query(PiPoint).all()
    event = postgres_session.query(Event).get('1')

    assert all(point.subscription_status == SubscriptionStatus.subscribed for point in points)
    assert event.status == EventStatus.success
    assert event.pi_points == ['point1', 'point2']
    assert iot_service.iot_client.create_thing.has_calls([call(thingName='point1'), call(thingName='point2')])


@freeze_time('2016-01-02 11:12:13')
def test_handle_failed_subscribe_request(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([PiPoint(pi_point='point1'), PiPoint(pi_point='point2')])
    postgres_session.add(SubscribeEvent(id='1', status=EventStatus.pending, pi_points=['point1', 'point2']))
    payload = {'points': ['point1'], 'error_message': 'point2 failed'}

    managed_feeds_postgres_manager.handle_subscribe_request('1', payload)

    point1 = postgres_session.query(PiPoint).get('point1')
    point2 = postgres_session.query(PiPoint).get('point2')
    event = postgres_session.query(Event).get('1')

    assert point1.subscription_status == SubscriptionStatus.subscribed
    assert point2.subscription_status == SubscriptionStatus.unsubscribed
    assert event.status == EventStatus.failure


@freeze_time('2016-01-02 11:12:13')
def test_send_unsubscribe_request(managed_feeds_postgres_manager, incoming_queue, sqs_uuid4, postgres_session):
    postgres_session.add_all([PiPoint(pi_point='point1'), PiPoint(pi_point='point2')])
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_unsubscribe_request(['point1', 'point2'])

    points = postgres_session.query(PiPoint).all()
    event = postgres_session.query(Event).get('1')

    assert all(point.subscription_status == SubscriptionStatus.pending for point in points)
    assert event.pi_points == ['point1', 'point2']
    assert event.event_type == 'unsubscribe'
    assert event.status == EventStatus.pending
    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'unsubscribe',
            'created_at': '2016-01-02T11:12:13',
            'payload': {'points': ['point1', 'point2']}
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_unsubscribe_request(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([PiPoint(pi_point='point1'), PiPoint(pi_point='point2')])
    postgres_session.add(UnsubscribeEvent(id='1', status=EventStatus.pending, pi_points=['point1', 'point2']))
    payload = {'points': ['point1', 'point2']}

    managed_feeds_postgres_manager.handle_unsubscribe_request('1', payload)

    points = postgres_session.query(PiPoint).all()
    event = postgres_session.query(Event).get('1')

    assert all(point.subscription_status == SubscriptionStatus.unsubscribed for point in points)
    assert event.status == EventStatus.success
    assert event.pi_points == ['point1', 'point2']


@freeze_time('2016-01-02 11:12:13')
def test_handle_failed_unsubscribe_request(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([PiPoint(pi_point='point1'), PiPoint(pi_point='point2')])
    postgres_session.add(UnsubscribeEvent(id='1', status=EventStatus.pending, pi_points=['point1', 'point2']))
    payload = {'points': ['point1'], 'error_message': 'point2 failed'}

    managed_feeds_postgres_manager.handle_unsubscribe_request('1', payload)

    point1 = postgres_session.query(PiPoint).get('point1')
    point2 = postgres_session.query(PiPoint).get('point2')
    event = postgres_session.query(Event).get('1')

    assert point1.subscription_status == SubscriptionStatus.unsubscribed
    assert point2.subscription_status == SubscriptionStatus.subscribed
    assert event.status == EventStatus.failure


@freeze_time('2016-01-02 11:12:13')
def test_send_sync_pi_points_request(managed_feeds_postgres_manager, incoming_queue, sqs_uuid4, postgres_session):
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_sync_pi_points_request('bucket')

    event = postgres_session.query(Event).get('1')

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

    assert event.event_type == 'sync_pi_points'
    assert event.status == EventStatus.pending
    assert event.s3_bucket == 'bucket'
    assert event.s3_key == 'pi_points_sync/20160102_111213/pi_points.json'


@freeze_time('2017-01-02 11:12:13')
def test_handle_sync_pi_points(managed_feeds_postgres_manager, postgres_session, s3_resource):
    postgres_session.add_all([
        PiPoint(pi_point='point1', subscription_status=SubscriptionStatus.pending),
        PiPoint(pi_point='point2', subscription_status=SubscriptionStatus.pending),
        PiPoint(pi_point='point3', subscription_status=SubscriptionStatus.subscribed),
        PiPoint(pi_point='point4', subscription_status=SubscriptionStatus.subscribed),
    ])
    postgres_session.add(
        SyncPiPointsEvent(id='1', status=EventStatus.pending, s3_bucket='bucket', s3_key='pi_points.json')
    )
    s3_resource.Bucket('bucket').upload_fileobj(
        BytesIO(b'["point1","point3","point5"]'),
        'pi_points.json'
    )
    payload = {}

    managed_feeds_postgres_manager.handle_sync_pi_points('1', payload)

    points = postgres_session.query(PiPoint).all()
    point1 = postgres_session.query(PiPoint).get('point1')
    point3 = postgres_session.query(PiPoint).get('point3')
    point5 = postgres_session.query(PiPoint).get('point5')
    event = postgres_session.query(Event).get('1')

    assert len(points) == 3
    assert point1.subscription_status == SubscriptionStatus.pending
    assert point3.subscription_status == SubscriptionStatus.subscribed
    assert point5.subscription_status == SubscriptionStatus.unsubscribed
    assert event.status == EventStatus.success


@freeze_time('2016-01-02 11:12:13')
def test_send_sync_af_request(managed_feeds_postgres_manager, incoming_queue, postgres_session, sqs_uuid4):
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_sync_af_request('bucket', 'database')

    event = postgres_session.query(Event).get('1')

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

    assert event.event_type == 'sync_af'
    assert event.status == EventStatus.pending
    assert event.s3_bucket == 'bucket'
    assert event.s3_key == 'af_structure_sync/database/20160102_111213/af_structure.json'
    assert event.database == 'database'


@freeze_time('2016-01-02 11:12:13')
def test_handle_sync_af(managed_feeds_postgres_manager, postgres_session, s3_resource):
    managed_feeds_postgres_manager._make_unique_s3_key = lambda *args, **kwargs: 'af_structure.json'
    msg_id = managed_feeds_postgres_manager.send_sync_af_request('bucket', 'NuGreen')
    af_structure = {
        "name": "NuGreen",
        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen",
        "description": None,
        "template": None,
        "categories": None,
        "attributes": None,
        "assets": []
    }
    s3_resource.Bucket('bucket').upload_fileobj(
        BytesIO(json.dumps(af_structure).encode()),
        'af_structure.json'
    )
    payload = {}

    managed_feeds_postgres_manager.handle_sync_af(msg_id, payload)

    event = postgres_session.query(Event).get(msg_id)

    assert event.status == EventStatus.success


@freeze_time('2016-01-02 11:12:13')
def test_send_backfill_request(managed_feeds_postgres_manager, postgres_session, incoming_queue, sqs_uuid4):
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_backfill_request(
        query_syntax=False,
        feeds=['point1', 'point2'],
        request_from='2016-01-02T11:12:13',
        request_to='2016-01-02T11:12:13',
        name='name'
    )

    event = postgres_session.query(Event).get('1')

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

    assert event.pi_points == ['point1', 'point2']
    assert event.status == EventStatus.pending
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_send_backfill_request_with_query(managed_feeds_postgres_manager, incoming_queue, postgres_session, sqs_uuid4):
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_backfill_request(
        query_syntax=True,
        feeds=['point1', 'point2'],
        query='-1d',
        name='name'
    )

    event = postgres_session.query(Event).get('1')

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

    assert event.pi_points == ['point1', 'point2']
    assert event.status == EventStatus.pending
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_handle_backfill(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add(
        BackfillEvent(id='1', pi_points=['point1'], status=EventStatus.pending, name='name')
    )

    managed_feeds_postgres_manager.handle_backfill_status('1', {})

    event = postgres_session.query(Event).get('1')

    assert event.pi_points == ['point1']
    assert event.status == EventStatus.success
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_handle_backfill_failed(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add(
        BackfillEvent(id='1', pi_points=['point1'], status=EventStatus.pending, name='name')
    )
    payload = {
        'failed_points': [{
            'point': 'point1',
            'error_message': 'fail'
        }]
    }

    managed_feeds_postgres_manager.handle_backfill_status('1', payload)

    event = postgres_session.query(Event).get('1')

    assert event.pi_points == ['point1']
    assert event.status == EventStatus.failure
    assert event.name == 'name'
    assert event.error_message == "{'point1': 'fail'}"


@freeze_time('2016-01-02 11:12:13')
def test_send_interpolate_request(managed_feeds_postgres_manager, incoming_queue, postgres_session, sqs_uuid4):
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_interpolate_request(
        query_syntax=False,
        feeds=['point1', 'point2'],
        interval=1,
        interval_unit='seconds',
        request_from='2016-01-02T11:12:13',
        request_to='2016-01-02T11:12:13',
        name='name'
    )

    event = postgres_session.query(Event).get('1')

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

    assert event.pi_points == ['point1', 'point2']
    assert event.status == EventStatus.pending
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_send_interpolate_request_with_query(managed_feeds_postgres_manager, incoming_queue, postgres_session, sqs_uuid4):
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_interpolate_request(
        query_syntax=True,
        feeds=['point1', 'point2'],
        interval=1,
        interval_unit='seconds',
        query='-1d',
        name='name'
    )

    event = postgres_session.query(Event).get('1')

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

    assert event.pi_points == ['point1', 'point2']
    assert event.status == EventStatus.pending
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_handle_interpolation(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add(
        InterpolateEvent(id='1', pi_points=['point1'], status=EventStatus.pending, name='name')
    )

    managed_feeds_postgres_manager.handle_interpolation_status('1', {})

    event = postgres_session.query(Event).get('1')

    assert event.pi_points == ['point1']
    assert event.status == EventStatus.success
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_handle_interpolation_with_failure(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add(
        BackfillEvent(id='1', pi_points=['point1'], status=EventStatus.pending, name='name')
    )
    payload = {
        "failed_points": [
            {
                "point": "point1",
                "error_message": "fail"
            }
        ]
    }

    managed_feeds_postgres_manager.handle_interpolation_status('1', payload)

    event = postgres_session.query(Event).get('1')

    assert event.pi_points == ['point1']
    assert event.status == EventStatus.failure
    assert event.name == 'name'
    assert event.error_message == "{'point1': 'fail'}"
