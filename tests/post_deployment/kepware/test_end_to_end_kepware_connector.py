import json

import pytest
import requests

from tests.post_deployment.helpers import get_result_event, get_last_event_id, safe_list_get_id, \
    get_s3_objects_number, get_structure, wait_for_s3_file, get_feeds, unsubscribe_feed, sync_feeds, \
    get_default_sub_request


@pytest.mark.timeout(600)
def test_sync_structure(base_api_url, headers, curated_bucket_name, s3_resource):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    url = f'{base_api_url}/structure/sync'
    paths = ['as_structure_sync']
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)

    res = requests.request('POST', url, data=json.dumps({}), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 1, headers, 'sync_as', last_event_id)
    assert result == {'success'}
    structure = get_structure(base_api_url, headers)
    assert structure['assets']
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'


@pytest.mark.timeout(600)
def test_sync_feeds(base_api_url, headers, curated_bucket_name, s3_resource):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    paths = ['feeds_sync']
    url = f'{base_api_url}/feeds/sync'
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)

    res = requests.request('POST', url, data=json.dumps({}), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 1, headers, 'sync_feeds', last_event_id)
    assert result == {'success'}
    feeds = get_feeds(base_api_url, headers)
    assert feeds
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'


@pytest.mark.timeout(120)
def test_subscribe_feed(base_api_url, headers, curated_bucket_name, s3_resource):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    sync_feeds(base_api_url, headers)
    paths = ['data/numeric', 'data/text']
    feeds = get_feeds(base_api_url, headers)
    assert feeds
    feed_to_subscribe = feeds[0]
    request = {
        "feeds": [feed_to_subscribe],
        "name": "",
        "data_source": "all"
    }
    unsubscribe_feed(base_api_url, headers, request)
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)
    request = get_default_sub_request()
    url = f'{base_api_url}/feeds/subscribe'

    res = requests.request('POST', url, data=json.dumps(request), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 2, headers, 'subscribe', last_event_id)
    assert result == {'success'}
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'
