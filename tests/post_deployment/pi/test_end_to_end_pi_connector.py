import json
import time
import uuid
from datetime import datetime, timedelta, date

import pytest
import requests

from tests.post_deployment.conftest import get_athena_info
from tests.post_deployment.helpers import sync_structure
from tests.post_deployment.helpers import unsubscribe_feed, get_default_sub_request, \
    get_last_event_id, safe_list_get_id, get_result_event, sync_feeds, get_structure, get_feeds, \
    get_s3_objects_number, subscribe_feed, wait_for_s3_file, wait_for_event_with_name, get_query_result


@pytest.mark.timeout(300)
def test_sync_structure(base_api_url, headers):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    url = f'{base_api_url}/structure/sync'

    res = requests.request('POST', url, data=json.dumps({}), headers=headers)

    assert res.status_code == 200
    result = get_result_event(base_api_url, 1, headers, 'sync_as', last_event_id)
    structure = get_structure(base_api_url, headers)
    assert structure['assets']
    assert result == {'success'}


@pytest.mark.timeout(300)
def test_sync_feeds(base_api_url, headers):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    url = f'{base_api_url}/feeds/sync'

    requests.request('POST', url, data=json.dumps({}), headers=headers)

    result = get_result_event(base_api_url, 1, headers, 'sync_feeds', last_event_id)
    feeds = get_feeds(base_api_url, headers)
    assert feeds
    assert result == {'success'}


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


@pytest.mark.timeout(600)
def test_subscribe_feed(base_api_url, headers, curated_bucket_name, s3_resource):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    paths = ['data/numeric', 'data/text']
    sync_feeds(base_api_url, headers)
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


@pytest.mark.timeout(600)
def test_backfill(base_api_url, headers, athena_client, bucket_name, s3_resource, curated_bucket_name):
    number_of_feeds_to_backfill = 2
    paths = ['data/numeric', 'data/text']
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)
    url = f'{base_api_url}/feeds/backfill'
    athena_info = get_athena_info(base_api_url, headers)
    from_date, to_date = get_start_and_finish_date(5)
    backfill_name = f'test_backfill_{str(uuid.uuid1())[:10]}'
    sync_feeds(base_api_url, headers)
    feeds_to_backfill = [name for name in get_feeds(base_api_url, headers)][:number_of_feeds_to_backfill]
    request = {
        'feeds': feeds_to_backfill, 'name': backfill_name, 'syntax': False,
        'to': to_date, 'from': from_date, 'query': ''
    }

    requests.request('POST', url, data=json.dumps(request), headers=headers)

    event_status = wait_for_event_with_name(base_api_url, headers, backfill_name, 'backfill')
    assert event_status['status'] == 'success'
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'
    query_result = get_query_result(athena_client, athena_info, bucket_name, feeds_to_backfill, backfill_name)
    assert query_result == len(feeds_to_backfill)


@pytest.mark.timeout(600)
def test_interpolate(base_api_url, headers, athena_client, bucket_name, s3_resource, curated_bucket_name):
    number_of_feeds_to_interpolate = 2
    paths = ['data/numeric', 'data/text']
    s3_objects_starting_number = get_s3_objects_number(curated_bucket_name, s3_resource, paths)
    url = f'{base_api_url}/feeds/interpolate'
    athena_info = get_athena_info(base_api_url, headers)
    interpolate_name = f'test_interpolate_{str(uuid.uuid1())[:10]}'
    from_date, to_date = get_start_and_finish_date(5*60)
    feeds_to_interpolate = [name for name in get_feeds(base_api_url, headers)][:number_of_feeds_to_interpolate]
    request = {
        'feeds': feeds_to_interpolate, 'name': interpolate_name, 'syntax': False,
        'to': to_date, 'from': from_date, 'query': '', 'interval': '3600', 'interval_unit': 'seconds'
    }

    requests.request('POST', url, data=json.dumps(request), headers=headers)

    event_status = wait_for_event_with_name(base_api_url, headers, interpolate_name, 'interpolate')
    assert event_status['status'] == 'success'
    s3_result = wait_for_s3_file(curated_bucket_name, s3_resource, paths, s3_objects_starting_number)
    assert s3_result['status'] == 'success'
    query_result = get_query_result(
        athena_client, athena_info,
        bucket_name, feeds_to_interpolate, interpolate_name)
    assert query_result == len(feeds_to_interpolate)


@pytest.mark.timeout(600)
def test_sync_with_join(base_api_url, headers, athena_client, bucket_name):
    sync_feeds(base_api_url, headers)
    sync_structure(base_api_url, headers)
    feeds = get_feeds(base_api_url, headers, 50)
    assert feeds
    subscribe_feed(base_api_url, headers, request={
        "feeds": feeds,
        "name": "",
        "data_source": "all"
    })
    athena_info = get_athena_info(base_api_url, headers)
    try_again_check_kinesis_data(10, athena_client, athena_info, bucket_name, feeds)

    res = get_feeds_query_result(athena_client, athena_info, bucket_name, feeds)

    asset_index = res[0]['Data'].index({'VarCharValue': 'asset'})
    assert asset_index
    assert [x['Data'][asset_index]['VarCharValue'] for x in res[1:]]
    assert [x['Data'][asset_index]['VarCharValue'] for x in res[1:]] != ['null']*len(res)


def try_again_check_kinesis_data(number_more_tries, athena_client, athena_info, bucket_name, feeds):
    if number_more_tries <= 0:
        return

    time.sleep(60)
    res = get_feeds_query_result(athena_client, athena_info, bucket_name, feeds)

    asset_index = res[0]['Data'].index({'VarCharValue': 'asset'})
    if not asset_index or not [x['Data'][asset_index]['VarCharValue'] for x in res[1:]] \
            or not [x['Data'][asset_index]['VarCharValue'] for x in res[1:]] != ['null'] * len(res):
        return try_again_check_kinesis_data(number_more_tries - 1, athena_client, athena_info, bucket_name, feeds)


def get_feeds_query_result(athena_client, athena_info, bucket_name, feeds):

    query = get_athena_query(feeds, athena_info)
    query_execution_id = athena_client.start_query_execution(
        QueryString=query,
        QueryExecutionContext={
            'Database': athena_info['database_name']
        },
        ResultConfiguration={
            'OutputLocation': f's3://{bucket_name}/'
        }
    )['QueryExecutionId']
    while True:
        stats = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        status = stats['QueryExecution']['Status']['State']
        if status in ['SUCCEEDED', 'FAILED', 'CANCELLED']:
            break
        time.sleep(0.2)
    assert status == 'SUCCEEDED'

    response = athena_client.get_query_results(
        QueryExecutionId=query_execution_id,
        MaxResults=100
    )
    return response['ResultSet']['Rows']


def get_athena_query(feeds, athena_info):
    timestamp = str(datetime.utcnow() - timedelta(minutes=1))[:-3]
    return f"""
        SELECT *
        FROM {athena_info['numeric_table_name']}
        WHERE timestamp > timestamp '{timestamp}'
        AND name in {tuple(feeds)}
        ORDER BY timestamp DESC;"""


def get_start_and_finish_date(duration_minutes):
    def formatted_date(date_):
        return f'{date.strftime(date_, "%Y-%m-%dT%H:%M:%S.%fZ")}'
    assert type(duration_minutes) == int
    start_date = (datetime.utcnow() - timedelta(days=5)).replace(hour=0, minute=0, second=0, microsecond=0)
    from_date = formatted_date(start_date)
    to_date = formatted_date(start_date + timedelta(minutes=duration_minutes))
    return from_date, to_date
