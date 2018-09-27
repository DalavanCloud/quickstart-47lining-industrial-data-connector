import json
import time
from datetime import datetime, timedelta, date

import requests

SLEEP_TIME = 5
TIMEOUT = 300


def get_last_event_id(base_api_url, headers):
    request = get_request_with_responses_number(1)
    url = f'{base_api_url}/events/list'
    return requests.request('POST', url, data=json.dumps(request), headers=headers).json()['events']


def get_request_with_responses_number(number_of_responses):
    return {
        'page': 0,
        'page_size': number_of_responses,
        'type': 'all',
        'status': 'all',
        'from': '',
        'to': ''
    }


def get_default_sub_request():
    return {
        'only_searched_feeds': True,
        'search_pattern': '',
        'search_status': 'all',
        'use_regex': False,
        'name': '',
        'data_source': 'all'
    }


def unsubscribe_feed(base_api_url, headers, request):
    manage_feed(base_api_url, headers, request, 'unsubscribe')


def subscribe_feed(base_api_url, headers, request):
    manage_feed(base_api_url, headers, request, 'subscribe')


def manage_feed(base_api_url, headers, request, action):
    assert action in ['subscribe', 'unsubscribe']
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    url = f'{base_api_url}/feeds/{action}'
    requests.request('POST', url, data=json.dumps(request), headers=headers)
    get_result_event(base_api_url, 1, headers, action, last_event_id)


def safe_list_get_id(l, idx, default):
    try:
        return l[idx]['id']
    except IndexError:
        return default


def get_result_event(base_api_url, number_of_responses, headers, action, last_event_id, custom_timeout=300):
    timeout = custom_timeout
    request = get_request_with_responses_number(number_of_responses)
    url = f'{base_api_url}/events/list'
    start = time.time()
    while True:
        request_result = requests.request('POST', url, data=json.dumps(request), headers=headers)
        res_events = request_result.json()['events']
        filtered_results = \
            [] if any([x['id'] == last_event_id for x in res_events]) \
            else list(filter(lambda x: x['type'] == action, res_events))

        results = set([res['status'] for res in filtered_results])

        if not filtered_results:
            time.sleep(SLEEP_TIME)
        elif 'pending' not in results:
            break
        elif time.time() - start > timeout:
            results = {'failed'}
            break
        else:
            time.sleep(SLEEP_TIME)
    return results


def get_structure(base_api_url, headers):
    url = f'{base_api_url}/structure/search'
    request = {'filters': [], 'page': 0, 'page_size': 5}
    result = requests.request('POST', url, data=json.dumps(request), headers=headers)
    return result.json()


def get_feeds(base_api_url, headers, number_of_feeds=10):
    url = f'{base_api_url}/feeds/search'
    request = {'page': 0, 'page_size': number_of_feeds, 'status': 'all', 'query': '', 'use_regex': False}
    result = requests.request('POST', url, data=json.dumps(request), headers=headers)
    return [feed['name'] for feed in result.json()['feeds']]


def wait_for_s3_file(curated_bucket_name, s3_resource, destination_paths, starting_numbers):
    start_time = time.time()
    while True:
        current_number_s3_objects = get_s3_objects_number(curated_bucket_name, s3_resource, destination_paths)

        if all([current_number_s3_objects[key] > starting_numbers[key] for key in destination_paths]):
            return {'status': 'success'}
        elif time.time() - start_time > TIMEOUT:
            return {'status': 'failure'}
        else:
            time.sleep(SLEEP_TIME)


def get_s3_objects_number(curated_bucket_name, s3_resource, destination_paths):
    curated_bucket = s3_resource.Bucket(curated_bucket_name)
    all_obj = curated_bucket.objects.all()
    return {key: count_s3_object_with_prefix(key, all_obj) for key in destination_paths}


def count_s3_object_with_prefix(prefix, _all_objects):
    return len([1 for _ in [x for x in _all_objects if x.key.startswith(prefix)]])


