from flask import request
from workers.managed_feeds.user_provider.UserProvider import UserProvider


class ApiUserProvider(UserProvider):
    def get_username(self):
        return request.headers['username']
