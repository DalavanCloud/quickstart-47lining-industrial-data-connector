from flask import current_app, request
from injector import inject

from api.v1.ApiResource import ApiResource
from api.v1.authentication.utils import login_required
from workers.managed_feeds.managed_feeds_manager import ManagedFeedsManager
from flask_restplus import Namespace
from api.api_utils import raise_backend_exception


def create_structure_namespace(api, **kwargs):
    structure_ns = Namespace('structure',
                             description='Operations related to asset structure - searching, synchronizing, fetching assets and asset attributes')  # noqa

    @structure_ns.route('/search', methods=['POST'])
    class SearchStructure(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Unable to search assets')
        @api.expect(kwargs['search_assets_request'])
        @api.marshal_with(kwargs['search_assets_response'], code=200,
                          description='Assets matching criteria are returned')
        @login_required
        def post(self):
            """
            Search assets matching specified criteria
            """
            data = self._feed_manager.search_assets(
                filters=request.json['filters'],
                page=request.json.get('page', 0),
                page_size=request.json.get('page_size', 5)
            )
            return data

    @structure_ns.route('/sync', methods=['POST'])
    class SyncStructure(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Cannot send structure sync request')
        @api.response(200, 'Structure sync request is sent')
        @login_required
        def post(self):
            """
            Send asset structure synchronization request
            """
            s3_bucket = current_app.config['CURATED_DATASETS_BUCKET_NAME']
            database = self._feed_manager.get_settings().get('as_db_name', 'default')
            self._feed_manager.send_sync_as_request(s3_bucket, database)
            return 'OK', 200

    @structure_ns.route('/asset-children', methods=['POST'])
    class AssetChildren(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Unable to load assets')
        @api.expect(kwargs['asset_children_request'])
        @api.marshal_with(kwargs['asset_children_response'], code=200)
        @login_required
        def post(self):
            """
            Fetch assets - children of specified asset
            """
            data = self._feed_manager.get_asset_children(request.json['parent_asset_id'])
            return {'assets': data}

    @structure_ns.route('/asset-attributes', methods=['POST'])
    class AssetAttributes(ApiResource):
        @inject
        def __init__(self, feed_manager: ManagedFeedsManager, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._feed_manager = feed_manager

        @raise_backend_exception('Unable to search assets')
        @api.expect(kwargs['asset_attributes_request'])
        @api.marshal_with(kwargs['asset_attributes_response'], code=200,
                          description='Asset attributes matching search criteria are returned')
        @login_required
        def post(self):
            """
            Fetch attributes of specified asset that match search filters
            """
            data = self._feed_manager.search_asset_attributes(
                request.json['asset_id'], request.json['filters'])
            return data

    return structure_ns
