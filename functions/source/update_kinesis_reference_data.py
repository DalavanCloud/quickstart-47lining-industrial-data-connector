'''
Updates reference data in Kinesis DA application. To be executed on s3 event trigger.
'''


import os
import logging
import boto3


log = logging.getLogger(__name__)
log.setLevel(logging.INFO)


def _update_reference_data_source(client, app_name, structure_bucket, structure_key, role_arn):
    response = client.describe_application(ApplicationName=app_name)
    application_version_id = response['ApplicationDetail']['ApplicationVersionId']
    reference_id = response['ApplicationDetail']['ReferenceDataSourceDescriptions'][0]['ReferenceId']
    log.info("Updating reference data of application %s, data source in s3: %s/%s" %
             (app_name, structure_bucket, structure_key))
    client.update_application(
        ApplicationName=app_name,
        CurrentApplicationVersionId=application_version_id,
        ApplicationUpdate={
            "ReferenceDataSourceUpdates": [
                {
                    'ReferenceId': reference_id,
                    'TableNameUpdate': 'REFERENCE_DATA',
                    'S3ReferenceDataSourceUpdate': {
                        'BucketARNUpdate': 'arn:aws:s3:::%s' % structure_bucket,
                        'FileKeyUpdate': structure_key,
                        'ReferenceRoleARNUpdate': role_arn
                    }
                }
            ]
        }
    )


def lambda_handler(event, context):
    deployment_suffix = os.environ['DEPLOYMENT_SUFFIX']
    app_name = 'managed-feeds-app-{}'.format(deployment_suffix)
    client = boto3.client('kinesisanalytics', region_name=os.environ['AWS_REGION'])
    _update_reference_data_source(
        client=client,
        app_name=app_name,
        structure_bucket=os.environ['STRUCTURE_DATA_BUCKET'],
        structure_key=os.environ['STRUCTURE_DATA_KEY'],
        role_arn=os.environ['ROLE_ARN']
    )
