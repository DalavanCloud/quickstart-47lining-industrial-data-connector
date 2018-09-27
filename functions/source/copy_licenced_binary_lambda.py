import logging
import os

import boto3

from source.utils import send_cfnresponse

log = logging.getLogger(__name__)


def copy_files(src_bucket_name, src_prefix, dest_bucket_name, dest_prefix):
    log.info("Copying from %s/%s to %s/%s" % (src_bucket_name, src_prefix, dest_bucket_name, dest_prefix))

    s3 = boto3.resource('s3')
    src_bucket = s3.Bucket(src_bucket_name)
    dest_bucket = s3.Bucket(dest_bucket_name)

    for obj in src_bucket.objects.filter(Prefix=src_prefix):
        source = {'Bucket': src_bucket_name, 'Key': obj.key}
        dest_bucket.copy(source, os.path.join(dest_prefix, os.path.basename(obj.key)))


def delete_binary_files(bucket_name, licensed_prefix, agent_prefix):
    bucket = boto3.resource('s3').Bucket(bucket_name)

    for prefix in [licensed_prefix, agent_prefix]:
        for obj in bucket.objects.filter(Prefix=prefix):
            obj.delete()


@send_cfnresponse
def handler(event, context):
    target_bucket_name = event['ResourceProperties']['DestinationBucketName']
    target_licensed_key_prefix = event['ResourceProperties']['DestinationKeyPrefix']
    compiled_agent_key_prefix = event['ResourceProperties']['CompiledAgentKeyPrefix']

    if event['RequestType'] == 'Create':
        copy_files(event['ResourceProperties']['LicensedSoftwareS3BucketName'],
                   event['ResourceProperties']['LicensedSoftwareS3KeyPrefix'],
                   event['ResourceProperties']['DestinationBucketName'],
                   event['ResourceProperties']['DestinationKeyPrefix'])

        copy_files(event['ResourceProperties']['ConnectorAgentAssetsS3BucketName'],
                   event['ResourceProperties']['ConnectorAgentAssetsS3KeyPrefix'],
                   event['ResourceProperties']['DestinationBucketName'],
                   event['ResourceProperties']['DestinationKeyPrefix'])

    elif event['RequestType'] == 'Delete':
        delete_binary_files(target_bucket_name, target_licensed_key_prefix, compiled_agent_key_prefix)
