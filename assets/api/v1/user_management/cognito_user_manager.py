from botocore.exceptions import ClientError, ParamValidationError
from warrant import Cognito

from api.v1.user_management.exceptions import CognitoException


class CognitoUserManager():
    """
    Provides user management via Amazon Cognito using specific user pool and app client
    """
    def __init__(self, cognito_user_pool_id, cognito_client_id, cognito_client_secret):
        self._cognito_user_pool_id = cognito_user_pool_id
        self._cognito_client_id = cognito_client_id
        self._cognito_client_secret = cognito_client_secret
        self._region = self._cognito_user_pool_id.split('_')[0]
        self._attr_map = {'given_name': 'first_name', 'family_name': 'last_name'}
        self._region = self._cognito_user_pool_id.split('_')[0]

    def create_user(self, access_token, username, password, **kwargs):
        try:
            u = Cognito(self._cognito_user_pool_id, self._cognito_client_id, access_token=access_token,
                        client_secret=self._cognito_client_secret, username=username, user_pool_region=self._region)
            u.add_base_attributes(**kwargs)
            u.register(username, password)
            u.admin_confirm_sign_up(username)
            # because it can be set after confirmation only
            self.update_user(access_token, username, {"preferred_username": username})
        except ClientError as e:
            raise CognitoException.from_client_error(e)
        except ParamValidationError as e:
            raise CognitoException(e.kwargs['report'], e)

    def get_users(self, access_token):
        u = Cognito(self._cognito_user_pool_id, self._cognito_client_id, access_token=access_token,
                    client_secret=self._cognito_client_secret, user_pool_region=self._region)
        user_objects = u.get_users(attr_map=self._attr_map)
        users = [self._get_user_from_object(user_object) for user_object in user_objects]
        return users

    def update_user(self, access_token, username, update_dict):
        try:
            u = Cognito(self._cognito_user_pool_id, self._cognito_client_id, access_token=access_token,
                        client_secret=self._cognito_client_secret, username=username, user_pool_region=self._region)
            u.admin_update_profile(update_dict, attr_map=self._attr_map)
        except ClientError as e:
            raise CognitoException.from_client_error(e)
        except ParamValidationError as e:
            raise CognitoException(e.kwargs['report'], e)

    def delete_user(self, access_token, username):
        u = Cognito(self._cognito_user_pool_id, self._cognito_client_id, access_token=access_token,
                    client_secret=self._cognito_client_secret, username=username, user_pool_region=self._region)
        u.admin_delete_user()

    def _get_user_from_object(self, user):
        return {
            "username": user.username,
            "preferred_username": user.preferred_username,
            "first_name": user.first_name,
            "last_name": user.last_name
        }
