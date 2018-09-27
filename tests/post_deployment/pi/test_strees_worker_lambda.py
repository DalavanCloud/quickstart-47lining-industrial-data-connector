import json
import uuid
from datetime import date
from datetime import datetime, timedelta

import pytest
import requests

from tests.post_deployment.conftest import get_athena_info
from tests.post_deployment.helpers import get_default_sub_request, get_last_event_id, safe_list_get_id, \
    get_result_event, sync_feeds, get_structure, get_feeds, get_s3_objects_number, wait_for_s3_file, \
    wait_for_event_with_name, get_query_result, sync_structure, wait_for_reset, \
    subscribe_all, unsubscribe_all

SLEEP_TIME = 2


@pytest.mark.timeout(600)
def test_unsubscribe_all_feeds(base_api_url, headers):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    sync_feeds(base_api_url, headers)
    subscribe_all(base_api_url, headers)
    request = get_default_sub_request()
    url = f'{base_api_url}/feeds/unsubscribe'

    res = requests.request('POST', url, data=json.dumps(request), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 2, headers, 'unsubscribe', last_event_id)
    assert result == {'success'}


@pytest.mark.timeout(600)
def test_subscribe_all_feeds(base_api_url, headers, curated_bucket_name, s3_resource):
    paths = ['data/numeric', 'data/text']
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    sync_feeds(base_api_url, headers)
    unsubscribe_all(base_api_url, headers)
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)
    request = get_default_sub_request()
    url = f'{base_api_url}/feeds/subscribe'

    res = requests.request('POST', url, data=json.dumps(request), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 2, headers, 'subscribe', last_event_id)
    assert result == {'success'}
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'


@pytest.mark.timeout(800)
def test_reset_data(base_api_url, headers):
    sync_structure(base_api_url, headers)
    sync_feeds(base_api_url, headers)
    subscribe_all(base_api_url, headers)
    request = {'name': ''}
    url = f'{base_api_url}/feeds/reset'

    res = requests.request('POST', url, data=json.dumps(request), headers=headers)

    assert res.status_code == 200
    result = wait_for_reset(base_api_url, 2, headers)
    structure = get_structure(base_api_url, headers)['assets']
    feeds = get_feeds(base_api_url, headers)
    assert result == 'success'
    assert not structure
    assert not feeds


@pytest.mark.timeout(800)
def test_heavy_backfill(base_api_url, headers, athena_client, bucket_name, s3_resource, curated_bucket_name):
    number_of_feeds_to_backfill = 10
    paths = ['data/numeric', 'data/text']
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)
    url = f'{base_api_url}/feeds/backfill'
    athena_info = get_athena_info(base_api_url, headers)
    start_date = (datetime.utcnow() - timedelta(days=5)).replace(hour=0, minute=0, second=0, microsecond=0)
    backfill_name = f'test_backfill_{str(uuid.uuid1())[:10]}'
    from_time = f'{date.strftime(start_date, "%Y-%m-%dT%H:%M:%S.%fZ")}'
    to_time = f'{date.strftime(start_date + timedelta(days=1), "%Y-%m-%dT%H:%M:%S.%fZ")}'
    sync_feeds(base_api_url, headers)
    feeds_to_backfill = [name for name in get_feeds(base_api_url, headers)
                         if len(name) < 12][:number_of_feeds_to_backfill]
    request = {
        'feeds': feeds_to_backfill, 'name': backfill_name, 'syntax': False,
        'to': to_time, 'from': from_time, 'query': ''
    }

    res = requests.request('POST', url, data=json.dumps(request), headers=headers)

    assert res.status_code == 200
    event_status = wait_for_event_with_name(base_api_url, headers, backfill_name, 'backfill')
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'
    query_result = get_query_result(athena_client, athena_info, bucket_name, feeds_to_backfill, backfill_name)
    assert event_status['status'] == 'success'
    assert query_result == len(feeds_to_backfill)
