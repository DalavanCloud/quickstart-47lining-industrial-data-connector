import json
import uuid
from datetime import datetime, timedelta

import pytest
import requests

from tests.post_deployment.conftest import get_athena_info
from tests.post_deployment.helpers import unsubscribe_feed, get_default_sub_request, \
    get_last_event_id, safe_list_get_id, get_result_event, sync_feeds, get_structure, get_feeds, \
    get_s3_objects_number, subscribe_feed, wait_for_s3_file, wait_for_event_with_name, get_query_result, \
    sync_structure, get_start_and_finish_date, subscribe_all, wait_for_reset


@pytest.mark.timeout(600)
def test_sync_structure(base_api_url, headers, curated_bucket_name, s3_resource):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    url = f'{base_api_url}/structure/sync'
    paths = ['as_structure_sync']
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)

    res = requests.request('POST', url, data=json.dumps({}), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 1, headers, 'sync_as', last_event_id)
    structure = get_structure(base_api_url, headers)
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'
    assert structure['assets']
    assert result == {'success'}


@pytest.mark.timeout(600)
def test_sync_feeds(base_api_url, headers, curated_bucket_name, s3_resource):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    paths = ['feeds_sync']
    url = f'{base_api_url}/feeds/sync'
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)

    res = requests.request('POST', url, data=json.dumps({}), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 1, headers, 'sync_feeds', last_event_id)
    feeds = get_feeds(base_api_url, headers)
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'
    assert feeds
    assert result == {'success'}


@pytest.mark.timeout(600)
def test_backfill(base_api_url, headers, athena_client, bucket_name, s3_resource, curated_bucket_name):
    # Only numeric subset is used here, there are no known feeds of type text
    paths = ['data/numeric']
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)
    url = f'{base_api_url}/feeds/backfill'
    athena_info = get_athena_info(base_api_url, headers)
    start_date = (datetime.utcnow() - timedelta(minutes=30)).replace(hour=0, minute=0, second=0, microsecond=0)
    from_date, to_date = get_start_and_finish_date(5, start_date)
    backfill_name = f'test_backfill_{str(uuid.uuid1())[:10]}'
    sync_feeds(base_api_url, headers)
    feeds = [name for name in get_feeds(base_api_url, headers)]
    request = {
        'feeds': feeds, 'name': backfill_name, 'syntax': False,
        'to': to_date, 'from': from_date, 'query': ''
    }

    requests.request('POST', url, data=json.dumps(request), headers=headers)

    event_status = wait_for_event_with_name(base_api_url, headers, backfill_name, 'backfill')
    assert event_status['status'] == 'success'
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'
    query_result = get_query_result(athena_client, athena_info, bucket_name, feeds, backfill_name)
    # Only a small subset of feeds have backfill data
    assert query_result > 0


@pytest.mark.timeout(120)
def test_unsubscribe_feed(base_api_url, headers):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    sync_feeds(base_api_url, headers)
    feeds = get_feeds(base_api_url, headers)
    assert feeds
    feed_to_unsubscribe = feeds[0]
    request = {
        "feeds": [feed_to_unsubscribe],
        "name": "",
        "data_source": "all"
    }
    subscribe_feed(base_api_url, headers, request)
    request = get_default_sub_request()
    url = f'{base_api_url}/feeds/unsubscribe'

    res = requests.request('POST', url, data=json.dumps(request), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 2, headers, 'unsubscribe', last_event_id)
    assert result == {'success'}


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
    url = f'{base_api_url}/feeds/unsubscribe'

    res = requests.request('POST', url, data=json.dumps(request), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 2, headers, 'unsubscribe', last_event_id)
    assert result == {'success'}
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'


@pytest.mark.timeout(800)
def test_reset_data(base_api_url, headers):
    sync_structure(base_api_url, headers)
    sync_feeds(base_api_url, headers)
    subscribe_all(base_api_url, headers, 1)
    request = {'name': ''}
    url = f'{base_api_url}/feeds/reset'

    res = requests.request('POST', url, data=json.dumps(request), headers=headers)

    assert res.status_code == 200
    result = wait_for_reset(base_api_url, 2, headers)
    structure = get_structure(base_api_url, headers)['assets']
    feeds = get_feeds(base_api_url, headers)
    assert result == {'status': 'success'}
    assert not structure
    assert not feeds
