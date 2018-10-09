import json

from model.pi.models import (SyncFeedsEvent, SyncAsEvent, BackfillEvent, InterpolateEvent, SubscribeEvent,
                             UnsubscribeEvent, EventStatus, FeedGroup)
import datetime

from tests.pre_deployment.assets.api.v1.utils import parse_response, copy_db_objects

update_timestamp = datetime.datetime(2017, 1, 1)

event_db_1 = SyncFeedsEvent(id='1', status=EventStatus.success, start_timestamp=datetime.datetime(2017, 1, 1),
                            s3_bucket='bucket', s3_key='key', update_timestamp=update_timestamp)
event_db_2 = SyncAsEvent(id='2', status=EventStatus.failure, start_timestamp=datetime.datetime(2017, 1, 2),
                         s3_bucket='bucket', s3_key='key', error_message='abc', update_timestamp=update_timestamp)
event_db_3 = BackfillEvent(id='3', status=EventStatus.pending, start_timestamp=datetime.datetime(2017, 1, 3),
                           name='name1', update_timestamp=update_timestamp)
event_db_4 = InterpolateEvent(id='4', status=EventStatus.failure, start_timestamp=datetime.datetime(2017, 1, 4),
                              name='name2', update_timestamp=update_timestamp)
event_db_5 = SubscribeEvent(id='5', status=EventStatus.pending, start_timestamp=datetime.datetime(2017, 1, 5),
                            data_source='archive', name='name3', update_timestamp=update_timestamp)
event_db_6 = UnsubscribeEvent(id='6', status=EventStatus.pending, start_timestamp=datetime.datetime(2017, 1, 6),
                              data_source='snapshot', name='name4', update_timestamp=update_timestamp)
feed_group_for_event_3 = FeedGroup(id=0, event_id='3', feeds=['f1'], status=EventStatus.pending)
feed_group_for_event_4 = FeedGroup(id=0, event_id='4', feeds=['f1'], status=EventStatus.failure, error_message='abc')
feed_group_for_event_5 = FeedGroup(id=0, event_id='5', feeds=['f1'], status=EventStatus.pending)
feed_group_for_event_6 = FeedGroup(id=0, event_id='6', feeds=['f1, f2, f3'], status=EventStatus.pending)
feed_group_2_for_event_6 = FeedGroup(id=1, event_id='6', feeds=['f4, f5, f6'], status=EventStatus.pending)


event_json_1 = {
    'data_source': None,
    'error_message': None,
    'id': '1',
    'name': None,
    'number_of_feeds': None,
    's3_bucket': 'bucket',
    's3_key': 'key',
    'start_timestamp': '2017-01-01T00:00:00',
    'status': 'success',
    'type': 'sync_feeds',
    'update_timestamp': '2017-01-01T00:00:00',
    'username': None
}
event_json_2 = {
    'data_source': None,
    'error_message': 'abc',
    'id': '2',
    'name': None,
    'number_of_feeds': None,
    's3_bucket': 'bucket',
    's3_key': 'key',
    'start_timestamp': '2017-01-02T00:00:00',
    'status': 'failure',
    'type': 'sync_as',
    'update_timestamp': '2017-01-01T00:00:00',
    'username': None
}
event_json_3 = {
    'data_source': None,
    'error_message': None,
    'id': '3',
    'name': 'name1',
    'number_of_feeds': None,
    's3_bucket': None,
    's3_key': None,
    'start_timestamp': '2017-01-03T00:00:00',
    'status': 'pending',
    'type': 'backfill',
    'update_timestamp': '2017-01-01T00:00:00',
    'username': None
}
event_json_4 = {
    'data_source': None,
    'error_message': None,
    'id': '4',
    'name': 'name2',
    'number_of_feeds': None,
    's3_bucket': None,
    's3_key': None,
    'start_timestamp': '2017-01-04T00:00:00',
    'status': 'failure',
    'type': 'interpolate',
    'update_timestamp': '2017-01-01T00:00:00',
    'username': None
}
event_json_5 = {
    'data_source': 'archive',
    'error_message': None,
    'id': '5',
    'name': 'name3',
    'number_of_feeds': None,
    's3_bucket': None,
    's3_key': None,
    'start_timestamp': '2017-01-05T00:00:00',
    'status': 'pending',
    'type': 'subscribe',
    'update_timestamp': '2017-01-01T00:00:00',
    'username': None
}
event_json_6 = {
    'data_source': 'snapshot',
    'error_message': None,
    'id': '6',
    'name': 'name4',
    'number_of_feeds': None,
    's3_bucket': None,
    's3_key': None,
    'start_timestamp': '2017-01-06T00:00:00',
    'status': 'pending',
    'type': 'unsubscribe',
    'update_timestamp': '2017-01-01T00:00:00',
    'username': None
}


