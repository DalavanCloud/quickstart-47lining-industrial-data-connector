import json

from random import randint
import boto3
import pytest
from boto3 import Session
from mock import Mock, mock
from collections import namedtuple

from service.sqs_service import SQSService
from service.iot_service import IoTService
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from workers.managed_feeds.dao.managed_feeds_postgres_dao_pi import ManagedFeedsPostgresDaoPi
from workers.managed_feeds.dao.managed_feeds_postgres_dao_wonderware import ManagedFeedsPostgresDaoWonderware
from workers.managed_feeds.dao.managed_feeds_postgres_dao_kepware import ManagedFeedsPostgresDaoKepware
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager
from workers.managed_feeds.user_provider.UserProvider import AnonymousUserProvider

__all__ = [
    's3',
    's3_resource',
    's3_client',
    'sqs_service',
    'iot_service',
    'outgoing_queue',
    'incoming_queue',
    'backfill_queue',
    'interpolation_queue',
    'subscription_queue',
    'dynamodb_resource',
    'feeds_dynamo_table',
    'events_status_table',
    'sqs_uuid4',
    'boto_session',
    'postgres_session_pi',
    'postgres_session_wonderware',
    'postgres_session_kepware',
    'postgres_engine_pi',
    'postgres_engine_wonderware',
    'postgres_engine_kepware',
    'managed_feeds_postgres_dao_pi',
    'managed_feeds_postgres_dao_wonderware',
    'managed_feeds_postgres_manager',
    'managed_feeds_postgres_manager_wonderware',
    'managed_feeds_postgres_dao_kepware'
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
backfill_queue = sqs_queue
interpolation_queue = sqs_queue
subscription_queue = sqs_queue


@pytest.fixture()
def sqs_service(incoming_queue, outgoing_queue, backfill_queue, interpolation_queue, subscription_queue):
    return SQSService(incoming_queue=incoming_queue, backfill_queue=backfill_queue,
                      interpolation_queue=interpolation_queue, subscription_queue=subscription_queue,
                      outgoing_queue=outgoing_queue)


@pytest.fixture()
def iot_service(managed_feeds_postgres_dao):
    return IoTService(
        iot_client=Mock(),
        managed_feeds_dao=managed_feeds_postgres_dao
    )


@pytest.fixture()
def iot_service_wonderware(managed_feeds_postgres_dao_wonderware):
    return IoTService(
        iot_client=Mock(),
        managed_feeds_dao=managed_feeds_postgres_dao_wonderware
    )


@pytest.fixture()
def iot_service_kepware(managed_feeds_postgres_dao_kepware):
    return IoTService(
        iot_client=Mock(),
        managed_feeds_dao=managed_feeds_postgres_dao_kepware
    )


@pytest.fixture(scope='session')
def dynamodb_resource():
    return boto3.resource(
        'dynamodb',
        aws_access_key_id='ak_id',
        aws_secret_access_key='ak',
        region_name='us-west-2',
        endpoint_url='http://localhost:4569'
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
        endpoint_url='http://localhost:4572'
    )
    resource = boto3.resource(
        's3',
        aws_access_key_id='ak_id',
        aws_secret_access_key='ak',
        endpoint_url='http://localhost:4572'
    )

    request.addfinalizer(delete_all_s3_data)

    S3 = namedtuple('S3', 'client resource')
    return S3(client=client, resource=resource)


@pytest.fixture()
def bucket_name(s3_resource):
    bucket_name = f'bucket-{randint(1, 10000)}'
    s3_resource.create_bucket(
        Bucket=bucket_name,
        CreateBucketConfiguration={
            'LocationConstraint': 'us-west-1'
        }
    )
    return bucket_name


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
def feeds_dynamo_table(request, dynamodb_resource):
    dynamodb_resource.create_table(
        AttributeDefinitions=[
            {
                "AttributeName": "name",
                "AttributeType": "S"
            }
        ],
        KeySchema=[
            {
                "AttributeName": "name",
                "KeyType": "HASH"
            }
        ],
        ProvisionedThroughput={
            "ReadCapacityUnits": 10,
            "WriteCapacityUnits": 10
        },
        TableName="feeds"
    )
    table = dynamodb_resource.Table('feeds')
    request.addfinalizer(lambda: table.delete())
    return table


@pytest.fixture()
def events_status_table(request, dynamodb_resource):
    dynamodb_resource.create_table(
        AttributeDefinitions=[
            {
                "AttributeName": "type",
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
                        "AttributeName": "type",
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
def postgres_engine_pi(request):
    from model.pi.models import Base

    def drop_all():
        for table in reversed(Base.metadata.sorted_tables):
            table.drop(bind=engine)

    engine = create_engine(
        'postgresql://postgres:postgres@localhost:5432/postgres',
        use_batch_mode=True,
        echo=True
    )
    Base.metadata.create_all(engine)
    request.addfinalizer(drop_all)

    return engine


@pytest.fixture()
def postgres_engine_wonderware(request):
    from model.wonderware.models import Base

    def drop_all():
        for table in reversed(Base.metadata.sorted_tables):
            table.drop(bind=engine)

    engine = create_engine(
        'postgresql://postgres:postgres@localhost:5432/postgres',
        use_batch_mode=True,
        echo=True
    )
    Base.metadata.create_all(engine)
    request.addfinalizer(drop_all)

    return engine


@pytest.fixture()
def postgres_engine_kepware(request):
    from model.kepware.models import Base

    def drop_all():
        for table in reversed(Base.metadata.sorted_tables):
            table.drop(bind=engine)

    engine = create_engine(
        'postgresql://postgres:postgres@localhost:5432/postgres',
        use_batch_mode=True,
        echo=True
    )
    Base.metadata.create_all(engine)
    request.addfinalizer(drop_all)

    return engine


@pytest.fixture()
def postgres_engine(postgres_engine_pi):
    return postgres_engine_pi


@pytest.fixture()
def postgres_session_pi(request, postgres_engine_pi):
    session_factory = sessionmaker(bind=postgres_engine_pi)
    Session = scoped_session(session_factory)
    request.addfinalizer(Session.remove)
    return Session


@pytest.fixture()
def postgres_session_wonderware(request, postgres_engine_wonderware):
    session_factory = sessionmaker(bind=postgres_engine_wonderware)
    Session = scoped_session(session_factory)
    request.addfinalizer(Session.remove)
    return Session


@pytest.fixture()
def postgres_session_kepware(request, postgres_engine_kepware):
    session_factory = sessionmaker(bind=postgres_engine_kepware)
    Session = scoped_session(session_factory)
    request.addfinalizer(Session.remove)
    return Session


@pytest.fixture()
def postgres_session(postgres_session_pi):
    return postgres_session_pi


@pytest.fixture()
def user_provider():
    return AnonymousUserProvider()


@pytest.fixture()
def managed_feeds_postgres_dao(managed_feeds_postgres_dao_pi):
    return managed_feeds_postgres_dao_pi


@pytest.fixture()
def managed_feeds_postgres_dao_pi(postgres_session_pi, s3_client):
    return ManagedFeedsPostgresDaoPi(postgres_session_pi, s3_client)


@pytest.fixture()
def managed_feeds_postgres_dao_wonderware(postgres_session_wonderware, s3_client):
    return ManagedFeedsPostgresDaoWonderware(postgres_session_wonderware, s3_client)


@pytest.fixture()
def managed_feeds_postgres_dao_kepware(postgres_session_kepware, s3_client):
    return ManagedFeedsPostgresDaoKepware(postgres_session_kepware, s3_client)


@pytest.fixture()
def managed_feeds_postgres_manager(managed_feeds_postgres_manager_pi):
    return managed_feeds_postgres_manager_pi


@pytest.fixture()
def managed_feeds_postgres_manager_pi(s3_resource, sqs_service, managed_feeds_postgres_dao_pi, iot_service,
                                      user_provider):
    return ManagedFeedsManager(s3_resource, sqs_service, managed_feeds_postgres_dao_pi, iot_service, user_provider)


@pytest.fixture()
def managed_feeds_postgres_manager_wonderware(s3_resource, sqs_service, managed_feeds_postgres_dao_wonderware,
                                              iot_service_wonderware, user_provider):
    return ManagedFeedsManager(s3_resource, sqs_service, managed_feeds_postgres_dao_wonderware, iot_service_wonderware,
                               user_provider)


@pytest.fixture()
def managed_feeds_postgres_manager_kepware(s3_resource, sqs_service, managed_feeds_postgres_dao_kepware,
                                           iot_service_kepware, user_provider):
    return ManagedFeedsManager(s3_resource, sqs_service, managed_feeds_postgres_dao_kepware, iot_service_kepware,
                               user_provider)
