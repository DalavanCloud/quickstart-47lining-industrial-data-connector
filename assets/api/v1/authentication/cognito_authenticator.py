from warrant import Cognito, AWSSRP


class CognitoAuthenticator():
    """
    Provides authentication via Amazon Cognito using specific user pool and app client
    """
    def __init__(self, cognito_user_pool_id, cognito_client_id, cognito_client_secret):
        self._cognito_user_pool_id = cognito_user_pool_id
        self._cognito_client_id = cognito_client_id
        self._cognito_client_secret = cognito_client_secret
        self._region = self._cognito_user_pool_id.split('_')[0]

    def login(self, username, password):
        if username is None or password is None:
            return {}
        aws = AWSSRP(username=username,
                     password=password,
                     pool_id=self._cognito_user_pool_id,
                     client_id=self._cognito_client_id,
                     pool_region=self._region,
                     client_secret=self._cognito_client_secret)

        tokens = aws.authenticate_user()
        authentication_result = {
            'id_token': tokens['AuthenticationResult']['IdToken'],
            'access_token': tokens['AuthenticationResult']['AccessToken'],
            'refresh_token': tokens['AuthenticationResult']['RefreshToken'],
            'username': username
        }
        return authentication_result

    def logout(self, id_token, refresh_token, access_token, username):
        cognito = Cognito(
            self._cognito_user_pool_id,
            self._cognito_client_id,
            id_token=id_token,
            refresh_token=refresh_token,
            access_token=access_token,
            username=username,
            user_pool_region=self._region
        )
        cognito.logout()

    def get_user(self, id_token, refresh_token, access_token, username):
        cognito = Cognito(
            self._cognito_user_pool_id,
            self._cognito_client_id,
            id_token=id_token,
            refresh_token=refresh_token,
            access_token=access_token,
            username=username,
            user_pool_region=self._region
        )
        cognito.get_user()
