from source.utils import create_managed_feeds_manager_for_periodic_lambda

def pi_points_sync_handler(event, context):
    mfm = create_managed_feeds_manager_for_periodic_lambda()

    s3_bucket = event['s3_bucket']

    mfm.send_sync_pi_points_request(s3_bucket)