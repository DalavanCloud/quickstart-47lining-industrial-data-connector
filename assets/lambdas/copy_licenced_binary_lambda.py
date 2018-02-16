import os
from concurrent.futures import ThreadPoolExecutor

import boto3
import functools
from lambdas.utils import send_cfnresponse


def copy_data(event, source_bucket, source_key, destination_key):
    submissions_bucket = boto3.resource('s3').Bucket(event['ResourceProperties']['DestinationBucketName'])
    copy_source = {
        'Bucket': source_bucket,
        'Key': source_key
    }
    return functools.partial(submissions_bucket.copy, copy_source, destination_key)


def recursive_copy_data(event, source_bucket, source_prefix, destination_prefix):
    data_bucket = boto3.resource('s3').Bucket(source_bucket)
    source_path = source_prefix
    for obj in data_bucket.objects.filter(Prefix=source_path):
        source_key = obj.key
        destination_key = os.path.join(destination_prefix, os.path.basename(obj.key))
        yield copy_data(event, source_bucket, source_key, destination_key)


def generate_copy_jobs(event):
    yield from recursive_copy_data(event,
                                   source_bucket=event['ResourceProperties']['LicensedSoftwareS3BucketName'],
                                   source_prefix=event['ResourceProperties']['LicensedSoftwareS3KeyPrefix'],
                                   destination_prefix=event['ResourceProperties']['DestinationKeyPrefix'])
    yield from recursive_copy_data(event,
                                   source_bucket=event['ResourceProperties']['ConnectorAgentAssetsS3BucketName'],
                                   source_prefix=event['ResourceProperties']['ConnectorAgentAssetsS3KeyPrefix'],
                                   destination_prefix=event['ResourceProperties']['DestinationKeyPrefix'])




@send_cfnresponse
def handler(event, context):
    if event['RequestType'] == 'Create':
        with ThreadPoolExecutor(max_workers=7) as executor:
            futures = [executor.submit(job) for job in generate_copy_jobs(event)]
        for future in futures:
            exception = future.exception()
            if exception is not None:
                print(exception)
                raise exception
    elif event['RequestType'] == 'Delete':
        regional_lambda_bucket = boto3.resource('s3').Bucket(event['ResourceProperties']['DestinationBucketName'])
        for key in regional_lambda_bucket.objects.filter(Prefix=event['ResourceProperties']['DestinationKeyPrefix']):
            key.delete()


