from source.utils import create_managed_feeds_manager_for_periodic_lambda


def as_sync_handler(event, context):
    mfm = create_managed_feeds_manager_for_periodic_lambda()

    s3_bucket = event['s3_bucket']
    database = event['database']

    mfm.send_sync_as_request(s3_bucket, database)
