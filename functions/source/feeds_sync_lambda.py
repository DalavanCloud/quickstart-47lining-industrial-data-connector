from source.utils import create_managed_feeds_manager_for_periodic_lambda


def feeds_sync_handler(event, context):
    mfm = create_managed_feeds_manager_for_periodic_lambda()

    s3_bucket = event['s3_bucket']

    mfm.send_sync_feeds_request(s3_bucket)
