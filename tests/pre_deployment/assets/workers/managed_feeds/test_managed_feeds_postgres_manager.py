import datetime
import json
from io import BytesIO
from operator import itemgetter

from freezegun import freeze_time
from mock import call

from model.enums import EventStatus
from model.pi.models import SyncAsEvent, SyncFeedsEvent, InterpolateEvent, BackfillEvent, FeedGroup, Feed, \
    SubscribeEvent, UnsubscribeEvent, Event, Settings


def test_get_events_with_page_size(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        SyncAsEvent(
            id='1',
            error_message='Fail',
            status=EventStatus.failure,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 4),
            s3_bucket='bucket',
            s3_key='key',
            database='database'
        ),
        SyncFeedsEvent(
            id='2',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 3),
            s3_bucket='bucket',
            s3_key='key'
        ),
        InterpolateEvent(
            id='3',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 2),
            name='name',
            number_of_feeds=2
        ),
        BackfillEvent(
            id='4',
            status=EventStatus.success,
            update_timestamp=datetime.datetime(2017, 1, 1),
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='3',
            feeds=['point1', 'point2'],
            status=EventStatus.success
        ),
        FeedGroup(
            id='0',
            event_id='4',
            feeds=['point1', 'point2'],
            status=EventStatus.success
        )
    ])

    result = managed_feeds_postgres_manager.get_events(page=0, page_size=3)

    assert result == {
        'events': [
            {
                'database': 'database',
                'error_message': 'Fail',
                'id': '1',
                's3_bucket': 'bucket',
                's3_key': 'key',
                'status': EventStatus.failure,
                'type': 'sync_as',
                'start_timestamp': datetime.datetime(2017, 1, 1),
                'update_timestamp': datetime.datetime(2017, 1, 4),
                'username': None
            },
            {
                'error_message': None,
                'id': '2',
                's3_bucket': 'bucket',
                's3_key': 'key',
                'status': EventStatus.success,
                'type': 'sync_feeds',
                'start_timestamp': datetime.datetime(2017, 1, 1),
                'update_timestamp': datetime.datetime(2017, 1, 3),
                'username': None
            },
            {
                'error_message': None,
                'name': 'name',
                'id': '3',
                'status': EventStatus.success,
                'number_of_feeds': 2,
                'type': 'interpolate',
                'start_timestamp': datetime.datetime(2017, 1, 1),
                'update_timestamp': datetime.datetime(2017, 1, 2),
                'username': None
            }
        ],
        'total_count': 4
    }


def test_get_events_with_status(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        SyncAsEvent(
            id='1',
            error_message='Fail',
            status=EventStatus.failure,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 4),
            s3_bucket='bucket',
            s3_key='key',
            database='database'
        ),
        SyncFeedsEvent(
            id='2',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 3),
            s3_bucket='bucket',
            s3_key='key'
        ),
        InterpolateEvent(
            id='3',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 2),
            name='name',
            number_of_feeds=2
        ),
        BackfillEvent(
            id='4',
            status=EventStatus.success,
            update_timestamp=datetime.datetime(2017, 1, 1),
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='3',
            feeds=['point1', 'point2'],
            status=EventStatus.success
        ),
        FeedGroup(
            id='0',
            event_id='4',
            feeds=['point1', 'point2'],
            status=EventStatus.success
        )
    ])

    result = managed_feeds_postgres_manager.get_events(status='failure')

    assert result == {
        'events': [
            {
                'database': 'database',
                'error_message': 'Fail',
                'id': '1',
                's3_bucket': 'bucket',
                's3_key': 'key',
                'status': EventStatus.failure,
                'type': 'sync_as',
                'start_timestamp': datetime.datetime(2017, 1, 1),
                'update_timestamp': datetime.datetime(2017, 1, 4),
                'username': None
            }
        ],
        'total_count': 1
    }


