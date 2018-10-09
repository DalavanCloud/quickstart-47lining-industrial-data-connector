import importlib

import boto3
import logging
import os
import time

from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from source.configuration.input_stream import additional_columns_stream

from source import cfnresponse
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager

log = logging.getLogger(__name__)


def import_sqlalchemy_model(connector_type, model_name):
    module_connector_map = {
        'PI': 'model.pi.models',
        'WONDERWARE': 'model.wonderware.models',
        'KEPWARE': 'model.kepware.models',
    }

    module = importlib.import_module(module_connector_map[connector_type])
    return getattr(module, model_name)


class AthenaQueryError(Exception):
    pass


def run_athena_query(query, query_output_location_dir, region):
    query_config = dict(
        QueryString=query,
        ResultConfiguration={
            'OutputLocation': query_output_location_dir
        }
    )
    client = boto3.client('athena', region_name=region)
    response = client.start_query_execution(**query_config)
    query_execution_id = response['QueryExecutionId']
    wait_for_athena_query_completion(client, query_execution_id)


def wait_for_athena_query_completion(athena_client, query_execution_id, timeout=20):
    start_time = time.time()
    while True:
        time.sleep(0.5)
        response = athena_client.get_query_execution(QueryExecutionId=query_execution_id)
        query_state = response['QueryExecution']['Status']['State']
        if query_state == 'SUCCEEDED':
            break
        if query_state == 'FAILED':
            raise AthenaQueryError(response)
        if (time.time() - start_time) > timeout:
            raise TimeoutError('Athena query execution timeout')


def make_drop_table_query(database_name, table_name):
    return """
        DROP TABLE IF EXISTS {database_name}.{table_name} PURGE
    """.format(
        database_name=database_name,
        table_name=table_name
    )


def send_cfnresponse(custom_resource_lambda):
    def wrapper(event, context):
        try:
            data = custom_resource_lambda(event, context)
            cfnresponse.send(event, context, cfnresponse.SUCCESS, response_data=data)
        except Exception as e:
            log.exception(e)
            cfnresponse.send(event, context, cfnresponse.FAILED)

    return wrapper


def make_elasticsearch_client(elasticsearch_endpoint):
    awsauth = AWSRequestsAuth(
        aws_access_key=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'],
        aws_token=os.environ['AWS_SESSION_TOKEN'],
        aws_host=elasticsearch_endpoint,
        aws_region=os.environ['AWS_REGION'],
        aws_service='es'
    )
    return Elasticsearch(
        hosts=['{0}:443'.format(elasticsearch_endpoint)],
        use_ssl=True,
        connection_class=RequestsHttpConnection,
        http_auth=awsauth
    )


def create_managed_feeds_manager_for_periodic_lambda():
    aws_region = os.environ['AWS_REGION']
    incoming_queue_name = os.environ['SQS_IN_QUEUE_NAME']
    engine = create_engine(os.environ['POSTGRES_URI'])
    connector_type = os.environ['CONNECTOR_TYPE']

    Session = sessionmaker(bind=engine)

    return ManagedFeedsManager.create_manager(aws_region, Session(), incoming_queue_name, connector_type=connector_type)


def make_additional_assets_columns_without_join_column(connector_type):
    join_column_name = get_join_column(connector_type)
    additional_assets_columns_with_join_column = get_additional_assets_columns_with_join_column(connector_type)

    additional_assets_columns = [x for x in additional_assets_columns_with_join_column if
                                 x['column_name'] != join_column_name]
    return additional_assets_columns


def get_additional_assets_columns_with_join_column(connector_type):
    if connector_type == 'PI':
        from source.configuration.assets_structure_pi import additional_assets_columns_with_join_column
        assets_columns = additional_assets_columns_with_join_column + additional_columns_stream
    elif connector_type == 'WONDERWARE':
        from source.configuration.assets_structure_wonderware import additional_assets_columns_with_join_column
        assets_columns = additional_assets_columns_with_join_column + additional_columns_stream
    elif connector_type == 'KEPWARE':
        from source.configuration.assets_structure_kepware import additional_assets_columns_with_join_column
        assets_columns = additional_assets_columns_with_join_column
    else:
        raise NotImplementedError('Unknown connector type {}'.format(connector_type))
    return assets_columns


def get_join_column(connector_type):
    if connector_type == 'PI':
        from source.configuration.assets_structure_pi import JOIN_COLUMN_NAME
    elif connector_type == 'WONDERWARE':
        from source.configuration.assets_structure_wonderware import JOIN_COLUMN_NAME
    elif connector_type == 'KEPWARE':
        from source.configuration.assets_structure_kepware import JOIN_COLUMN_NAME
    else:
        raise NotImplementedError('Unknown connector type {}'.format(connector_type))
    return JOIN_COLUMN_NAME


def get_input_stream_record_columns(connector_type):
    if connector_type == 'PI':
        from source.configuration.input_stream import input_stream_record_columns_pi as input_stream_record_columns
    elif connector_type == 'WONDERWARE':
        from source.configuration.input_stream import input_stream_record_columns_wonderware as \
            input_stream_record_columns
    elif connector_type == 'KEPWARE':
        from source.configuration.input_stream import input_stream_record_columns_kepware as input_stream_record_columns
    else:
        raise NotImplementedError('Unknown connector type {}'.format(connector_type))

    return input_stream_record_columns
