import pytest

from model.wonderware.models import Asset, Attribute, Settings


@pytest.fixture()
def get_example_asset_tree():
    return [
        Asset(
            name='Historian System',
            id=r'\\Historian System',
            parent_id=None,
            is_leaf=False,
        ),
        Asset(
            name='EC2AMAZ-R9C2RFF',
            id=r'\\Historian System\EC2AMAZ-R9C2RFF',
            parent_id=r'\\Historian System',
            is_leaf=False,
        ),
        Asset(
            name='EC2AMAZ-R9C2RFF_2',
            id=r'\\Historian System\EC2AMAZ-R9C2RFF_2',
            parent_id=r'\\Historian System',
            is_leaf=False,
        ),
        Asset(
            name='SysDrv',
            id=r'\\Historian System\EC2AMAZ-R9C2RFF\SysDrv',
            parent_id=r'\\Historian System\EC2AMAZ-R9C2RFF',
            is_leaf=False,
        ),
        Asset(
            name='Topic1',
            id=r'\\Historian System\EC2AMAZ-R9C2RFF\SysDrv|Topic1',
            parent_id=r'\\Historian System\EC2AMAZ-R9C2RFF\SysDrv',
            is_leaf=True,
        ),
        Attribute(
            name='TagName1',
            id=r'\\Historian System\EC2AMAZ-R9C2RFF\SysDrv|Topic1!\TagName1',
            asset_id=r'\\Historian System\EC2AMAZ-R9C2RFF\SysDrv|Topic1',
            feed='tag_id',
            description='tag_description',
            type='tag_type',
            uom='engineeringUnit',
            item_name=None,
        ),
        Attribute(
            name='TagName2',
            id=r'\\Historian System\EC2AMAZ-R9C2RFF\SysDrv|Topic1!ItemName2\TagName2',
            asset_id=r'\\Historian System\EC2AMAZ-R9C2RFF\SysDrv|Topic1',
            feed='TagName2',
            description='tag_description_2',
            type='tag_type_2',
            uom='engineeringUnit_2',
            item_name='ItemName2',
        )
    ]


def test_get_asset_children(managed_feeds_postgres_dao_wonderware, postgres_session_wonderware):
    asset_1 = Asset(
        name='Historian System',
        id=r'\\Historian System',
        parent_id=None,
        is_leaf=False,
    )

    asset_2 = Asset(
        name='EC2AMAZ-R9C2RFF',
        id=r'\\Historian System\EC2AMAZ-R9C2RFF',
        parent_id=r'\\Historian System',
        is_leaf=True,
    )

    postgres_session_wonderware.add(asset_1)
    postgres_session_wonderware.add(asset_2)

    children = managed_feeds_postgres_dao_wonderware.get_asset_children(r'\\Historian System')

    assert children == [
        {
            "id": "\\\\Historian System\\EC2AMAZ-R9C2RFF",
            "name": "EC2AMAZ-R9C2RFF",
            "is_leaf": True,
        }
    ]


def test_search_assets_without_filters(managed_feeds_postgres_dao_wonderware, postgres_session_wonderware,
                                       get_example_asset_tree):
    postgres_session_wonderware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_wonderware.search_assets(filters=[])

    assert search_results['feeds_total_count'] == 2
    assert search_results['total_count'] == 5


def test_search_assets_by_name(managed_feeds_postgres_dao_wonderware, postgres_session_wonderware,
                               get_example_asset_tree):
    postgres_session_wonderware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_wonderware.search_assets(
        filters=[
            {
                'type': 'asset',
                'parameter': 'name',
                'value': 'SysDrv'
            }
        ]
    )

    expected = {
        'assets': [
            {
                'id': '\\\\Historian System\\EC2AMAZ-R9C2RFF\\SysDrv',
                'name': 'SysDrv',
                'description': None,
                'parent_id': '\\\\Historian System\\EC2AMAZ-R9C2RFF',
                'is_leaf': False,
            }
        ],
        'feeds_total_count': 0,
        'total_count': 1
    }
    assert search_results == expected


def test_search_assets_by_name_with_wildcard(managed_feeds_postgres_dao_wonderware, postgres_session_wonderware,
                                             get_example_asset_tree):
    postgres_session_wonderware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_wonderware.search_assets(
        filters=[
            {
                'type': 'asset',
                'parameter': 'name',
                'value': 'EC2AMAZ-R9C2RFF*'
            }
        ]
    )

    expected = {
        'assets': [
            {
                'description': None,
                'id': '\\\\Historian System\\EC2AMAZ-R9C2RFF',
                'is_leaf': False,
                'name': 'EC2AMAZ-R9C2RFF',
                'parent_id': '\\\\Historian System',
            },
            {
                'description': None,
                'id': '\\\\Historian System\\EC2AMAZ-R9C2RFF_2',
                'is_leaf': False,
                'name': 'EC2AMAZ-R9C2RFF_2',
                'parent_id': '\\\\Historian System',
            }
        ],
        'feeds_total_count': 0,
        'total_count': 2
    }

    assert search_results == expected


def test_search_assets_by_attribute_name(managed_feeds_postgres_dao_wonderware, postgres_session_wonderware,
                                         get_example_asset_tree):
    postgres_session_wonderware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_wonderware.search_assets(
        filters=[
            {
                'type': 'attribute',
                'parameter': 'name',
                'value': 'TagName1'
            }
        ]
    )

    expected = {
        'assets': [
            {
                'description': None,
                'id': '\\\\Historian System\\EC2AMAZ-R9C2RFF\\SysDrv|Topic1',
                'is_leaf': True,
                'name': 'Topic1',
                'parent_id': '\\\\Historian System\EC2AMAZ-R9C2RFF\SysDrv',
            }
        ],
        'feeds_total_count': 1,
        'total_count': 1
    }

    assert search_results == expected


def test_search_asset_attributes_by_attribute_name(managed_feeds_postgres_dao_wonderware, postgres_session_wonderware,
                                                   get_example_asset_tree):
    postgres_session_wonderware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_wonderware.search_asset_attributes(
        asset_id=r'\\Historian System\EC2AMAZ-R9C2RFF\SysDrv|Topic1',
        filters=[
            {
                'type': 'attribute',
                'parameter': 'name',
                'value': 'TagName1'
            }
        ]
    )

    expected = {
        'attributes': [
            {
                'asset_id': '\\\\Historian System\EC2AMAZ-R9C2RFF\SysDrv|Topic1',
                'description': 'tag_description',
                'id': '\\\\Historian System\EC2AMAZ-R9C2RFF\SysDrv|Topic1!\TagName1',
                'name': 'TagName1',
                'feed': 'tag_id',
                'type': 'tag_type',
                'subscription_status': None,
                'uom': 'engineeringUnit',
                'item_name': None
            }
        ],
        'feeds_total_count': 1,
        'total_count': 1
    }

    assert search_results == expected


def test_get_settings(managed_feeds_postgres_dao_wonderware, postgres_session_wonderware):
    postgres_session_wonderware.add(Settings(name='key', value='value'))

    result = managed_feeds_postgres_dao_wonderware.get_settings()

    assert result == {'key': 'value'}


def test_save_settings(managed_feeds_postgres_dao_wonderware):
    settings = {'key': 'value'}

    managed_feeds_postgres_dao_wonderware.save_settings(settings)

    result = managed_feeds_postgres_dao_wonderware.get_settings()

    assert result == {'key': 'value'}
