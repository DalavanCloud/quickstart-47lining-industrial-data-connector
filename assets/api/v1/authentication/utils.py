from botocore.exceptions import ClientError
from flask import request

from api.api_utils import BackendException


def login_required(fun):
    def wrapper(self, *args, **kwargs):

        headers = request.headers
        if 'id_token' not in headers or 'refresh_token' not in headers or 'access_token' not in headers \
                or 'username' not in headers:
            raise BackendException("Not logged in", status_code=403)
        try:
            self._authenticator.get_user(
                id_token=headers['id_token'],
                refresh_token=headers['refresh_token'],
                access_token=headers['access_token'],
                username=request.headers['username']
            )
        except(ClientError):
            raise BackendException("Not logged in", status_code=403)
        return fun(self, *args, **kwargs)
    return wrapper
