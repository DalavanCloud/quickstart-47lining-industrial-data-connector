import base64

import boto3

from source.utils import send_cfnresponse


@send_cfnresponse
def lambda_handler(event, context):
    client = boto3.client('kms')
    secret = client.generate_random(
        NumberOfBytes=32
    )['Plaintext']

    data = {
        'secret': base64.b64encode(secret).decode()
    }

    return data
