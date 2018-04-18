import logging
import boto3

from lambdas.utils import send_cfnresponse

@send_cfnresponse
def lambda_handler(event, context):
    if event['RequestType'] == 'Delete':
        certificate_id = event['ResourceProperties']['CertificateId']
        client = boto3.client('iot')

        logging.info("Deactivating certificate %s" % certificate_id)

        client.update_certificate(
            certificateId=certificate_id,
            newStatus='INACTIVE'
        )
    else:
        logging.info("Not DELETE request, skipping.")