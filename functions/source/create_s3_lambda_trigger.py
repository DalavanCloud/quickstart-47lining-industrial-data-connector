'''
Generic function creating lambda trigger with given lambda, s3 bucket, s3 key and list of s3 events.
Preserving old notification configurations
'''


import logging
import boto3
import uuid
from source.utils import send_cfnresponse


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def _get_old_notification_configurations(client, bucket):
    return client.get_bucket_notification_configuration(
        Bucket=bucket
    )


def _build_notification_configuration(prefix, lambda_arn, events):
    notification_id = uuid.uuid4().hex
    return {
        'Id': notification_id,
        'LambdaFunctionArn': lambda_arn,
        'Events': events,
        'Filter': {
            'Key': {
                'FilterRules': [
                    {
                        'Name': 'prefix',
                        'Value': prefix
                    }
                ]
            }
        }
    }


def _join_notification_configurations(current_notifications, new_notification):
    new_notifications = {}
    new_notifications['TopicConfigurations'] = current_notifications.get('TopicConfigurations', [])
    new_notifications['QueueConfigurations'] = current_notifications.get('QueueConfigurations', [])
    new_notifications['LambdaFunctionConfigurations'] = current_notifications.get('LambdaFunctionConfigurations', [])
    new_notifications['LambdaFunctionConfigurations'].append(new_notification)
    return new_notifications


def _create_notification_configuration(client, bucket, prefix, lambda_arn, events):
    current_notifications = _get_old_notification_configurations(client, bucket)
    new_notification = _build_notification_configuration(prefix, lambda_arn, events)
    new_notifications = _join_notification_configurations(current_notifications, new_notification)
    log.info("Putting notification configuration for bucket %s, keys with prefix: %s, lambda ARN: %s and events: %s" %
             (bucket, prefix, lambda_arn, events))
    log.info("Existing configuration: %s" % (current_notifications))
    log.info("New configuration: %s" % (new_notifications))
    client.put_bucket_notification_configuration(
        Bucket=bucket,
        NotificationConfiguration=new_notifications
    )


@send_cfnresponse
def lambda_handler(event, context):
    log.info("Invoked: Create S3 lambda trigger")
    log.info("Event: %s" % (event))
    if event['RequestType'] == 'Create':
        _create_notification_configuration(
            client=boto3.client('s3'),
            bucket=event['ResourceProperties']['Bucket'],
            prefix=event['ResourceProperties']['Prefix'],
            lambda_arn=event['ResourceProperties']['LambdaARN'],
            events=event['ResourceProperties']['Events']
        )