def test_get_events_with_type(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        SyncAsEvent(
            id='1',
            error_message='Fail',
            status=EventStatus.failure,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 4),
            s3_bucket='bucket',
            s3_key='key',
            database='database'
        ),
        SyncFeedsEvent(
            id='2',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 3),
            s3_bucket='bucket',
            s3_key='key'
        ),
        InterpolateEvent(
            id='3',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 2),
            name='name',
            number_of_feeds=2
        ),
        BackfillEvent(
            id='4',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 1),
            name='backfill event',
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='3',
            feeds=['point1', 'point2'],
            status=EventStatus.success
        ),
        FeedGroup(
            id='0',
            event_id='4',
            feeds=['point1', 'point2'],
            status=EventStatus.success
        )
    ])

    result = managed_feeds_postgres_manager.get_events(type='backfill')

    assert result == {
        'events': [
            {
                'name': 'backfill event',
                'id': '4',
                'number_of_feeds': 2,
                'status': EventStatus.success,
                'error_message': None,
                'type': 'backfill',
                'start_timestamp': datetime.datetime(2017, 1, 1),
                'update_timestamp': datetime.datetime(2017, 1, 1),
                'username': None
            }
        ],
        'total_count': 1
    }


def test_get_events_with_time_range(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        SyncAsEvent(
            id='1',
            error_message='Fail',
            status=EventStatus.failure,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 4),
            s3_bucket='bucket',
            s3_key='key',
            database='database'
        ),
        SyncFeedsEvent(
            id='2',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 3),
            s3_bucket='bucket',
            s3_key='key'
        ),
        InterpolateEvent(
            id='3',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 2),
            name='name',
            number_of_feeds=2
        ),
        BackfillEvent(
            id='4',
            status=EventStatus.success,
            start_timestamp=datetime.datetime(2017, 1, 1),
            update_timestamp=datetime.datetime(2017, 1, 1),
            name='backfill event',
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='3',
            feeds=['point1', 'point2'],
            status=EventStatus.success
        ),
        FeedGroup(
            id='0',
            event_id='4',
            feeds=['point1', 'point2'],
            status=EventStatus.success
        )
    ])

    result = managed_feeds_postgres_manager.get_events(
        timestamp_from=datetime.datetime(2017, 1, 2),
        timestamp_to=datetime.datetime(2017, 1, 3)
    )

    assert result == {
        'events': [
            {
                'error_message': None,
                'id': '2',
                's3_bucket': 'bucket',
                's3_key': 'key',
                'status': EventStatus.success,
                'type': 'sync_feeds',
                'start_timestamp': datetime.datetime(2017, 1, 1),
                'update_timestamp': datetime.datetime(2017, 1, 3),
                'username': None
            },
            {
                'name': 'name',
                'id': '3',
                'status': EventStatus.success,
                'number_of_feeds': 2,
                'type': 'interpolate',
                'error_message': None,
                'start_timestamp': datetime.datetime(2017, 1, 1),
                'update_timestamp': datetime.datetime(2017, 1, 2),
                'username': None
            }
        ],
        'total_count': 2
    }


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


