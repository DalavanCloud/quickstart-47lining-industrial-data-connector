import logging
import os

import boto3

from source.utils import send_cfnresponse

log = logging.getLogger(__name__)
s3 = boto3.resource('s3')


def copy_files(src_bucket_name, src_prefix, dest_bucket_name, dest_prefix):
    log.info("Copying from %s/%s to %s/%s" % (src_bucket_name, src_prefix, dest_bucket_name, dest_prefix))

    src_bucket = s3.Bucket(src_bucket_name)
    dest_bucket = s3.Bucket(dest_bucket_name)

    for obj in src_bucket.objects.filter(Prefix=src_prefix):
        source = {'Bucket': src_bucket_name, 'Key': obj.key}
        dest_bucket.copy(source, os.path.join(dest_prefix, os.path.basename(obj.key)))

    else:
        log.error("Bucket %s not found!" % src_bucket)


def delete_binary_files(bucket_name, licensed_prefix, agent_prefix):
    bucket = boto3.resource('s3').Bucket(bucket_name)

    for prefix in [licensed_prefix, agent_prefix]:
        for obj in bucket.objects.filter(Prefix=prefix):
            obj.delete()


@send_cfnresponse
def handler(event, context):
    destination_bucket_name = os.environ['DESTINATION_BUCKET_NAME']
    destination_key_prefix = os.environ['DESTINATION_KEY_PREFIX']
    compiled_agent_key_prefix = os.environ['COMPILED_AGENT_KEY_PREFIX']

    if event['RequestType'] == 'Create':
        licensed_software_bucket_name = os.environ['LICENSED_SOFTWARE_BUCKET_NAME']
        licensed_software_key_prefix = os.environ['LICENSED_SOFTWARE_KEY_PREFIX']

        copy_files(licensed_software_bucket_name,
                   licensed_software_key_prefix,
                   destination_bucket_name,
                   destination_key_prefix)

        connector_agent_bucket_name = os.environ['CONNECTOR_AGENT_BUCKET_NAME']
        connector_agent_key_prefix = os.environ['CONNECTOR_AGENT_KEY_PREFIX']

        copy_files(connector_agent_bucket_name,
                   connector_agent_key_prefix,
                   destination_bucket_name,
                   destination_key_prefix)

    elif event['RequestType'] == 'Delete':
        delete_binary_files(destination_bucket_name, destination_key_prefix, compiled_agent_key_prefix)
