import logging
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager


def read_args_from_environment():
    return {
        'postgres_uri': os.environ['POSTGRES_URI'],
        'outgoing_sqs_name': os.environ['OUTGOING_SQS_NAME'],
        'subscription_sqs_name': os.environ['SUBSCRIPTION_SQS_NAME'],
        'region': os.environ['REGION'],
        'dts': os.environ['DTS'],
        'connector_type': os.environ['CONNECTOR_TYPE'],
    }


def lambda_handler(event, context):

    messages = event['Records']
    message_to_process = messages[0]['body']

    logging.basicConfig(
        level=logging.INFO,
        format='[%(asctime)s][%(levelname)s] %(message)s',
        datefmt='%H:%M:%S'
    )
    args = read_args_from_environment()

    engine = create_engine(args['postgres_uri'], use_batch_mode=True)
    session_factory = sessionmaker(bind=engine)
    Session = scoped_session(session_factory)

    feeds_manager = ManagedFeedsManager.create_manager(
        args['region'],
        postgres_session=Session,
        outgoing_queue_name=args['outgoing_sqs_name'],
        subscription_queue_name=args['subscription_sqs_name'],
        use_iot=args['dts'] == 'AWS IoT',
        connector_type=args['connector_type'],
    )

    feeds_manager.start_processing_requests(message_to_process)
