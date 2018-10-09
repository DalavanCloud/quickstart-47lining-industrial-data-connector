import datetime
import json

import pytest

from model.wonderware.models import Feed
from tests.pre_deployment.assets.api.v1.utils import parse_response, copy_db_objects

feed_1 = Feed(name='feed1', subscription_status={'default': 'unsubscribed'},
              update_timestamp=datetime.datetime(2017, 1, 1))
feed_2 = Feed(name='feed2', subscription_status={'default': 'unsubscribed'},
              update_timestamp=datetime.datetime(2017, 1, 1))
feed_3 = Feed(name='feed3', subscription_status={'default': 'subscribed'},
              update_timestamp=datetime.datetime(2017, 1, 1))
feed_4 = Feed(name='feed4', subscription_status={'default': 'subscribed'},
              update_timestamp=datetime.datetime(2017, 1, 1))

feed_json_1 = {
    'name': 'feed1', 'subscription_status': {'default': 'unsubscribed'}, 'update_timestamp': '2017-01-01T00:00:00'
}

feed_json_2 = {
    'name': 'feed2', 'subscription_status': {'default': 'unsubscribed'}, 'update_timestamp': '2017-01-01T00:00:00'
}

feed_json_3 = {
    'name': 'feed3', 'subscription_status': {'default': 'subscribed'}, 'update_timestamp': '2017-01-01T00:00:00'
}

feed_json_4 = {
    'name': 'feed4', 'subscription_status': {'default': 'subscribed'}, 'update_timestamp': '2017-01-01T00:00:00'
}


@pytest.mark.parametrize("search_request,expected_response", [
    (
            {'page': 0, 'page_size': 10, 'query': '*1', 'feeds': None, 'status': 'all', 'use_regex': False},
            {'total_count': 1, 'subscribed_count': 0, 'unsubscribed_count': 1, 'pending_count': 0,
             'feeds': [feed_json_1]}
    ),
    (
            {'page': 0, 'page_size': 10, 'query': 'feed(1|2)', 'feeds': None, 'status': None, 'use_regex': True},
            {'total_count': 2, 'subscribed_count': 0, 'unsubscribed_count': 2, 'pending_count': 0,
             'feeds': [feed_json_1, feed_json_2]}
    ),
    (
            {'page': 0, 'page_size': 10, 'query': '', 'feeds': ['feed1', 'feed2'], 'status': 'subscribed',
             'use_regex': False},
            {'total_count': 0, 'subscribed_count': 0, 'unsubscribed_count': 0, 'pending_count': 0,
             'feeds': []}
    ),
    (
            {'page': 0, 'page_size': 10, 'query': '', 'feeds': None, 'status': 'subscribed', 'use_regex': False},
            {'total_count': 2, 'subscribed_count': 2, 'unsubscribed_count': 0, 'pending_count': 0,
             'feeds': [feed_json_3, feed_json_4]
             }
    )
])
def test_feeds_search_ww(api_test_wonderware_client, postgres_session_wonderware, search_request, expected_response):
    postgres_session_wonderware.add_all(copy_db_objects([feed_1, feed_2, feed_3, feed_4]))
    response = parse_response(api_test_wonderware_client.post('/api/v1/feeds/search',
                                                              data=json.dumps(search_request),
                                                              content_type='application/json',
                                                              headers={'id_token': '', 'refresh_token': '',
                                                                       'access_token': '', 'username': ''}))

    assert response.response == expected_response
