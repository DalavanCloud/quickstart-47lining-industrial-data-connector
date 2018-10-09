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
        as_database = properties['AsStructureDatabase']

        engine = create_engine(postgres_uri)
        Session = sessionmaker(bind=engine)

        session = Session()

        session.add(
            Settings(
                name='as_db_name',
                value=as_database
            )
        )

        session.commit()
