import datetime
import json
import time
from unittest.mock import Mock

import pytest
from flask import current_app

from model.pi.models import Feed
from tests.pre_deployment.assets.api.v1.utils import parse_response, copy_db_objects

feed_1 = Feed(name='feed1', subscription_status={'snapshot': 'unsubscribed', 'archive': 'unsubscribed'},
              update_timestamp=datetime.datetime(2017, 1, 1))
feed_2 = Feed(name='feed2', subscription_status={'snapshot': 'unsubscribed', 'archive': 'subscribed'},
              update_timestamp=datetime.datetime(2017, 1, 1))
feed_3 = Feed(name='feed3', subscription_status={'snapshot': 'subscribed', 'archive': 'subscribed'},
              update_timestamp=datetime.datetime(2017, 1, 1))
feed_4 = Feed(name='feed4', subscription_status={'snapshot': 'subscribed', 'archive': 'subscribed'},
              update_timestamp=datetime.datetime(2017, 1, 1))

feed_json_1 = {
    'name': 'feed1', 'subscription_status': {'snapshot': 'unsubscribed', 'archive': 'unsubscribed'},
    'update_timestamp': '2017-01-01T00:00:00'
}

feed_json_2 = {
    'name': 'feed2', 'subscription_status': {'snapshot': 'unsubscribed', 'archive': 'subscribed'},
    'update_timestamp': '2017-01-01T00:00:00'
}

feed_json_3 = {
    'name': 'feed3', 'subscription_status': {'snapshot': 'subscribed', 'archive': 'subscribed'},
    'update_timestamp': '2017-01-01T00:00:00'
}

feed_json_4 = {
    'name': 'feed4', 'subscription_status': {'snapshot': 'subscribed', 'archive': 'subscribed'},
    'update_timestamp': '2017-01-01T00:00:00'
}


@pytest.mark.parametrize("search_request,expected_response", [
    (
            {'page': 0, 'page_size': 10, 'query': '*1', 'feeds': None, 'status': 'all', 'use_regex': False},
            {'total_count': 1, 'subscribed_count': 0, 'unsubscribed_count': 1, 'pending_count': 0,
             'feeds': [feed_json_1]}
    ),
    (
            {'page': 0, 'page_size': 10, 'query': 'feed(1|2)', 'feeds': None, 'status': None, 'use_regex': True},
            {'total_count': 2, 'subscribed_count': 1, 'unsubscribed_count': 1, 'pending_count': 0,
             'feeds': [feed_json_1, feed_json_2]}
    ),
    (
            {'page': 0, 'page_size': 10, 'query': '', 'feeds': ['feed1', 'feed2'], 'status': 'subscribed',
             'use_regex': False},
            {'total_count': 1, 'subscribed_count': 1, 'unsubscribed_count': 0, 'pending_count': 0,
             'feeds': [feed_json_2]}
    ),
    (
            {'page': 0, 'page_size': 10, 'query': '', 'feeds': None, 'status': 'subscribed', 'use_regex': False},
            {'total_count': 3, 'subscribed_count': 3, 'unsubscribed_count': 0, 'pending_count': 0,
             'feeds': [feed_json_2, feed_json_3, feed_json_4]
             }
    ),
    (
            {'page': 0, 'page_size': 10, 'query': None, 'feeds': None, 'status': 'subscribed', 'use_regex': False},
            {'total_count': 3, 'subscribed_count': 3, 'unsubscribed_count': 0, 'pending_count': 0,
             'feeds': [feed_json_2, feed_json_3, feed_json_4]}
    ),
    (
            {'page': 0, 'page_size': 10, 'query': '', 'feeds': None, 'status': 'unsubscribed', 'use_regex': False},
            {'total_count': 2, 'subscribed_count': 1, 'unsubscribed_count': 1, 'pending_count': 0,
             'feeds': [feed_json_1, feed_json_2]}
    )
])
def test_feeds_search_pi(api_test_pi_client, postgres_session_pi, search_request, expected_response):
    postgres_session_pi.add_all(copy_db_objects([feed_1, feed_2, feed_3, feed_4]))
    response = parse_response(api_test_pi_client.post('/api/v1/feeds/search',
                                                      data=json.dumps(search_request),
                                                      content_type='application/json',
                                                      headers={'id_token': '', 'refresh_token': '',
                                                               'access_token': '', 'username': ''}))

    assert response.response == expected_response


