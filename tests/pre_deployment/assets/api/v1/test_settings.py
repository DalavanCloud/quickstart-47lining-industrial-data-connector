import json

from model.pi.models import Settings
from tests.pre_deployment.assets.api.v1.utils import parse_response


def test_settings_load(api_test_client, postgres_session):
    postgres_session.add_all([
        Settings(name='as_db_name', value='val1'),
        Settings(name='deployment_name', value='val2'),
        Settings(name='feed_group_size', value='1000'),
        Settings(name='time_window_days', value='1')
    ])

    response = api_test_client.get(
        '/api/v1/settings/load',
        headers={'id_token': '', 'refresh_token': '', 'access_token': '', 'username': ''}
    )

    assert parse_response(response).response == {
        'as_db_name': 'val1',
        'deployment_name': 'val2',
        'feed_group_size': '1000',
        'time_window_days': '1'
    }


def test_settings_save(api_test_client):
    request = {
        "as_db_name": "new as db name",
        "deployment_name": "new deployment name",
        "feed_group_size": "2000",
        "time_window_days": "2"
    }

    response_save = api_test_client.post(
        '/api/v1/settings/save',
        data=json.dumps(request),
        content_type='application/json',
        headers={'id_token': '', 'refresh_token': '', 'access_token': '', 'username': ''}
    )
    response_load = api_test_client.get(
        'api/v1/settings/load',
        headers={'id_token': '', 'refresh_token': '', 'access_token': '', 'username': ''}
    )

    assert parse_response(response_save).status_code == 200
    assert parse_response(response_load).response == request
