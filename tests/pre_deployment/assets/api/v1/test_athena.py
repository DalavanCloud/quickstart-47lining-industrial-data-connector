from flask import current_app

from tests.pre_deployment.assets.api.v1.utils import parse_response


def test_athena_info(api_test_client):
    athena_database = 'database'
    athena_numeric_table_name = 'numeric_table'
    athena_text_table_name = 'text_table'
    data_transport_service = 'Amazon Kinesis'
    connector_type = 'PI'
    current_app.config['ATHENA_DATABASE_NAME'] = athena_database
    current_app.config['ATHENA_NUMERIC_TABLE_NAME'] = athena_numeric_table_name
    current_app.config['ATHENA_TEXT_TABLE_NAME'] = athena_text_table_name
    current_app.config['REGION'] = 'region'
    current_app.config['DATA_TRANSPORT_SERVICE'] = data_transport_service
    current_app.config['CONNECTOR_TYPE'] = connector_type

    response = api_test_client.get(
        '/api/v1/athena/info',
        headers={'id_token': '', 'refresh_token': '', 'access_token': '', 'username': ''}
    )
    assert parse_response(response).response == {
        'url': "https://region.console.aws.amazon.com/athena/home?region=region",
        'database_name': athena_database,
        'numeric_table_name': athena_numeric_table_name,
        'text_table_name': athena_text_table_name,
        'connector_type': connector_type,
        'data_transport_service': data_transport_service
    }