def sync_feeds(base_api_url, headers):
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    url = f'{base_api_url}/feeds/sync'
    requests.request('POST', url, data=json.dumps({}), headers=headers)
    get_result_event(base_api_url, 1, headers, 'sync_feeds', last_event_id)


def sync_structure(base_api_url, headers):
    url = f'{base_api_url}/structure/sync'
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    requests.request('POST', url, data=json.dumps({}), headers=headers)
    get_result_event(base_api_url, 1, headers, 'sync_as', last_event_id)


def wait_for_event_with_name(base_api_url, headers, action_name, action_type):
    timeout = 600
    request = get_request_with_responses_number(1)
    url = f'{base_api_url}/events/list'
    start = time.time()

    while True:
        request_result = requests.request('POST', url, data=json.dumps(request), headers=headers)
        result_events = request_result.json()['events']
        if result_events:
            event = result_events[0]
            if event['name'] == action_name and event['type'] == action_type and event['status'] == 'success':
                result = {'status': 'success'}
                break
            else:
                time.sleep(SLEEP_TIME)
        elif time.time() - start > timeout:
            result = {'status': 'failed'}
            break
        else:
            time.sleep(SLEEP_TIME)
    return result


def get_athena_query(athena_info, backfill_name, feeds_to_backfill):
    return f"""SELECT
               (SELECT count(DISTINCT name)
               FROM {athena_info['numeric_table_name']}
               WHERE data_source = '{backfill_name}'
               AND name in {tuple(feeds_to_backfill)}) +
               (SELECT count(DISTINCT name)
               FROM {athena_info['text_table_name']}
               WHERE data_source = '{backfill_name}'
               AND name in {tuple(feeds_to_backfill)}) as count;"""


def get_query_result(athena_client, athena_info, bucket_name, feeds_to_backfill, backfill_name):

    start_time = time.time()
    query = get_athena_query(athena_info, backfill_name, feeds_to_backfill)
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
        if time.time() - start_time > TIMEOUT:
            break
    assert(status == 'SUCCEEDED')

    response = athena_client.get_query_results(
        QueryExecutionId=query_execution_id,
        MaxResults=100
    )
    return int(response['ResultSet']['Rows'][1]['Data'][0]['VarCharValue'])


def get_start_and_finish_date(duration_minutes, start_date=None):
    def formatted_date(date_):
        return f'{date.strftime(date_, "%Y-%m-%dT%H:%M:%S.%fZ")}'
    assert(type(duration_minutes) == int)
    if start_date is None:
        start_date = (datetime.utcnow() - timedelta(days=5)).replace(hour=0, minute=0, second=0, microsecond=0)
    from_date = formatted_date(start_date)
    to_date = formatted_date(start_date + timedelta(minutes=duration_minutes))
    return from_date, to_date


def wait_for_reset(base_api_url, number_of_responses, headers):
    timeout = 600
    request = get_request_with_responses_number(number_of_responses)
    url = f'{base_api_url}/events/list'
    start = time.time()

    while True:
        request_result = requests.request('POST', url, data=json.dumps(request), headers=headers)
        res = request_result.json()['events']
        if len(res) == 1 and res[0]['type'] == 'reset' and res[0]['status'] == 'success':
            result = {'status': 'success'}
            break
        elif time.time() - start > timeout:
            result = {'status': 'failed'}
            break
        else:
            time.sleep(SLEEP_TIME)
    return result


def subscribe_all(base_api_url, headers, number_of_responses=2):
    prepare_feeds_state(base_api_url, headers, 'subscribe', number_of_responses)


def unsubscribe_all(base_api_url, headers, number_of_responses=2):
    prepare_feeds_state(base_api_url, headers, 'unsubscribe', number_of_responses)


def prepare_feeds_state(base_api_url, headers, action, number_of_responses=2):
    request = get_default_sub_request()
    last_event_id = safe_list_get_id(get_last_event_id(base_api_url, headers), 0, None)
    url = f'{base_api_url}/feeds/{action}'
    requests.request('POST', url, data=json.dumps(request), headers=headers)
    get_result_event(base_api_url, number_of_responses, headers, action, last_event_id)