def test_feeds_sync(api_test_client, managed_feeds_postgres_manager):
    managed_feeds_postgres_manager.send_sync_feeds_request = Mock()
    current_app.config['CURATED_DATASETS_BUCKET_NAME'] = 'bucket'

    response = parse_response(api_test_client.post('/api/v1/feeds/sync',
                                                   data={},
                                                   content_type='application/json',
                                                   headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                            'username': ''}))

    assert response.status_code == 200
    managed_feeds_postgres_manager.send_sync_feeds_request.assert_called_once()


def test_feeds_backfill(api_test_client, managed_feeds_postgres_manager):
    managed_feeds_postgres_manager.send_backfill_request = Mock()
    backfill_request = {
        'feeds': ['feed1'], 'syntax': '', 'from': '2017-01-01T00:00:00', 'to': '2017-01-01T00:00:00',
        'name': 'request', 'query': '', 'only_searched_feeds': False, 'filters': [], 'search_pattern': '',
        'search_status': ''
    }

    response = parse_response(api_test_client.post('api/v1/feeds/backfill',
                                                   data=json.dumps(backfill_request),
                                                   content_type='application/json',
                                                   headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                            'username': ''}))

    assert response.status_code == 200
    managed_feeds_postgres_manager.send_backfill_request.assert_called_once()


def test_feeds_interpolate(api_test_client, managed_feeds_postgres_manager):
    managed_feeds_postgres_manager.send_interpolate_request = Mock()
    interpolate_request = {
        'feeds': ['feed1'], 'syntax': '', 'from': '2017-01-01T00:00:00', 'to': '2017-01-01T00:00:00',
        'name': 'request', 'query': '', 'only_searched_feeds': False, 'filters': [], 'search_pattern': '',
        'search_status': '',
        'interval': 30, 'interval_unit': 'seconds'
    }

    response = parse_response(api_test_client.post('api/v1/feeds/interpolate',
                                                   data=json.dumps(interpolate_request),
                                                   content_type='application/json',
                                                   headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                            'username': ''}))

    assert response.status_code == 200
    managed_feeds_postgres_manager.send_interpolate_request.assert_called_once()


def test_feeds_subscribe(api_test_client, managed_feeds_postgres_manager):
    managed_feeds_postgres_manager.send_subscribe_request = Mock()
    subscribe_request = {
        'feeds': ['feed1'], 'name': 'request', 'data_source': 'archive', 'only_searched_feeds': False, 'filters': [],
        'search_pattern': '', 'search_status': ''
    }

    response = parse_response(api_test_client.post('api/v1/feeds/subscribe',
                                                   data=json.dumps(subscribe_request),
                                                   content_type='application/json',
                                                   headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                            'username': ''}))

    assert response.status_code == 200
    managed_feeds_postgres_manager.send_subscribe_request.assert_called_once()


def test_feeds_unsubscribe(api_test_client, managed_feeds_postgres_manager):
    managed_feeds_postgres_manager.send_unsubscribe_request = Mock()
    unsubscribe_request = {
        'feeds': ['feed1'], 'name': 'request', 'data_source': 'archive', 'only_searched_feeds': False, 'filters': [],
        'search_pattern': '', 'search_status': ''
    }

    response = parse_response(api_test_client.post('api/v1/feeds/unsubscribe',
                                                   data=json.dumps(unsubscribe_request),
                                                   content_type='application/json',
                                                   headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                            'username': ''}))

    assert response.status_code == 200
    managed_feeds_postgres_manager.send_unsubscribe_request.assert_called_once()


def test_feeds_reset_data(api_test_client, managed_feeds_postgres_manager):
    managed_feeds_postgres_manager.purge_queues = Mock()
    managed_feeds_postgres_manager.send_unsubscribe_request = Mock()
    managed_feeds_postgres_manager.reset_database = Mock()
    managed_feeds_postgres_manager.search_feeds = Mock()
    managed_feeds_postgres_manager.search_feeds.return_value = {'feeds': []}

    reset_data_request = {
        'name': ''
    }

    response = parse_response(api_test_client.post('api/v1/feeds/reset',
                                                   data=json.dumps(reset_data_request),
                                                   content_type='application/json',
                                                   headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                            'username': ''}))

    time.sleep(1)
    assert response.status_code == 200
    managed_feeds_postgres_manager.purge_queues.assert_called_once()
    managed_feeds_postgres_manager.send_unsubscribe_request.assert_called_once()
    managed_feeds_postgres_manager.reset_database.assert_called_once()
