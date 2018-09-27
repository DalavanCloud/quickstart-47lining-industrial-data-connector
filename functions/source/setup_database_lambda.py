import os

from sqlalchemy import create_engine
from sqlalchemy.engine import reflection
from sqlalchemy.schema import (
    MetaData,
    Table,
    DropTable,
    ForeignKeyConstraint,
    DropConstraint
)

from source.utils import send_cfnresponse, import_sqlalchemy_model

Base = import_sqlalchemy_model(os.environ.get('CONNECTOR_TYPE'), 'Base')


def drop_all(engine):
    """https://bitbucket.org/zzzeek/sqlalchemy/wiki/UsageRecipes/DropEverything"""
    conn = engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.

    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(
                ForeignKeyConstraint((), (), name=fk['name'])
            )
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))

    trans.commit()


@send_cfnresponse
def lambda_handler(event, context):
    if event['RequestType'] == 'Create':
        postgres_uri = event['ResourceProperties']['PostgresUri']
        engine = create_engine(postgres_uri)
        Base.metadata.create_all(engine)
    elif event['RequestType'] == 'Update':
        postgres_uri = event['ResourceProperties']['PostgresUri']
        engine = create_engine(postgres_uri)
        drop_all(engine)
        Base.metadata.create_all(engine)
