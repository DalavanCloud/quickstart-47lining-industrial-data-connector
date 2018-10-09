from api.v1.model.common import search_filter
from flask_restplus import fields, Model

search_assets_request = Model('SearchAssetsRequest', {
    'filters': fields.List(
        fields.Nested(
            search_filter,
            required=True
        ),
        required=True,
        description='Filter criteria'
    ),
    'page': fields.Integer(
        required=False,
        default=0,
        description='Page number in view'
    ),
    'page_size': fields.Integer(
        required=False,
        default=5,
        description='Number of items that can be displayed on single view page'
    )
})


def gen_search_assets_response(asset):
    _search_assets_response = Model('SearchAssetsResponse', {
        'assets': fields.List(
            fields.Nested(
                asset,
                required=True
            ),
            required=True
        ),
        'feeds_total_count': fields.Integer(
            required=True,
            description='Count of feeds'
        ),
        'total_count': fields.Integer(
            required=True,
            description='Count of assets'
        )
    })
    return _search_assets_response


asset_children_request = Model('AssetChildrenRequest', {
    'parent_asset_id': fields.String(
        required=True,
        description='ID of parent asset'
    )
})

asset_child = Model('AssetChild', {
    'id': fields.String(
        required=True,
        description='ID of child asset'
    ),
    'is_leaf': fields.Boolean(
        required=True,
        description='Indicates if asset does not have any children'
    ),
    'name': fields.String(
        required=True,
        description='Asset name'
    )
})

asset_children_response = Model('AssetChildrenResponse', {
    'assets': fields.List(
        fields.Nested(
            asset_child,
            required=True
        ),
        required=True,
        description='Asset children'
    )
})

asset_attributes_request = Model('AssetAttributesRequest', {
    'filters': fields.List(
        fields.Nested(
            search_filter,
            required=True
        ),
        required=True,
        description='Filter criteria'
    ),
    'asset_id': fields.String(
        required=True,
        description='Id of asset'
    )
})


def gen_asset_attributes_response(attribute):
    _asset_attributes_response = Model('AssetAttributesResponse', {
        'attributes': fields.List(
            fields.Nested(
                attribute,
                required=True
            ),
            required=True,
            description='Asset attributes'
        ),
        'feeds_total_count': fields.Integer(
            required=True,
            description='Count of feeds'
        ),
        'total_count': fields.Integer(
            required=True,
            description='Count of asset attributes'
        )
    })
    return _asset_attributes_response
