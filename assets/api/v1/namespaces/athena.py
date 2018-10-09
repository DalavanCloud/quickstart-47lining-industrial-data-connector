from flask import current_app
from flask_restplus import Namespace

from api.api_utils import raise_backend_exception
from api.v1.ApiResource import ApiResource
from api.v1.authentication.utils import login_required


# TODO: After adding 'data_transport_service' it is no longer AthenaInfo but more general - DeploymentInfo.
# we should change names from 'athena' to for example 'deployment'
def create_athena_info_namespace(api, **kwargs):
    athena_ns = Namespace('athena',
                          description='Provide athena information - URL, database name, text and numeric table names')

    @athena_ns.route('/info', methods=['GET'])
    class AthenaInfo(ApiResource):

        @api.marshal_with(kwargs['athena_response'], code=200,
                          description='Athena URL, database name and table names info is returned')
        @raise_backend_exception('Cannot get Athena table name')
        @login_required
        def get(self):
            """
            Return athena URL, database name and table names
            """
            athena_database = current_app.config['ATHENA_DATABASE_NAME']
            athena_numeric_table_name = current_app.config['ATHENA_NUMERIC_TABLE_NAME']
            athena_text_table_name = current_app.config['ATHENA_TEXT_TABLE_NAME']
            data_transport_service = current_app.config['DATA_TRANSPORT_SERVICE']
            connector_type = current_app.config['CONNECTOR_TYPE']
            athena_url = "https://{}.console.aws.amazon.com/athena/home?region={}".format(
                current_app.config['REGION'],
                current_app.config['REGION']
            )

            return {
                'url': athena_url,
                'database_name': athena_database,
                'numeric_table_name': athena_numeric_table_name,
                'text_table_name': athena_text_table_name,
                'data_transport_service': data_transport_service,
                'connector_type': connector_type
            }
    return athena_ns
