from flask_restplus import fields, Model

athena_response = Model('AthenaResponse', {
    'url': fields.String(
        required=True,
        description='Athena URL'
    ),
    'database_name': fields.String(
        required=True,
        description='Athena database name'
    ),
    'numeric_table_name': fields.String(
        required=True,
        description='Athena numeric table name'
    ),
    'text_table_name': fields.String(
        required=True,
        description='Athena text table name'
    ),
    'data_transport_service': fields.String(
        required=True,
        description='Method that defines how data from feed server will be delivered to AWS'
    ),
    'connector_type': fields.String(
        required=True,
        description='Name of connector type (historian server)'
    )
})
