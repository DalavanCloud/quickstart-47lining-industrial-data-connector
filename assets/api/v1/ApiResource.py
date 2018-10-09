from flask_restplus import Resource
from injector import inject

from api.v1.authentication.cognito_authenticator import CognitoAuthenticator


class ApiResource(Resource):
    @inject
    def __init__(self, authenticator: CognitoAuthenticator, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._authenticator = authenticator
