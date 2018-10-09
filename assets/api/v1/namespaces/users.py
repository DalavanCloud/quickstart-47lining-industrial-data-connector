from flask import request
from flask_restplus import Namespace
from injector import inject

from api.api_utils import raise_backend_exception, BackendException
from api.v1.ApiResource import ApiResource
from api.v1.authentication.utils import login_required
from api.v1.user_management.cognito_user_manager import CognitoUserManager


def create_users_namespace(api, **kwargs):
    users_ns = Namespace('users', description='Operations related to users management')

    @users_ns.route('/register', methods=['POST'])
    class RegisterUser(ApiResource):
        @inject
        def __init__(self, user_manager: CognitoUserManager,  *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._user_manager = user_manager

        @raise_backend_exception('Unable to register user')
        @api.response(200, 'User is registered')
        @api.expect(kwargs['user_model'])
        @login_required
        def post(self):
            access_token = request.headers.get('access_token')
            self._user_manager.create_user(access_token, request.json['username'], request.json['password'],
                                           given_name=request.json['first_name'], family_name=request.json['last_name'])

    @users_ns.route('/user/<string:username>/update', methods=['POST'])
    class UpdateUser(ApiResource):
        @inject
        def __init__(self, user_manager: CognitoUserManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._user_manager = user_manager

        @raise_backend_exception('Unable to update user')
        @api.response(200, 'User is updated')
        @api.expect(kwargs['user_model'])
        @login_required
        def post(self, username):
            access_token = request.headers.get('access_token')
            update_dict = {}
            if 'last_name' in request.json:
                update_dict['family_name'] = request.json['last_name']
            if 'first_name' in request.json:
                update_dict['given_name'] = request.json['first_name']
            if 'username' in request.json:
                update_dict['preferred_username'] = request.json['preferred_username']
            self._user_manager.update_user(access_token, username, update_dict)

    @users_ns.route('/user/<string:username>/delete', methods=['POST'])
    class DeleteUser(ApiResource):
        @inject
        def __init__(self, user_manager: CognitoUserManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._user_manager = user_manager

        @raise_backend_exception('Unable to delete user')
        @api.response(200, 'User is deleted')
        @login_required
        def post(self, username):
            access_token = request.headers.get('access_token')
            current_user = request.headers.get('username')
            if username == current_user:
                raise BackendException('Cannot delete your own account')
            self._user_manager.delete_user(access_token, username)

    @users_ns.route('/users', methods=['POST'])
    class ListUsers(ApiResource):
        @inject
        def __init__(self, user_manager: CognitoUserManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._user_manager = user_manager

        @raise_backend_exception('Unable to list users')
        @login_required
        def post(self):
            access_token = request.headers.get('access_token')
            return self._user_manager.get_users(access_token)

    return users_ns
