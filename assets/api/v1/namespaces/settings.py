from flask import request
from flask_restplus import Namespace
from injector import inject

from api.api_utils import raise_backend_exception
from api.v1.ApiResource import ApiResource
from api.v1.authentication.utils import login_required

from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager


def create_settings_namespace(api, **kwargs):
    settings_ns = Namespace('settings', description='Get or save global settings of deployment')

    @settings_ns.route('/load', methods=['GET'])
    class LoadSettings(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Unable to load settings')
        @api.marshal_with(kwargs['settings_model'], code=200, description='Current settings are returned')
        @login_required
        def get(self):
            """
            Get settings
            """
            settings = self._feed_manager.get_settings()
            return settings

    @settings_ns.route('/save', methods=['POST'])
    class SaveSettings(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Unable to save settings')
        @api.response(200, 'Settings are saved')
        @api.expect(kwargs['settings_model'])
        @login_required
        def post(self):
            """
            Save settings
            """
            self._feed_manager.save_settings(request.json)
            return 'OK', 200

    return settings_ns