def test_get_feeds(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        Feed(
            name='point1',
            subscription_status={'archive': 'subscribed', 'snapshot': 'unsubscribed'},
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        Feed(
            name='point2',
            subscription_status={'archive': 'pending', 'snapshot': 'pending'},
            update_timestamp=datetime.datetime(2017, 1, 2)
        ),
        Feed(
            name='point3',
            subscription_status={'archive': 'unsubscribed', 'snapshot': 'unsubscribed'},
            update_timestamp=datetime.datetime(2017, 1, 3)
        )
    ])

    points_data = managed_feeds_postgres_manager.get_feeds()
    points_data['feeds'] = sorted(points_data['feeds'], key=itemgetter('name'))

    assert points_data == {
        'feeds': [
            {
                'name': 'point1',
                'subscription_status': {'archive': 'subscribed', 'snapshot': 'unsubscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            },
            {
                'name': 'point2',
                'subscription_status': {'archive': 'pending', 'snapshot': 'pending'},
                'update_timestamp': datetime.datetime(2017, 1, 2, 0, 0)
            },
            {
                'name': 'point3',
                'subscription_status': {'archive': 'unsubscribed', 'snapshot': 'unsubscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 3, 0, 0)
            }
        ],
        'total_count': 3
    }


def test_get_feeds_with_pagination(managed_feeds_postgres_manager, postgres_session):
    for i in range(10):
        feed = Feed(
            name='point{}'.format(i),
            subscription_status={'archive': 'subscribed', 'snapshot': 'unsubscribed'},
            update_timestamp=datetime.datetime(2017, 1, 1)
        )
        postgres_session.add(feed)

    points_data = managed_feeds_postgres_manager.get_feeds(page=2, page_size=2)
    points_data['feeds'] = sorted(points_data['feeds'], key=itemgetter('name'))

    assert points_data == {
        'feeds': [
            {
                'name': 'point4',
                'subscription_status': {'archive': 'subscribed', 'snapshot': 'unsubscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            },
            {
                'name': 'point5',
                'subscription_status': {'archive': 'subscribed', 'snapshot': 'unsubscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            }
        ],
        'total_count': 10
    }


def test_search_feeds_with_query(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        Feed(
            name='name-test-name',
            subscription_status={'archive': 'subscribed', 'snapshot': 'unsubscribed'},
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        Feed(
            name='test-test-test',
            subscription_status={'archive': 'pending', 'snapshot': 'unsubscribed'},
            update_timestamp=datetime.datetime(2017, 1, 2)
        )
    ])

    points_data = managed_feeds_postgres_manager.search_feeds(pattern='name-*-name')

    assert points_data == {
        'feeds': [
            {
                'name': 'name-test-name',
                'subscription_status': {'archive': 'subscribed', 'snapshot': 'unsubscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            }
        ],
        'total_count': 1,
        'subscribed_count': 1,
        'unsubscribed_count': 0,
        'pending_count': 0
    }


def test_search_feeds_using_regex(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        Feed(
            name='test1',
            subscription_status={'archive': 'subscribed', 'snapshot': 'unsubscribed'},
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        Feed(
            name='Test12',
            subscription_status={'archive': 'pending', 'snapshot': 'unsubscribed'},
            update_timestamp=datetime.datetime(2017, 1, 2)
        )
    ])

    points_data = managed_feeds_postgres_manager.search_feeds(
        pattern='[A-Z]{1}[a-z]?[0-9]?',
        use_regex=True
    )

    assert points_data == {
        'feeds': [
            {
                'name': 'Test12',
                'subscription_status': {'archive': 'pending', 'snapshot': 'unsubscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 2, 0, 0)
            }
        ],
        'total_count': 1,
        'subscribed_count': 0,
        'unsubscribed_count': 0,
        'pending_count': 1
    }


def test_search_feeds_with_feeds(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        Feed(
            name='name1',
            subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'},
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        Feed(
            name='name2',
            subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'},
            update_timestamp=datetime.datetime(2017, 1, 2)
        ),
        Feed(
            name='name3',
            subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'},
            update_timestamp=datetime.datetime(2017, 1, 3)
        )
    ])

    points_data = managed_feeds_postgres_manager.search_feeds(feeds=['name1', 'name3'])
    points_data['feeds'] = sorted(points_data['feeds'], key=itemgetter('name'))

    assert points_data == {
        'feeds': [
            {
                'name': 'name1',
                'subscription_status': {'archive': 'subscribed', 'snapshot': 'subscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            },
            {
                'name': 'name3',
                'subscription_status': {'archive': 'subscribed', 'snapshot': 'subscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 3, 0, 0)
            }
        ],
        'total_count': 2,
        'subscribed_count': 2,
        'unsubscribed_count': 0,
        'pending_count': 0
    }


def test_search_feeds_with_status(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        Feed(
            name='name1',
            subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'},
            update_timestamp=datetime.datetime(2017, 1, 1)
        ),
        Feed(
            name='name2',
            subscription_status={'archive': 'pending', 'snapshot': 'pending'},
            update_timestamp=datetime.datetime(2017, 1, 2)
        ),
        Feed(
            name='name3',
            subscription_status={'archive': 'unsubscribed', 'snapshot': 'unsubscribed'},
            update_timestamp=datetime.datetime(2017, 1, 3)
        )
    ])

    points_data = managed_feeds_postgres_manager.search_feeds(status='subscribed')

    assert points_data == {
        'feeds': [
            {
                'name': 'name1',
                'subscription_status': {'archive': 'subscribed', 'snapshot': 'subscribed'},
                'update_timestamp': datetime.datetime(2017, 1, 1, 0, 0)
            }
        ],
        'total_count': 1,
        'subscribed_count': 1,
        'unsubscribed_count': 0,
        'pending_count': 0
    }


@freeze_time('2016-01-02 11:12:13')
def test_send_subscribe_request(managed_feeds_postgres_manager, subscription_queue, sqs_uuid4, postgres_session):
    postgres_session.add_all([
        Feed(name='point1'),
        Feed(name='point2'),
        Settings(name='feed_group_size', value='1000')
    ])

    def get_uuid():
        uuid_iter = iter(range(1000))

        def get_uuid_inner():
            return str(next(uuid_iter))
        return get_uuid_inner

    sqs_uuid4.side_effect = get_uuid()

    managed_feeds_postgres_manager.send_subscribe_request(['point1'])

    points = postgres_session.query(Feed).filter(Feed.name == 'point1')
    event = postgres_session.query(Event).get('0')

    assert all(point.subscription_status['archive'] == 'pending' for point in points)
    assert all(point.subscription_status['snapshot'] == 'pending' for point in points)
    assert event.type == 'subscribe'
    assert event.status == EventStatus.pending
    assert len(event.feed_groups) == 1

    assert subscription_queue.messages == [
        {
            'id': '0|0',
            'action': 'subscribe',
            'created_at': '2016-01-02T11:12:13',
            'payload': {'feeds': ['point1'], 'data_source': 'archive'}
        },
        {
            'id': '1|0',
            'action': 'subscribe',
            'created_at': '2016-01-02T11:12:13',
            'payload': {'feeds': ['point1'], 'data_source': 'snapshot'}
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_subscribe_request_with_success(managed_feeds_postgres_manager, postgres_session, iot_service):
    postgres_session.add_all([
        Feed(name='point1'),
        Feed(name='point2'),
        SubscribeEvent(
            id='1',
            status=EventStatus.pending,
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='1',
            feeds=['point1', 'point2'],
            status=EventStatus.pending
        ),
        FeedGroup(
            id='1',
            event_id='1',
            feeds=['point3', 'point4'],
            status=EventStatus.success
        )
    ])
    payload = {'feeds': ['point1', 'point2'], 'data_source': 'snapshot'}

    managed_feeds_postgres_manager.handle_subscribe_request('1|0', payload)

    points = postgres_session.query(Feed).all()
    event = postgres_session.query(Event).get('1')

    assert all(point.subscription_status['archive'] == 'unsubscribed' for point in points)
    assert all(point.subscription_status['snapshot'] == 'subscribed' for point in points)
    assert event.status == EventStatus.success
    assert iot_service.iot_client.create_thing.has_calls([call(thingName='point1'), call(thingName='point2')])


@freeze_time('2016-01-02 11:12:13')
def test_handle_subscribe_request_with_failure(managed_feeds_postgres_manager, postgres_session, iot_service):
    postgres_session.add_all([
        Feed(name='point1'),
        Feed(name='point2'),
        Feed(name='point3'),
        Feed(name='point4'),
        SubscribeEvent(
            id='1',
            status=EventStatus.pending,
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='1',
            feeds=['point1', 'point2'],
            status=EventStatus.pending
        ),
        FeedGroup(
            id='1',
            event_id='1',
            feeds=['point3', 'point4'],
            status=EventStatus.pending
        )
    ])
    payload = {'feeds': ['point1', 'point2'], 'data_source': 'snapshot'}

    managed_feeds_postgres_manager.handle_subscribe_request('1|0', payload)
    managed_feeds_postgres_manager.handle_subscribe_request('1|1', {**payload, 'error_message': 'error'})

    event = postgres_session.query(Event).get('1')

    assert event.status == EventStatus.failure


@freeze_time('2016-01-02 11:12:13')
def test_send_unsubscribe_request(managed_feeds_postgres_manager, subscription_queue, sqs_uuid4, postgres_session):
    postgres_session.add_all([
        Feed(name='point1', subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'}),
        Settings(name='feed_group_size', value='1000')
    ])

    def get_uuid():
        uuid_iter = iter(range(1000))

        def get_uuid_inner():
            return str(next(uuid_iter))
        return get_uuid_inner

    sqs_uuid4.side_effect = get_uuid()

    managed_feeds_postgres_manager.send_unsubscribe_request(['point1'])

    feeds = postgres_session.query(Feed).filter(Feed.name == 'point1')
    event = postgres_session.query(Event).get('0')

    assert all(feed.subscription_status['archive'] == 'pending' for feed in feeds)
    # assert sorted(event.feeds) == ['point1']
    assert event.type == 'unsubscribe'
    assert event.status == EventStatus.pending

    assert subscription_queue.messages == [
        {
            'id': '0|0',
            'action': 'unsubscribe',
            'created_at': '2016-01-02T11:12:13',
            'payload': {'feeds': ['point1'], 'data_source': 'archive'}
        },
        {
            'id': '1|0',
            'action': 'unsubscribe',
            'created_at': '2016-01-02T11:12:13',
            'payload': {'feeds': ['point1'], 'data_source': 'snapshot'}
        }
    ]


@freeze_time('2016-01-02 11:12:13')
def test_handle_unsubscribe_request(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        Feed(name='point1', subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'}),
        Feed(name='point2', subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'}),
        UnsubscribeEvent(
            id='1',
            status=EventStatus.pending,
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='1',
            feeds=['point1', 'point2'],
            status=EventStatus.pending
        )
    ])
    payload = {'feeds': ['point1', 'point2'], 'data_source': 'archive'}

    managed_feeds_postgres_manager.handle_unsubscribe_request('1|0', payload)

    feeds = postgres_session.query(Feed).all()
    event = postgres_session.query(Event).get('1')

    assert all(feed.subscription_status['archive'] == 'unsubscribed' for feed in feeds)
    assert event.status == EventStatus.success


@freeze_time('2016-01-02 11:12:13')
def test_handle_failed_unsubscribe_request(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        Feed(name='point1', subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'}),
        Feed(name='point2', subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'}),
        UnsubscribeEvent(
            id='1',
            status=EventStatus.pending,
            number_of_feeds=2
        ),
        FeedGroup(
            id='0',
            event_id='1',
            feeds=['point1', 'point2'],
            status=EventStatus.pending
        )
    ])
    payload = {'feeds': ['point1'], 'data_source': 'archive', 'error_message': 'point2 failed'}

    managed_feeds_postgres_manager.handle_unsubscribe_request('1|0', payload)

    point1 = postgres_session.query(Feed).get('point1')
    point2 = postgres_session.query(Feed).get('point2')
    event = postgres_session.query(Event).get('1')

    assert point1.subscription_status['archive'] == 'unsubscribed'
    assert point2.subscription_status['archive'] == 'subscribed'
    assert point1.subscription_status['snapshot'] == 'subscribed'
    assert point2.subscription_status['snapshot'] == 'subscribed'
    assert event.status == EventStatus.failure


@freeze_time('2016-01-02 11:12:13')
def test_send_sync_feeds_request(managed_feeds_postgres_manager, incoming_queue, sqs_uuid4, postgres_session):
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_sync_feeds_request('bucket')

    event = postgres_session.query(Event).get('1')

    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'sync_feeds',
            'created_at': '2016-01-02T11:12:13',
            'payload': {
                's3_bucket': 'bucket',
                's3_key': 'feeds_sync/20160102_111213/feeds.json'
            }
        }
    ]

    assert event.type == 'sync_feeds'
    assert event.status == EventStatus.pending
    assert event.s3_bucket == 'bucket'
    assert event.s3_key == 'feeds_sync/20160102_111213/feeds.json'


@freeze_time('2017-01-02 11:12:13')
def test_handle_sync_feeds(managed_feeds_postgres_manager, postgres_session, s3_resource, bucket_name):
    postgres_session.add_all([
        Feed(name='point1', subscription_status={'archive': 'pending', 'snapshot': 'pending'}),
        Feed(name='point2', subscription_status={'archive': 'pending', 'snapshot': 'pending'}),
        Feed(name='point3', subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'}),
        Feed(name='point4', subscription_status={'archive': 'subscribed', 'snapshot': 'subscribed'}),
    ])
    postgres_session.add(
        SyncFeedsEvent(id='1', status=EventStatus.pending, s3_bucket=bucket_name, s3_key='feeds.json')
    )
    s3_resource.Bucket(bucket_name).upload_fileobj(
        BytesIO(b'["point1","point3","point5"]'),
        'feeds.json'
    )
    payload = {}
    managed_feeds_postgres_manager.handle_sync_feeds('1', payload)

    points = postgres_session.query(Feed).all()
    point1 = postgres_session.query(Feed).get('point1')
    point3 = postgres_session.query(Feed).get('point3')
    point5 = postgres_session.query(Feed).get('point5')
    event = postgres_session.query(Event).get('1')

    assert len(points) == 3
    assert point1.subscription_status['archive'] == 'pending'
    assert point3.subscription_status['archive'] == 'subscribed'
    assert point5.subscription_status['archive'] == 'unsubscribed'
    assert point1.subscription_status['snapshot'] == 'pending'
    assert point3.subscription_status['snapshot'] == 'subscribed'
    assert point5.subscription_status['snapshot'] == 'unsubscribed'
    assert event.status == EventStatus.success


@freeze_time('2016-01-02 11:12:13')
def test_send_sync_as_request(managed_feeds_postgres_manager, incoming_queue, postgres_session, sqs_uuid4):
    sqs_uuid4.return_value = '1'

    managed_feeds_postgres_manager.send_sync_as_request('bucket', 'database')

    event = postgres_session.query(Event).get('1')

    assert incoming_queue.messages == [
        {
            'id': '1',
            'action': 'sync_as',
            'created_at': '2016-01-02T11:12:13',
            'payload': {
                'database': 'database',
                's3_bucket': 'bucket',
                's3_key': 'as_structure_sync/database/20160102_111213/as_structure.json'
            }
        }
    ]

    assert event.type == 'sync_as'
    assert event.status == EventStatus.pending
    assert event.s3_bucket == 'bucket'
    assert event.s3_key == 'as_structure_sync/database/20160102_111213/as_structure.json'
    assert event.database == 'database'


@freeze_time('2016-01-02 11:12:13')
def test_handle_sync_as(managed_feeds_postgres_manager, postgres_session, s3_resource, bucket_name):
    managed_feeds_postgres_manager._make_unique_s3_key = lambda *args, **kwargs: 'as_structure.json'
    msg_id = managed_feeds_postgres_manager.send_sync_as_request(bucket_name, 'NuGreen')
    as_structure = {
        "name": "NuGreen",
        "path": "\\\\EC2AMAZ-0EE3VGR\\NuGreen",
        "description": None,
        "template": None,
        "categories": None,
        "attributes": None,
        "assets": []
    }
    s3_resource.Bucket(bucket_name).upload_fileobj(
        BytesIO(json.dumps(as_structure).encode()),
        'as_structure.json'
    )
    payload = {}

    managed_feeds_postgres_manager.handle_sync_as(msg_id, payload)

    event = postgres_session.query(Event).get(msg_id)

    assert event.status == EventStatus.success


@freeze_time('2016-01-02 11:12:13')
def test_send_backfill_request(managed_feeds_postgres_manager, postgres_session, backfill_queue, sqs_uuid4):
    sqs_uuid4.return_value = '1'
    postgres_session.add_all([
        Settings(name='time_window_days', value='1'),
        Settings(name='feed_group_size', value='1000'),
    ])

    managed_feeds_postgres_manager.send_backfill_request(
        query_syntax=False,
        feeds=['point1'],
        request_from='2016-01-02T11:12:13.000Z',
        request_to='2016-01-02T11:12:13.000Z',
        name='name'
    )

    event = postgres_session.query(Event).get('1')

    assert backfill_queue.messages == [
        {
            'id': '1|0',
            'action': 'backfill',
            'created_at': '2016-01-02T11:12:13',
            'payload': {
                'feeds': ['point1'],
                'from': '2016-01-02T11:12:13.000000Z',
                'to': '2016-01-02T11:12:13.000000Z',
                'use_query_syntax': False,
                'backfill_name': 'name'
            }
        }
    ]

    assert event.status == EventStatus.pending
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_send_backfill_request_with_query(managed_feeds_postgres_manager, backfill_queue, postgres_session, sqs_uuid4):
    sqs_uuid4.return_value = '1'
    postgres_session.add_all([
        Settings(name='time_window_days', value='1'),
        Settings(name='feed_group_size', value='1000'),
    ])

    managed_feeds_postgres_manager.send_backfill_request(
        query_syntax=True,
        feeds=['point1', 'point2'],
        query='-1d',
        name='name'
    )

    event = postgres_session.query(Event).get('1')

    assert backfill_queue.messages == [
        {
            'id': '1|0',
            'action': 'backfill',
            'created_at': '2016-01-02T11:12:13',
            'payload': {
                'feeds': ['point1', 'point2'],
                'query': '-1d',
                'use_query_syntax': True,
                'backfill_name': 'name'
            }
        }
    ]

    assert event.status == EventStatus.pending
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_handle_backfill(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add(
        BackfillEvent(id='1', number_of_feeds=2, status=EventStatus.pending, name='name'),
        FeedGroup(id='0', event_id='1', feeds=['point1'], status=EventStatus.pending)
    )

    managed_feeds_postgres_manager.handle_backfill_status('1|0', {})

    event = postgres_session.query(Event).get('1')

    assert event.status == EventStatus.success
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_handle_backfill_failed(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        BackfillEvent(id='1', number_of_feeds=1, status=EventStatus.pending, name='name'),
        FeedGroup(id='0', event_id='1', feeds=['point1'], status=EventStatus.pending)
    ])
    payload = {
        'failed_feeds': [{
            'feed': 'point1',
            'error_message': 'fail'
        }]
    }

    managed_feeds_postgres_manager.handle_backfill_status('1|0', payload)

    event = postgres_session.query(Event).get('1')
    feed_group = postgres_session.query(FeedGroup).get((0, '1'))

    assert event.status == EventStatus.failure
    assert event.name == 'name'
    assert feed_group.error_message == "{'point1': 'fail'}"


@freeze_time('2016-01-02 11:12:13')
def test_send_interpolate_request(managed_feeds_postgres_manager, interpolation_queue, postgres_session, sqs_uuid4):
    sqs_uuid4.return_value = '1'
    postgres_session.add_all([
        Settings(name='time_window_days', value='1'),
        Settings(name='feed_group_size', value='1000'),
    ])

    managed_feeds_postgres_manager.send_interpolate_request(
        query_syntax=False,
        feeds=['point1', 'point2'],
        interval=1,
        interval_unit='seconds',
        request_from='2016-01-02T11:12:13.000Z',
        request_to='2016-01-02T11:12:13.000Z',
        name='name'
    )

    event = postgres_session.query(Event).get('1')

    assert interpolation_queue.messages == [
        {
            "id": "1|0",
            "action": 'interpolate',
            'created_at': '2016-01-02T11:12:13',
            "payload": {
                "feeds": ['point1', 'point2'],
                'from': '2016-01-02T11:12:13.000000Z',
                'to': '2016-01-02T11:12:13.000000Z',
                'use_date_query_syntax': False,
                'interval_seconds': 1,
                'interpolation_name': 'name'
            }
        }
    ]

    assert event.status == EventStatus.pending
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_send_interpolate_request_with_query(managed_feeds_postgres_manager, interpolation_queue, postgres_session,
                                             sqs_uuid4):
    sqs_uuid4.return_value = '1'
    postgres_session.add_all([
        Settings(name='time_window_days', value='1'),
        Settings(name='feed_group_size', value='1000'),
    ])

    managed_feeds_postgres_manager.send_interpolate_request(
        query_syntax=True,
        feeds=['point1', 'point2'],
        interval=1,
        interval_unit='seconds',
        query='-1d',
        name='name'
    )

    event = postgres_session.query(Event).get('1')

    assert interpolation_queue.messages == [
        {
            "id": "1|0",
            "action": 'interpolate',
            'created_at': '2016-01-02T11:12:13',
            "payload": {
                "feeds": ['point1', 'point2'],
                'date_query': '-1d',
                'interval_seconds': 1,
                'use_date_query_syntax': True,
                'interpolation_name': 'name'
            }
        }
    ]

    assert event.status == EventStatus.pending
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_handle_interpolation(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        InterpolateEvent(id='1', number_of_feeds=2, status=EventStatus.pending, name='name'),
        FeedGroup(id='0', event_id='1', feeds=['point1'], status=EventStatus.pending)
    ])

    managed_feeds_postgres_manager.handle_interpolation_status('1|0', {})

    event = postgres_session.query(Event).get('1')

    assert event.status == EventStatus.success
    assert event.name == 'name'


@freeze_time('2016-01-02 11:12:13')
def test_handle_interpolation_with_failure(managed_feeds_postgres_manager, postgres_session):
    postgres_session.add_all([
        InterpolateEvent(id='1', number_of_feeds=1, status=EventStatus.pending, name='name'),
        FeedGroup(id='0', event_id='1', feeds=['point1'], status=EventStatus.pending)
    ])

    payload = {
        "failed_feeds": [
            {
                "feed": "point1",
                "error_message": "fail"
            }
        ]
    }

    managed_feeds_postgres_manager.handle_interpolation_status('1|0', payload)

    event = postgres_session.query(Event).get('1')
    feed_group = postgres_session.query(FeedGroup).get((0, '1'))

    assert event.status == EventStatus.failure
    assert event.name == 'name'
    assert feed_group.error_message == "{'point1': 'fail'}"


@freeze_time('2016-01-02 11:12:13')
def test_handle_event_failure(managed_feeds_postgres_manager, postgres_session):
    feed1 = Feed(
        name='feed1',
        subscription_status={'archive': 'pending', 'snapshot': 'pending'},
        update_timestamp=datetime.datetime(2017, 1, 1)
    )
    event = SubscribeEvent(
        id='1',
        type='subscribe',
        status='pending',
        start_timestamp=datetime.datetime(2017, 1, 1),
        update_timestamp=datetime.datetime(2017, 1, 1),
        number_of_feeds=1,
        data_source='archive'
    )
    feed_group = FeedGroup(
        id=0,
        event_id='1',
        feeds=['feed1'],
        status=EventStatus.pending
    )
    postgres_session.add_all([feed1, event, feed_group])

    event = managed_feeds_postgres_manager.get_events()['events'][0]
    managed_feeds_postgres_manager.handle_event_failure(event)

    events = managed_feeds_postgres_manager.get_events()['events']

    feeds = managed_feeds_postgres_manager.get_feeds()['feeds']

    feed_group = managed_feeds_postgres_manager.get_event_feed_groups(event['id'])['feed_groups'][0]

    assert events[0]['status'] == EventStatus.failure
    assert feed_group['status'] == EventStatus.failure
    assert feeds[0]['subscription_status']['archive'] == 'unknown'
    assert feeds[0]['subscription_status']['snapshot'] == 'pending'
