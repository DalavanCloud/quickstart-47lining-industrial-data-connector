from io import BytesIO
from operator import itemgetter
from time import sleep

from freezegun import freeze_time

from tests.fixtures import *


@freeze_time('2016-01-02 11:12:13')
def test_update_pi_points_status(managed_feeds_dynamo_dao, pi_points_dynamo_table):
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1'})
    pi_points_dynamo_table.put_item(Item={'pi_point': 'point1'})
    pi_points = ['point1', 'point2']

    managed_feeds_dynamo_dao.update_pi_points_status(pi_points, 'pending')

    points = pi_points_dynamo_table.scan()['Items']
    sorted_points = sorted(points, key=itemgetter('pi_point'))

    assert sorted_points == [
        {'update_timestamp': '2016-01-02T11:12:13', 'subscription_status': 'pending', 'pi_point': 'point1'},
        {'update_timestamp': '2016-01-02T11:12:13', 'subscription_status': 'pending', 'pi_point': 'point2'}
    ]


def test_get_latest_af_structure(managed_feeds_dynamo_dao, events_status_table, s3_resource):
    events_status_table.put_item(
        Item={
            'id': '1',
            'update_timestamp': '2000-11-11T22:22:22',
            'event_type': 'sync_af',
            'database': 'database',
            's3_bucket': 'bucket1',
            's3_key': 'af_structure.json',
            'status': 'success'
        }
    )
    events_status_table.put_item(
        Item={
            'id': '2',
            'update_timestamp': '2001-01-01T22:22:22',
            'event_type': 'sync_af',
            'database': 'database',
            's3_bucket': 'bucket2',
            's3_key': 'af_structure.json',
            'status': 'success'
        }
    )
    events_status_table.put_item(
        Item={
            'id': '3',
            'update_timestamp': '2002-01-01T22:22:22',
            'event_type': 'sync_af',
            'database': 'database',
            's3_bucket': 'bucket3',
            's3_key': 'af_structure.json',
            'status': 'failure'
        }
    )
    events_status_table.put_item(
        Item={
            'id': '4',
            'update_timestamp': '2017-01-01T22:22:22',
            'event_type': 'sync_af',
            'database': 'otherdatabase',
            's3_bucket': 'bucket4',
            's3_key': 'af_structure.json',
            'status': 'success'
        }
    )
    s3_resource.Bucket('bucket2').upload_fileobj(
        BytesIO(b'{"af_structure": "test"}'),
        'af_structure.json'
    )

    af_structure = managed_feeds_dynamo_dao.get_latest_af_structure('database')

    assert af_structure == {'af_structure': 'test'}


def test_get_latest_af_structure_without_data(managed_feeds_dynamo_dao):
    af_structure = managed_feeds_dynamo_dao.get_latest_af_structure('database')

    assert af_structure is None


def test_get_event_by_id(managed_feeds_dynamo_dao, events_status_table):
    events_status_table.put_item(Item={'id': '1', 'key': 'test'})

    event = managed_feeds_dynamo_dao.get_event_by_id('1')

    assert event == {'id': '1', 'key': 'test'}
