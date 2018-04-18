import logging
import os
import time

from aws_requests_auth.aws_auth import AWSRequestsAuth
from elasticsearch import Elasticsearch, RequestsHttpConnection
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from lambdas import cfnresponse
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager

log = logging.getLogger(__name__)


class AthenaQueryError(Exception):
    pass


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


def send_cfnresponse(custom_resource_lambda):

    def wrapper(event, context):
        try:
            custom_resource_lambda(event, context)
            cfnresponse.send(event, context, cfnresponse.SUCCESS)
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

    Session = sessionmaker(bind=engine)

    return ManagedFeedsManager.create_manager(aws_region, Session(), incoming_queue_name)
