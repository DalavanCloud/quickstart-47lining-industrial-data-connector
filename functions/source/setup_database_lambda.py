from source.utils import send_cfnresponse
from model.models import Base
from sqlalchemy import create_engine


@send_cfnresponse
def lambda_handler(event, context):
    if event['RequestType'] == 'Create':
        postgres_uri = event['ResourceProperties']['PostgresUri']
        engine = create_engine(postgres_uri)
        Base.metadata.create_all(engine)
