import json

import boto3
import pytest
from boto3 import Session
from mock import Mock, mock
from collections import namedtuple

from service.publishing_manager import PublishingManager
from service.sqs_service import SQSService
from service.iot_service import IoTService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
# from workers.managed_feeds.managed_feeds_dynamodb_dao import ManagedFeedsDynamodbDao
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager

from assets.model.models import Base
from workers.managed_feeds.managed_feeds_postgres_dao import ManagedFeedsPostgresDao

__all__ = [
    's3',
    's3_resource',
    's3_client',
    'sqs_service',
    'iot_service',
    'outgoing_queue',
    'incoming_queue',
    'dynamodb_resource',
    'pi_points_dynamo_table',
    'events_status_table',
    'managed_feeds_manager',
    'sqs_uuid4',
    'publishing_manager',
    'boto_session',
    'postgres_session',
    'postgres_engine',
    'managed_feeds_postgres_dao',
    'managed_feeds_postgres_manager'
]


@pytest.fixture()
def sqs_uuid4(request):
    uuid_mock = mock.patch('service.sqs_service.uuid.uuid4').start()
    request.addfinalizer(lambda: uuid_mock.stop())
    return uuid_mock


@pytest.mark.usefixtures("sqs_uuid4")
@pytest.fixture()
def sqs_queue():

    def save_message(**kwargs):
        assert 'MessageBody' in kwargs
        msg = json.loads(kwargs['MessageBody'])
        messages.append(msg)

    messages = []
    queue = Mock(messages=messages)
    queue.send_message.side_effect = save_message

    return queue

incoming_queue = sqs_queue
outgoing_queue = sqs_queue


@pytest.fixture()
def sqs_service(incoming_queue, outgoing_queue):
    return SQSService(incoming_queue=incoming_queue, outgoing_queue=outgoing_queue)


@pytest.fixture()
def iot_service(managed_feeds_postgres_dao):
    return IoTService(
        iot_client=Mock(),
        managed_feeds_dao=managed_feeds_postgres_dao
    )


@pytest.fixture(scope='session')
def dynamodb_resource():
    return boto3.resource(
        'dynamodb',
        aws_access_key_id='ak_id',
        aws_secret_access_key='ak',
        region_name='us-west-2',
        endpoint_url='http://localhost:8000'
    )


@pytest.fixture()
def s3(request):
    def delete_all_s3_data():
        buckets = client.list_buckets()['Buckets']
        bucket_names = set(bucket['Name'] for bucket in buckets)

        for bucket_name in bucket_names:
            for obj in resource.Bucket(bucket_name).objects.all():
                obj.delete()

    client = boto3.client(
        's3',
        aws_access_key_id='ak_id',
        aws_secret_access_key='ak',
        endpoint_url='http://localhost:4569'
    )
    resource = boto3.resource(
        's3',
        aws_access_key_id='ak_id',
        aws_secret_access_key='ak',
        endpoint_url='http://localhost:4569'
    )

    request.addfinalizer(delete_all_s3_data)

    S3 = namedtuple('S3', 'client resource')
    return S3(client=client, resource=resource)


@pytest.fixture()
def s3_client(s3):
    return s3.client


@pytest.fixture()
def s3_resource(s3):
    return s3.resource


@pytest.fixture()
def boto_session(s3_resource):

    def make_resource(serivce_name, **kwargs):
        return {'s3': s3_resource}[serivce_name]

    session_mock = Mock(spec_set=Session)
    session_mock.resource.side_effect = make_resource
    return session_mock


@pytest.fixture()
def pi_points_dynamo_table(request, dynamodb_resource):
    dynamodb_resource.create_table(
        AttributeDefinitions=[
            {
                "AttributeName": "pi_point",
                "AttributeType": "S"
            }
        ],
        KeySchema=[
            {
                "AttributeName": "pi_point",
                "KeyType": "HASH"
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10
        },
        TableName="pi_points"
    )
    table = dynamodb_resource.Table('pi_points')
    request.addfinalizer(lambda: table.delete())
    return table


@pytest.fixture()
def events_status_table(request, dynamodb_resource):
    dynamodb_resource.create_table(
        AttributeDefinitions=[
            {
                "AttributeName": "event_type",
                "AttributeType": "S"
            },
            {
                "AttributeName": "id",
                "AttributeType": "S"
            },
            {
                "AttributeName": "update_timestamp",
                "AttributeType": "S"
            },
            {
                "AttributeName": "create_date",
                "AttributeType": "S"
            }
        ],
        KeySchema=[
            {
                "AttributeName": "id",
                "KeyType": "HASH"
            }
        ],
        GlobalSecondaryIndexes=[
            {
                'IndexName': 'EventTimestampIndex',
                'KeySchema': [
                    {
                        "AttributeName": "event_type",
                        "KeyType": "HASH"
                    },
                    {
                        'AttributeName': 'update_timestamp',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10
                }
            },
            {
                'IndexName': 'EventDateIndex',
                'KeySchema': [
                    {
                        "AttributeName": "create_date",
                        "KeyType": "HASH"
                    },
                    {
                        'AttributeName': 'update_timestamp',
                        'KeyType': 'RANGE'
                    },
                ],
                'Projection': {
                    'ProjectionType': 'ALL'
                },
                "ProvisionedThroughput": {
                    "ReadCapacityUnits": 10,
                    "WriteCapacityUnits": 10
                }
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10
        },
        TableName="events_status"
    )
    table = dynamodb_resource.Table('events_status')
    request.addfinalizer(lambda: table.delete())
    return table


@pytest.fixture()
def postgres_engine(request):

    def drop_all():
        for table in reversed(Base.metadata.sorted_tables):
            table.drop(bind=engine)

    engine = create_engine(
        'postgresql://postgres:postgres@localhost:5432/postgres',
        use_batch_mode=True
    )
    Base.metadata.create_all(engine)
    request.addfinalizer(drop_all)

    return engine


@pytest.fixture()
def postgres_session(request, postgres_engine):
    session_factory = sessionmaker(bind=postgres_engine)
    Session = scoped_session(session_factory)
    request.addfinalizer(Session.remove)
    return Session


@pytest.fixture()
def managed_feeds_postgres_dao(postgres_session, s3_client):
    return ManagedFeedsPostgresDao(postgres_session, s3_client)


@pytest.fixture()
def managed_feeds_postgres_manager(s3_resource, sqs_service, managed_feeds_postgres_dao, iot_service):
    return ManagedFeedsManager(s3_resource, sqs_service, managed_feeds_postgres_dao, iot_service)


@pytest.fixture()
def managed_feeds_manager(s3_resource, sqs_service, managed_feeds_dynamo_dao, iot_service):
    return ManagedFeedsManager(s3_resource, sqs_service, managed_feeds_dynamo_dao, iot_service)


@pytest.fixture()
def publishing_manager(request, s3_resource, boto_session):
    session_patcher = mock.patch('service.publishing_manager.boto3.session.Session')
    session_mock = session_patcher.start()
    session_mock.return_value = boto_session
    request.addfinalizer(lambda: session_patcher.stop())
    return PublishingManager(s3_resource)
