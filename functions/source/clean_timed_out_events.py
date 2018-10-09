import logging
import os
import datetime

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager


logger = logging.getLogger(__name__)


def lambda_handler(event, context):
    aws_region = os.environ['AWS_REGION']
    engine = create_engine(os.environ['POSTGRES_URI'])

    Session = sessionmaker(bind=engine)

    mfm = ManagedFeedsManager.create_manager(aws_region, Session(), connector_type=os.environ['CONNECTOR_TYPE'])

    failed_events = mfm.get_events(
        status='pending',
        timestamp_to=datetime.datetime.now() - datetime.timedelta(
            days=int(os.environ['TIMEOUT_DAYS'])
        )
    )['events']

    for event in failed_events:
        mfm.handle_event_failure(event)
        logger.info('Failed event %s', event['id'])

    cloudwatch = boto3.client('cloudwatch')
    cloudwatch.put_metric_data(
        MetricData=[
            {
                'MetricName': 'TimedOutEventsCount',
                'Unit': 'None',
                'Value': len(failed_events)
            },
        ],
        Namespace=os.environ['METRIC_NAMESPACE_NAME']
    )
