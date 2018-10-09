'''
Creates initial user for cognito user pool.
Additionally, this function returns app client secret as output that is
used later in management console environment variables, as it cannot be
currently done using CloudFormation.
'''


import os
import hashlib
import base64
import hmac
import boto3

from source.utils import send_cfnresponse


def _create_secret_hash(username, app_client_id, client_secret):
    message = username + app_client_id
    client_secret_bytes = bytes(client_secret, 'ascii')
    dig = hmac.new(client_secret_bytes, msg=message.encode('UTF-8'),
                   digestmod=hashlib.sha256).digest()
    return base64.b64encode(dig).decode()


def _get_client_secret(client, user_pool_id, app_client_id):
    response = client.describe_user_pool_client(UserPoolId=user_pool_id, ClientId=app_client_id)
    return response['UserPoolClient']['ClientSecret']


def create_admin_user(client, user_pool_id, app_client_id, client_secret, username, password):
    secret_hash = _create_secret_hash(username, app_client_id, client_secret)
    user_attributes = [
        {"Name": "given_name", "Value": "admin"},
        {"Name": "family_name", "Value": "admin"}
    ]
    client.sign_up(ClientId=app_client_id, Username=username, Password=password,
                   SecretHash=secret_hash, UserAttributes=user_attributes)
    client.admin_confirm_sign_up(UserPoolId=user_pool_id, Username=username)


@send_cfnresponse
def lambda_handler(event, context):
    user_pool_id = os.environ['USER_POOL_ID']
    app_client_id = os.environ['APP_CLIENT_ID']
    cognito_client = boto3.client('cognito-idp')
    client_secret = _get_client_secret(cognito_client, user_pool_id, app_client_id)

    admin_username = os.environ['ADMIN_USERNAME']
    admin_password = os.environ['ADMIN_PASSWORD']

    if event['RequestType'] == 'Create':
        create_admin_user(cognito_client, user_pool_id, app_client_id, client_secret, admin_username, admin_password)
        return {'ClientSecret': client_secret}