def test_events_list(api_test_client, postgres_session):

    postgres_session.add_all(copy_db_objects([event_db_1,
                                              event_db_2,
                                              event_db_3,
                                              event_db_4,
                                              event_db_5,
                                              event_db_6,
                                              feed_group_for_event_3,
                                              feed_group_for_event_4,
                                              feed_group_for_event_5,
                                              feed_group_for_event_6,
                                              feed_group_2_for_event_6
                                              ]))

    request_1 = {'from': '2017-01-01T00:00:00',
                 'to': '2017-01-03T00:00:00',
                 'status': 'all',
                 'type': None,
                 'page': 0,
                 'page_size': 10
                 }
    request_2 = {'from': '2017-01-01T00:00:00',
                 'to': '2017-01-06T00:00:00',
                 'status': 'pending',
                 'type': None,
                 'page': 0,
                 'page_size': 10
                 }
    request_3 = {'from': '2017-01-01T00:00:00',
                 'to': '2017-01-06T00:00:00',
                 'status': 'failure',
                 'type': 'sync_as',
                 'page': 0,
                 'page_size': 10
                 }
    request_4 = {'from': '2017-01-01T00:00:00',
                 'to': '2017-01-06T00:00:00',
                 'status': 'all',
                 'type': 'subscribe',
                 'page': 0,
                 'page_size': 10
                 }
    request_5 = {'from': '2017-01-01T00:00:00',
                 'to': '2017-01-06T00:00:00',
                 'status': 'all',
                 'type': None,
                 'page': 0,
                 'page_size': 1
                 }

    response_1 = parse_response(api_test_client.post('/api/v1/events/list', data=json.dumps(request_1),
                                                     content_type='application/json',
                                                     headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                              'username': ''}))
    response_2 = parse_response(api_test_client.post('/api/v1/events/list', data=json.dumps(request_2),
                                                     content_type='application/json',
                                                     headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                              'username': ''}))
    response_3 = parse_response(api_test_client.post('/api/v1/events/list', data=json.dumps(request_3),
                                                     content_type='application/json',
                                                     headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                              'username': ''}))
    response_4 = parse_response(api_test_client.post('/api/v1/events/list', data=json.dumps(request_4),
                                                     content_type='application/json',
                                                     headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                              'username': ''}))
    response_5 = parse_response(api_test_client.post('/api/v1/events/list', data=json.dumps(request_5),
                                                     content_type='application/json',
                                                     headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                              'username': ''}))

    assert response_1.response == {'total_count': 6,
                                   'events': [event_json_1, event_json_2, event_json_3,
                                              event_json_4, event_json_5, event_json_6]}
    assert response_2.response == {'total_count': 3, 'events': [event_json_3, event_json_5, event_json_6]}
    assert response_3.response == {'total_count': 1, 'events': [event_json_2]}
    assert response_4.response == {'total_count': 1, 'events': [event_json_5]}
    assert len(response_5.response['events']) == 1
    assert response_5.response['total_count'] == 6


def test_get_event_feed_groups(api_test_client, postgres_session):
    postgres_session.add_all(copy_db_objects([
        event_db_6, feed_group_for_event_6, feed_group_2_for_event_6
    ]))

    response = parse_response(
        api_test_client.post(
            '/api/v1/events/6',
            data=json.dumps({}),
            content_type='application/json',
            headers={'id_token': '', 'refresh_token': '', 'access_token': '', 'username': ''}
        )
    )

    expected = {
        'total_count': 2,
        'feed_groups': [
            {'id': 0, 'event_id': '6', 'feeds': ['f1, f2, f3'], 'status': 'pending', 'error_message': None},
            {'id': 1, 'event_id': '6', 'feeds': ['f4, f5, f6'], 'status': 'pending', 'error_message': None}
        ]
    }
    assert response.response == expected
