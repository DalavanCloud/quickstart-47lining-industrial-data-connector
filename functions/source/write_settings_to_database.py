import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from source.utils import send_cfnresponse, import_sqlalchemy_model

Settings = import_sqlalchemy_model(os.environ.get('CONNECTOR_TYPE'), 'Settings')


@send_cfnresponse
def lambda_handler(event, context):
    if event['RequestType'] == 'Create':
        properties = event['ResourceProperties']
        postgres_uri = properties['PostgresUri']
        deployment_suffix = properties['QSDeploymentSuffix']
        region = properties['Region']

        engine = create_engine(postgres_uri)
        Session = sessionmaker(bind=engine)

        session = Session()

        session.bulk_insert_mappings(
            Settings,
            [
                {
                    'name': 'deployment_name',
                    'value': f'{deployment_suffix} ({region})'
                },
                {
                    'name': 'feed_group_size',
                    'value': '1000'
                },
                {
                    'name': 'time_window_days',
                    'value': '7'
                }
            ]
        )

        session.commit()
