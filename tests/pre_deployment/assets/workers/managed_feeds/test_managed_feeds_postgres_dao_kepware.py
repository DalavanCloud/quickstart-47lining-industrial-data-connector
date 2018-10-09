import pytest

from model.kepware.models import Asset, Attribute, Settings


@pytest.fixture()
def get_example_asset_tree():
    return [
        Asset(
            name='Channel1',
            id=r'\\Channel1',
            description='channel1_description',
            parent_id=None,
            is_leaf=False,
        ),
        Asset(
            name='Device1',
            id=r'\\Channel1\Device1',
            description='device1_description',
            parent_id=r'\\Channel1',
            is_leaf=False,
        ),
        Asset(
            name='Tag1',
            id=r'\\Channel1\Device1\Tag1',
            description='tag1_description',
            parent_id=r'\\Channel1\Device1',
            is_leaf=True,
        ),
        Asset(
            name='Tag2',
            id=r'\\Channel1\Device1\Tag2',
            description='tag2_description',
            parent_id=r'\\Channel1\Device1',
            is_leaf=True,
        ),
        Attribute(
            name='Value',
            id=r'\\Channel1\Device1\Tag1\Value',
            asset_id=r'\\Channel1\Device1\Tag1',
            feed='Value',
        ),
        Attribute(
            name='Address',
            id=r'\\Channel1\Device1\Tag1\Address',
            asset_id=r'\\Channel1\Device1\Tag1',
            feed='Address'
        )
    ]


def test_get_asset_children(managed_feeds_postgres_dao_kepware, postgres_session_kepware):
    asset_1 = Asset(
        name='Channel1',
        id=r'\\Channel1',
        parent_id=None,
        is_leaf=False,
    )

    asset_2 = Asset(
        name='Device1',
        id=r'\\Channel1\Device1',
        parent_id=r'\\Channel1',
        is_leaf=True,
    )

    postgres_session_kepware.add(asset_1)
    postgres_session_kepware.add(asset_2)

    children = managed_feeds_postgres_dao_kepware.get_asset_children(r'\\Channel1')

    assert children == [
        {
            "id": "\\\\Channel1\\Device1",
            "name": "Device1",
            "is_leaf": True,
        }
    ]


def test_search_assets_without_filters(managed_feeds_postgres_dao_kepware, postgres_session_kepware,
                                       get_example_asset_tree):
    postgres_session_kepware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_kepware.search_assets(filters=[])

    assert search_results['feeds_total_count'] == 2
    assert search_results['total_count'] == 4


def test_search_assets_by_name(managed_feeds_postgres_dao_kepware, postgres_session_kepware,
                               get_example_asset_tree):
    postgres_session_kepware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_kepware.search_assets(
        filters=[
            {
                'type': 'asset',
                'parameter': 'name',
                'value': 'Tag1'
            }
        ]
    )

    expected = {
        'assets': [
            {
                "id": "\\\\Channel1\\Device1\\Tag1",
                'name': 'Tag1',
                'parent_id': "\\\\Channel1\\Device1",
                'is_leaf': True,
                'description': "tag1_description"
            }
        ],
        'feeds_total_count': 2,
        'total_count': 1
    }
    assert search_results == expected


def test_search_assets_by_name_with_wildcard(managed_feeds_postgres_dao_kepware, postgres_session_kepware,
                                             get_example_asset_tree):
    postgres_session_kepware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_kepware.search_assets(
        filters=[
            {
                'type': 'asset',
                'parameter': 'name',
                'value': 'Tag*'
            }
        ]
    )

    expected = {
        'assets': [
            {
                "id": "\\\\Channel1\\Device1\\Tag1",
                'name': 'Tag1',
                'parent_id': "\\\\Channel1\\Device1",
                'is_leaf': True,
                'description': "tag1_description"
            },
            {
                "id": "\\\\Channel1\\Device1\\Tag2",
                'name': 'Tag2',
                'parent_id': "\\\\Channel1\\Device1",
                'is_leaf': True,
                'description': "tag2_description"
            }
        ],
        'feeds_total_count': 2,
        'total_count': 2
    }

    assert search_results == expected


def test_search_assets_by_attribute_name(managed_feeds_postgres_dao_kepware, postgres_session_kepware,
                                         get_example_asset_tree):
    postgres_session_kepware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_kepware.search_assets(
        filters=[
            {
                'type': 'attribute',
                'parameter': 'name',
                'value': 'Address'
            }
        ]
    )

    expected = {
        'assets': [
            {
                "id": "\\\\Channel1\\Device1\\Tag1",
                'name': 'Tag1',
                'parent_id': "\\\\Channel1\\Device1",
                'is_leaf': True,
                'description': "tag1_description"
            }
        ],
        'feeds_total_count': 1,
        'total_count': 1
    }

    assert search_results == expected


def test_search_asset_attributes_by_attribute_name(managed_feeds_postgres_dao_kepware, postgres_session_kepware,
                                                   get_example_asset_tree):
    postgres_session_kepware.add_all(get_example_asset_tree)

    search_results = managed_feeds_postgres_dao_kepware.search_asset_attributes(
        asset_id=r'\\Channel1\Device1\Tag1',
        filters=[
            {
                'type': 'attribute',
                'parameter': 'name',
                'value': 'Value'
            }
        ]
    )

    expected_asset_id = '\\\\Channel1\\Device1\\Tag1'
    expected_id = '\\\\Channel1\\Device1\\Tag1\\Value'
    expected_name = 'Value'
    expected_feed = 'Value'

    assert search_results['attributes'][0]['asset_id'] == expected_asset_id
    assert search_results['attributes'][0]['id'] == expected_id
    assert search_results['attributes'][0]['name'] == expected_name
    assert search_results['attributes'][0]['feed'] == expected_feed


def test_get_settings(managed_feeds_postgres_dao_kepware, postgres_session_kepware):
    postgres_session_kepware.add(Settings(name='key', value='value'))

    result = managed_feeds_postgres_dao_kepware.get_settings()

    assert result == {'key': 'value'}


def test_save_settings(managed_feeds_postgres_dao_kepware):
    settings = {'key': 'value'}

    managed_feeds_postgres_dao_kepware.save_settings(settings)

    result = managed_feeds_postgres_dao_kepware.get_settings()

    assert result == {'key': 'value'}
