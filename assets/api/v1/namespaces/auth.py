from botocore.exceptions import ClientError
from flask import request
from flask_restplus import Namespace
from injector import inject

from api.api_utils import raise_backend_exception
from api.v1.ApiResource import ApiResource
from api.v1.authentication.cognito_authenticator import CognitoAuthenticator
from api.v1.authentication.utils import login_required


def create_auth_namespace(api, **kwargs):
    auth_ns = Namespace('auth', description='Operations related to authentication')

    @auth_ns.route('/login', methods=['POST'])
    @api.doc(security=None)
    class Login(ApiResource):

        @inject
        def __init__(self, authenticator: CognitoAuthenticator, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._authenticator = authenticator

        @api.response(200, 'User is logged in')
        @api.expect(kwargs['credentials'])
        def post(self):
            authentication_result = self._authenticator.login(request.json.get('username'),
                                                              request.json.get('password'))
            if not authentication_result:
                return {'message': 'Empty username or password'}, 400
            return authentication_result

        @api.errorhandler(ClientError)
        def login_failed(self):
            return {'message': 'Cannot login user'}, 401

    @auth_ns.route('/logout', methods=['POST'])
    class Logout(ApiResource):
        @inject
        def __init__(self, authenticator: CognitoAuthenticator, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._authenticator = authenticator

        @raise_backend_exception('Unable to logout')
        @api.response(200, 'User is logged out')
        @login_required
        def post(self):
            self._authenticator.logout(
                id_token=request.headers.get('id_token'),
                refresh_token=request.headers.get('refresh_token'),
                access_token=request.headers.get('access_token'),
                username=request.headers.get('username')
            )

    return auth_ns
