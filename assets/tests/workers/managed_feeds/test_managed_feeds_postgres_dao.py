import datetime
import json
from io import BytesIO
from operator import itemgetter


from freezegun import freeze_time
from model.models import Settings, Asset, Attribute
from tests.fixtures import *


def test_get_asset_children(managed_feeds_postgres_dao, postgres_session):

    postgres_session.add(
        Asset(
            id="\\\\EC2AMAZ-0EE3VGR\\NuGreen",
            parent_id=None,
            name="NuGreen",
            is_leaf=False
        )
    )
    postgres_session.add(
        Asset(
            id="\\\\EC2AMAZ-0EE3VGR\\NuGreen\\Houston",
            parent_id="\\\\EC2AMAZ-0EE3VGR\\NuGreen",
            name="Houston",
            is_leaf=True
        )
    )
    children = managed_feeds_postgres_dao.get_asset_children(r'\\EC2AMAZ-0EE3VGR\NuGreen')

    assert children == [
        {
            "id": "\\\\EC2AMAZ-0EE3VGR\\NuGreen\\Houston",
            "name": "Houston",
            "isLeaf": True
        }
    ]


def test_search_assets_without_filters(managed_feeds_postgres_dao, postgres_session):
    postgres_session.add_all(
        [
            Asset(
                name="Root",
                id=r"\\Root",
                description=None,
                template=None,
                categories=["cat1"],
                parent_id=None,
                is_leaf=False
            ),
            Asset(
                name="Child 1",
                id=r"\\Root\Child 1",
                description=None,
                template=None,
                categories=["cat1", "cat2"],
                parent_id=r"\\Root",
                is_leaf=False
            ),
            Asset(
                name="Subchild 1",
                id=r"\\Root\Child 1\Subchild 1",
                description=None,
                template=None,
                categories=["cat2", "cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Asset(
                name="Subchild 2",
                id=r"\\Root\Child 1\Subchild 2",
                description=None,
                template=None,
                categories=["cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Attribute(
                name="test attr",
                id=r"\\Root\Child 1|test attr",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="test attr2",
                id=r"\\Root\Child 1|test attr2",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="subchild 1 attr",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 1 attr2",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr2",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=None
            ),
            Attribute(
                name="subchild 2 attr",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI",
                categories=["attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr2",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr2",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr3",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr3",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            )
        ]
    )

    search_results = managed_feeds_postgres_dao.search_assets(filters=[])

    assert search_results['pi_points_total_count'] == 2
    assert search_results['total_count'] == 4


def test_search_assets_by_name_with_1_pi_point(managed_feeds_postgres_dao, postgres_session):
    postgres_session.add_all(
        [
            Asset(
                name="Root",
                id=r"\\Root",
                description=None,
                template=None,
                categories=["cat1"],
                parent_id=None,
                is_leaf=False
            ),
            Asset(
                name="Child 1",
                id=r"\\Root\Child 1",
                description=None,
                template=None,
                categories=["cat1", "cat2"],
                parent_id=r"\\Root",
                is_leaf=False
            ),
            Asset(
                name="Subchild 1",
                id=r"\\Root\Child 1\Subchild 1",
                description=None,
                template=None,
                categories=["cat2", "cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Asset(
                name="Subchild 2",
                id=r"\\Root\Child 1\Subchild 2",
                description=None,
                template=None,
                categories=["cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Attribute(
                name="test attr",
                id=r"\\Root\Child 1|test attr",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="test attr2",
                id=r"\\Root\Child 1|test attr2",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="subchild 1 attr",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 1 attr2",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr2",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=None
            ),
            Attribute(
                name="subchild 2 attr",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI",
                categories=["attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr2",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr2",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr3",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr3",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            )
        ]
    )

    search_results = managed_feeds_postgres_dao.search_assets(
        filters=[
            {
                'type': 'asset',
                'parameter': 'name',
                'value': 'Subchild 1'
            }
        ]
    )

    expected = {
        'assets': [
            {
                'id': '\\\\Root\\Child 1\\Subchild 1',
                'name': 'Subchild 1',
                'description': None,
                'template': None,
                'parent_id': '\\\\Root\\Child 1',
                'is_leaf': True,
                'categories': ['cat2', 'cat3']
            }
        ],
        'pi_points_total_count': 1,
        'total_count': 1
    }
    assert search_results == expected


def test_search_assets_by_name_with_2_pi_points(managed_feeds_postgres_dao, postgres_session):
    postgres_session.add_all(
        [
            Asset(
                name="Root",
                id=r"\\Root",
                description=None,
                template=None,
                categories=["cat1"],
                parent_id=None,
                is_leaf=False
            ),
            Asset(
                name="Child 1",
                id=r"\\Root\Child 1",
                description=None,
                template=None,
                categories=["cat1", "cat2"],
                parent_id=r"\\Root",
                is_leaf=False
            ),
            Asset(
                name="Subchild 1",
                id=r"\\Root\Child 1\Subchild 1",
                description=None,
                template=None,
                categories=["cat2", "cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Asset(
                name="Subchild 2",
                id=r"\\Root\Child 1\Subchild 2",
                description=None,
                template=None,
                categories=["cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Attribute(
                name="test attr",
                id=r"\\Root\Child 1|test attr",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="test attr2",
                id=r"\\Root\Child 1|test attr2",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="subchild 1 attr",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 1 attr2",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr2",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=None
            ),
            Attribute(
                name="subchild 2 attr",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI",
                categories=["attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr2",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr2",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr3",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr3",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            )
        ]
    )

    search_results = managed_feeds_postgres_dao.search_assets(
        filters=[
            {
                'type': 'asset',
                'parameter': 'name',
                'value': 'Subchild 2'
            }
        ]
    )

    expected = {
        'assets': [
            {
                'id': '\\\\Root\\Child 1\\Subchild 2',
                'name': 'Subchild 2',
                'description': None,
                'template': None,
                'parent_id': '\\\\Root\\Child 1',
                'is_leaf': True,
                'categories': ['cat3']
            }
        ],
        'pi_points_total_count': 2,
        'total_count': 1
    }
    assert search_results == expected


def test_search_assets_by_name_with_wildcard(managed_feeds_postgres_dao, postgres_session):
    postgres_session.add_all(
        [
            Asset(
                name="Root",
                id=r"\\Root",
                description=None,
                template=None,
                categories=["cat1"],
                parent_id=None,
                is_leaf=False
            ),
            Asset(
                name="Child 1",
                id=r"\\Root\Child 1",
                description=None,
                template=None,
                categories=["cat1", "cat2"],
                parent_id=r"\\Root",
                is_leaf=False
            ),
            Asset(
                name="Subchild 1",
                id=r"\\Root\Child 1\Subchild 1",
                description=None,
                template=None,
                categories=["cat2", "cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Asset(
                name="Subchild 2",
                id=r"\\Root\Child 1\Subchild 2",
                description=None,
                template=None,
                categories=["cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Attribute(
                name="test attr",
                id=r"\\Root\Child 1|test attr",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="test attr2",
                id=r"\\Root\Child 1|test attr2",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="subchild 1 attr",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 1 attr2",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr2",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=None
            ),
            Attribute(
                name="subchild 2 attr",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI",
                categories=["attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr2",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr2",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr3",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr3",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            )
        ]
    )

    search_results = managed_feeds_postgres_dao.search_assets(
        filters=[
            {
                'type': 'asset',
                'parameter': 'name',
                'value': 'Subchild*'
            }
        ]
    )

    expected = {
        'assets': [
            {
                'categories': ['cat2', 'cat3'],
                'description': None,
                'id': '\\\\Root\\Child 1\\Subchild 1',
                'is_leaf': True,
                'name': 'Subchild 1',
                'parent_id': '\\\\Root\\Child 1',
                'template': None
            },
            {
                'categories': ['cat3'],
                'description': None,
                'id': '\\\\Root\\Child 1\\Subchild 2',
                'is_leaf': True,
                'name': 'Subchild 2',
                'parent_id': '\\\\Root\\Child 1',
                'template': None
            }
        ],
        'pi_points_total_count': 2,
        'total_count': 2
    }

    assert search_results == expected


def test_search_assets_by_category(managed_feeds_postgres_dao, postgres_session):
    postgres_session.add_all(
        [
            Asset(
                name="Root",
                id=r"\\Root",
                description=None,
                template=None,
                categories=["cat1"],
                parent_id=None,
                is_leaf=False
            ),
            Asset(
                name="Child 1",
                id=r"\\Root\Child 1",
                description=None,
                template=None,
                categories=["cat1", "cat2"],
                parent_id=r"\\Root",
                is_leaf=False
            ),
            Asset(
                name="Subchild 1",
                id=r"\\Root\Child 1\Subchild 1",
                description=None,
                template=None,
                categories=["cat2", "cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Asset(
                name="Subchild 2",
                id=r"\\Root\Child 1\Subchild 2",
                description=None,
                template=None,
                categories=["cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Attribute(
                name="test attr",
                id=r"\\Root\Child 1|test attr",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="test attr2",
                id=r"\\Root\Child 1|test attr2",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="subchild 1 attr",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 1 attr2",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr2",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=None
            ),
            Attribute(
                name="subchild 2 attr",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI",
                categories=["attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr2",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr2",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr3",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr3",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            )
        ]
    )

    search_results = managed_feeds_postgres_dao.search_assets(
        filters=[
            {
                'type': 'asset',
                'parameter': 'category',
                'value': 'cat2'
            }
        ]
    )

    expected = {
        'assets': [
            {
                'categories': ['cat1', 'cat2'],
                'description': None,
                'id': '\\\\Root\\Child 1',
                'is_leaf': False,
                'name': 'Child 1',
                'parent_id': '\\\\Root',
                'template': None
            },
            {
                'categories': ['cat2', 'cat3'],
                'description': None,
                'id': '\\\\Root\\Child 1\\Subchild 1',
                'is_leaf': True,
                'name': 'Subchild 1',
                'parent_id': '\\\\Root\\Child 1',
                'template': None
            }
        ],
        'pi_points_total_count': 1,
        'total_count': 2
    }

    assert search_results == expected


def test_search_assets_by_attribute_name(managed_feeds_postgres_dao, postgres_session):
    postgres_session.add_all(
        [
            Asset(
                name="Root",
                id=r"\\Root",
                description=None,
                template=None,
                categories=["cat1"],
                parent_id=None,
                is_leaf=False
            ),
            Asset(
                name="Child 1",
                id=r"\\Root\Child 1",
                description=None,
                template=None,
                categories=["cat1", "cat2"],
                parent_id=r"\\Root",
                is_leaf=False
            ),
            Asset(
                name="Subchild 1",
                id=r"\\Root\Child 1\Subchild 1",
                description=None,
                template=None,
                categories=["cat2", "cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Asset(
                name="Subchild 2",
                id=r"\\Root\Child 1\Subchild 2",
                description=None,
                template=None,
                categories=["cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Attribute(
                name="test attr",
                id=r"\\Root\Child 1|test attr",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="test attr2",
                id=r"\\Root\Child 1|test attr2",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="subchild 1 attr",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 1 attr2",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr2",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=None
            ),
            Attribute(
                name="subchild 2 attr",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI",
                categories=["attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr2",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr2",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr3",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr3",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            )
        ]
    )

    search_results = managed_feeds_postgres_dao.search_assets(
        filters=[
            {
                'type': 'attribute',
                'parameter': 'name',
                'value': 'subchild 1 attr'
            }
        ]
    )

    expected = {
        'assets': [
            {
                'categories': ['cat2', 'cat3'],
                'description': None,
                'id': '\\\\Root\\Child 1\\Subchild 1',
                'is_leaf': True,
                'name': 'Subchild 1',
                'parent_id': '\\\\Root\\Child 1',
                'template': None
            }
        ],
        'pi_points_total_count': 1,
        'total_count': 1
    }

    assert search_results == expected


def test_search_asset_attributes_by_attribute_name(managed_feeds_postgres_dao, postgres_session):
    postgres_session.add_all(
        [
            Asset(
                name="Root",
                id=r"\\Root",
                description=None,
                template=None,
                categories=["cat1"],
                parent_id=None,
                is_leaf=False
            ),
            Asset(
                name="Child 1",
                id=r"\\Root\Child 1",
                description=None,
                template=None,
                categories=["cat1", "cat2"],
                parent_id=r"\\Root",
                is_leaf=False
            ),
            Asset(
                name="Subchild 1",
                id=r"\\Root\Child 1\Subchild 1",
                description=None,
                template=None,
                categories=["cat2", "cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Asset(
                name="Subchild 2",
                id=r"\\Root\Child 1\Subchild 2",
                description=None,
                template=None,
                categories=["cat3"],
                parent_id=r"\\Root\Child 1",
                is_leaf=True
            ),
            Attribute(
                name="test attr",
                id=r"\\Root\Child 1|test attr",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="test attr2",
                id=r"\\Root\Child 1|test attr2",
                asset_id=r"\\Root\Child 1",
                type=None,
                pi_point=None,
                categories=["attr cat1", "attr cat2"]
            ),
            Attribute(
                name="subchild 1 attr",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 1 attr2",
                id=r"\\Root\Child 1\Subchild 1|subchild 1 attr2",
                asset_id=r"\\Root\Child 1\Subchild 1",
                type=None,
                pi_point="PI",
                categories=None
            ),
            Attribute(
                name="subchild 2 attr",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI",
                categories=["attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr2",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr2",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            ),
            Attribute(
                name="subchild 2 attr3",
                id=r"\\Root\Child 1\Subchild 2|subchild 2 attr3",
                asset_id=r"\\Root\Child 1\Subchild 2",
                type=None,
                pi_point="PI2",
                categories=["attr cat2", "attr cat3"]
            )
        ]
    )

    search_results = managed_feeds_postgres_dao.search_asset_attributes(
        asset_id=r'\\Root\Child 1',
        filters=[
            {
                'type': 'attribute',
                'parameter': 'name',
                'value': 'test attr'
            }
        ]
    )

    expected = {
        'attributes': [
            {
                'asset_id': '\\\\Root\\Child 1',
                'categories': ['attr cat1', 'attr cat2'],
                'description': None,
                'id': '\\\\Root\\Child 1|test attr',
                'name': 'test attr',
                'pi_point': None,
                'type': None,
                'subscription_status': None
            }
        ],
        'pi_points_total_count': 0,
        'total_count': 1
    }

    assert search_results == expected


def test_get_settings(managed_feeds_postgres_dao, postgres_session):
    postgres_session.add(Settings(name='key', value='value'))

    result = managed_feeds_postgres_dao.get_settings()

    assert result == {'key': 'value'}


def test_save_settings(managed_feeds_postgres_dao, postgres_session):
    settings = {'key': 'value'}

    managed_feeds_postgres_dao.save_settings(settings)

    result = managed_feeds_postgres_dao.get_settings()

    assert result == {'key': 'value'}