import datetime
import json
from unittest.mock import Mock

from flask import current_app

from model.pi.models import Settings, Asset, Attribute, Feed
from tests.pre_deployment.assets.api.v1.utils import parse_response


def test_structure_search(api_test_client, postgres_session):
    asset_1 = Asset(id='a1', name='a1', description='desc1', template='t1', parent_id=None, is_leaf=False,
                    categories=['c1', 'c2'])
    asset_2 = Asset(id='a2', name='a2', description='desc2', template='t2', parent_id='a1', is_leaf=False,
                    categories=['c1', 'c3'])
    asset_3 = Asset(id='a3', name='a3', description='desc3', template='t1', parent_id='a2', is_leaf=True,
                    categories=['c2'])
    postgres_session.add_all([asset_1, asset_2, asset_3])

    asset_json_1 = {'categories': ['c1', 'c2'],
                    'description': 'desc1',
                    'id': 'a1',
                    'is_leaf': False,
                    'name': 'a1',
                    'parent_id': None,
                    'template': 't1'
                    }
    asset_json_2 = {'categories': ['c1', 'c3'],
                    'description': 'desc2',
                    'id': 'a2',
                    'is_leaf': False,
                    'name': 'a2',
                    'parent_id': 'a1',
                    'template': 't2'
                    }
    asset_json_3 = {'categories': ['c2'],
                    'description': 'desc3',
                    'id': 'a3',
                    'is_leaf': True,
                    'name': 'a3', 'parent_id':
                    'a2', 'template': 't1'
                    }

    search_request_1 = {
        'page': 0, 'page_size': 10, 'filters': [{'type': 'asset', 'parameter': 'template', 'value': 't1'}]
    }
    search_request_2 = {
        'page': 0, 'page_size': 10, 'filters': [{'type': 'asset', 'parameter': 'description', 'value': 'desc3'}]
    }
    search_request_3 = {
        'page': 0, 'page_size': 10, 'filters': [{'type': 'asset', 'parameter': 'category', 'value': 'c1'}]
    }

    search_response_1 = parse_response(api_test_client.post('/api/v1/structure/search',
                                                            data=json.dumps(search_request_1),
                                                            content_type='application/json',
                                                            headers={'id_token': '', 'refresh_token': '',
                                                                     'access_token': '', 'username': ''}
                                                            ))
    search_response_2 = parse_response(api_test_client.post('/api/v1/structure/search',
                                                            data=json.dumps(search_request_2),
                                                            content_type='application/json',
                                                            headers={'id_token': '', 'refresh_token': '',
                                                                     'access_token': '', 'username': ''}))
    search_response_3 = parse_response(api_test_client.post('/api/v1/structure/search',
                                                            data=json.dumps(search_request_3),
                                                            content_type='application/json',
                                                            headers={'id_token': '', 'refresh_token': '',
                                                                     'access_token': '', 'username': ''}))

    assert search_response_1.response == {
        'feeds_total_count': 0, 'total_count': 2, 'assets': [asset_json_1, asset_json_3]
    }
    assert search_response_2.response == {
        'feeds_total_count': 0, 'total_count': 1, 'assets': [asset_json_3]
    }
    assert search_response_3.response == {
        'feeds_total_count': 0, 'total_count': 2, 'assets': [asset_json_1, asset_json_2]
    }


def test_structure_sync(api_test_client, postgres_session, managed_feeds_postgres_manager):
    managed_feeds_postgres_manager.send_sync_as_request = Mock()
    current_app.config['CURATED_DATASETS_BUCKET_NAME'] = 'bucket'
    postgres_session.add(Settings(name='as_db_name', value='val1'))

    response = parse_response(api_test_client.post('/api/v1/structure/sync',
                                                   data={},
                                                   content_type='application/json',
                                                   headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                            'username': ''}))

    assert response.status_code == 200
    managed_feeds_postgres_manager.send_sync_as_request.assert_called_once()


def test_structure_asset_children(api_test_client, postgres_session):
    asset_1 = Asset(id='a1', name='a1', description='desc1', template='t1', parent_id=None, is_leaf=False,
                    categories=['c1', 'c2'])
    asset_2 = Asset(id='a2', name='a2', description='desc2', template='t2', parent_id='a1', is_leaf=True,
                    categories=['c1', 'c3'])
    asset_3 = Asset(id='a3', name='a3', description='desc3', template='t1', parent_id='a1', is_leaf=True,
                    categories=['c2'])
    postgres_session.add_all([asset_1, asset_2, asset_3])
    asset_json_2 = {'id': 'a2', 'is_leaf': True, 'name': 'a2'}
    asset_json_3 = {'id': 'a3', 'is_leaf': True, 'name': 'a3'}
    request = {'parent_asset_id': 'a1'}

    response = parse_response(api_test_client.post('/api/v1/structure/asset-children',
                                                   data=json.dumps(request),
                                                   content_type='application/json',
                                                   headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                            'username': ''}))

    assert response.response == {'assets': [asset_json_2, asset_json_3]}


