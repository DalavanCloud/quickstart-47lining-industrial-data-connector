import json
import logging
import re
import uuid

import boto3
import pytest
import requests

logger = logging.getLogger(__name__)


def pytest_addoption(parser):
    parser.addoption("--elb_url", action="store", help="Specify elb url for webapp management console")
    parser.addoption("--user_name", action="store", help="Specify user name for webapp management console")
    parser.addoption("--password", action="store", help="Specify password for webapp management console")
    parser.addoption("--curated_bucket", action="store", help="Specify curated_bucket for webapp management console")


def create_bucket(s3_resource, region):
    bucket_name = f'test-bucket-for-athena-query-{str(uuid.uuid1())[:10]}'
    if region == 'us-east-1':
        s3_resource.create_bucket(
            Bucket=bucket_name
        )
    else:
        s3_resource.create_bucket(
            Bucket=bucket_name,
            CreateBucketConfiguration={
                'LocationConstraint': region
            }
        )
    return bucket_name


def delete_bucket(s3_resource, bucket_name):
    bucket = s3_resource.Bucket(bucket_name)
    bucket.objects.all().delete()
    bucket.delete()


def pytest_collection_modifyitems(items, config):
    selected_items = []
    deselected_items = []

    for item in items:
        if str(item.name).startswith('test'):
            selected_items.append(item)
        else:
            deselected_items.append(item)
    config.hook.pytest_deselected(items=deselected_items)
    items[:] = selected_items


@pytest.fixture
def s3_resource():
    return boto3.resource('s3')


@pytest.fixture
def athena_client(base_api_url, headers):
    athena_info = get_athena_info(base_api_url, headers)
    region = re.search('=.*', athena_info['url']).group(0)[1:]
    return boto3.client('athena', region_name=region)


@pytest.fixture
def base_api_url(request):
    elb_url = request.config.getoption("--elb_url")
    if elb_url:
        return f'{elb_url}/api/v1'
    else:
        raise Exception('No arguments specified: elb_url')


@pytest.fixture
def curated_bucket_name(request):
    curated_bucket = request.config.getoption("--curated_bucket")
    if curated_bucket:
        return curated_bucket
    else:
        raise Exception('No arguments specified: curated_bucket')


@pytest.fixture
def headers(request):
    username = request.config.getoption("--user_name")
    password = request.config.getoption("--password")
    elb_url = request.config.getoption("--elb_url")
    if username and password:
        result = requests.request(
            method='POST',
            url=f'{elb_url}/api/v1/auth/login',
            data=json.dumps({"username": username, "password": password}),
            headers={'accept': 'application/json', 'content-type': 'application/json', 'connection': 'keep-alive'}
        )

        response = result.json()
        return {'accept': 'application/json', 'content-type': 'application/json', 'connection': 'keep-alive',
                'id_token': response['id_token'], 'access_token': response['access_token'],
                'refresh_token': response['refresh_token'], 'username': response['username']}
    else:
        raise Exception('No arguments specified: username, password')


@pytest.yield_fixture
def bucket_name(s3_resource, base_api_url, headers):
    athena_info = get_athena_info(base_api_url, headers)
    region = re.search('=.*', athena_info['url']).group(0)[1:]
    bucket_name = create_bucket(s3_resource, region)
    try:
        yield bucket_name
    except Exception:
        logger.error("Error occurred during bucket usage.")
    finally:
        delete_bucket(s3_resource, bucket_name)


def get_athena_info(base_api_url, headers):
    url = f'{base_api_url}/athena/info'
    return requests.request('GET', url, headers=headers).json()