def test_structure_asset_attributes(api_test_client, postgres_session):
    asset_1 = Asset(id='a1', name='a1', description='desc1', template='t1', parent_id=None, is_leaf=False,
                    categories=['c1', 'c2'])
    feed_1 = Feed(name='feed1', subscription_status={'snapshot': 'subscribed', 'archive': 'unsubscribed'},
                  update_timestamp=datetime.datetime(2017, 1, 1))
    feed_2 = Feed(name='feed2', subscription_status={'snapshot': 'unsubscribed', 'archive': 'subscribed'},
                  update_timestamp=datetime.datetime(2017, 1, 1))
    attr_1 = Attribute(id='r1', asset_id='a1', name='attr1', description='desc1', type='type1', categories=['c1', 'c2'],
                       feed='feed1', uom='UOM1')
    attr_2 = Attribute(id='r2', asset_id='a1', name='attr2', description='desc2', type='type1', categories=['c1'],
                       feed='feed1', uom='UOM2')
    attr_3 = Attribute(id='r3', asset_id='a1', name='attr3', description='desc3', type='type2', categories=['c1'],
                       feed='feed2', uom='UOM1')
    postgres_session.add_all([asset_1, feed_1, feed_2, attr_1, attr_2, attr_3])

    attr_json_1 = {'id': 'r1',
                   'asset_id': 'a1',
                   'name': 'attr1',
                   'description': 'desc1',
                   'type': 'type1',
                   'categories': ['c1', 'c2'],
                   'feed': 'feed1',
                   'subscription_status': {'archive': 'unsubscribed', 'snapshot': 'subscribed'},
                   'uom': 'UOM1'
                   }
    attr_json_2 = {'id': 'r2',
                   'asset_id': 'a1',
                   'name': 'attr2',
                   'description': 'desc2',
                   'type': 'type1',
                   'categories': ['c1'],
                   'feed': 'feed1',
                   'subscription_status': {'archive': 'unsubscribed', 'snapshot': 'subscribed'},
                   'uom': 'UOM2'
                   }
    attr_json_3 = {'id': 'r3',
                   'asset_id': 'a1',
                   'name': 'attr3',
                   'description': 'desc3',
                   'type': 'type2',
                   'categories': ['c1'],
                   'feed': 'feed2',
                   'subscription_status': {'archive': 'subscribed', 'snapshot': 'unsubscribed'},
                   'uom': 'UOM1'
                   }

    request_1 = {'asset_id': 'a1',
                 'filters': [{'type': 'attribute', 'parameter': 'feed', 'value': 'feed1'}]
                 }
    request_2 = {'asset_id': 'a1',
                 'filters': [{'type': 'attribute', 'parameter': 'category', 'value': 'c2'},
                             {'type': 'attribute', 'parameter': 'feed', 'value': 'feed2'}]
                 }
    request_3 = {'asset_id': 'a1',
                 'filters': []
                 }

    response_1 = parse_response(api_test_client.post('/api/v1/structure/asset-attributes',
                                                     data=json.dumps(request_1),
                                                     content_type='application/json',
                                                     headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                              'username': ''}))
    response_2 = parse_response(api_test_client.post('/api/v1/structure/asset-attributes',
                                                     data=json.dumps(request_2),
                                                     content_type='application/json',
                                                     headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                              'username': ''}))
    response_3 = parse_response(api_test_client.post('/api/v1/structure/asset-attributes',
                                                     data=json.dumps(request_3),
                                                     content_type='application/json',
                                                     headers={'id_token': '', 'refresh_token': '', 'access_token': '',
                                                              'username': ''}))

    assert response_1.response == {'feeds_total_count': 1, 'total_count': 2, 'attributes': [attr_json_1, attr_json_2]}
    assert response_2.response == {'feeds_total_count': 0, 'total_count': 0, 'attributes': []}
    assert response_3.response == {'feeds_total_count': 2,
                                   'total_count': 3,
                                   'attributes': [attr_json_1, attr_json_2, attr_json_3]
                                   }
