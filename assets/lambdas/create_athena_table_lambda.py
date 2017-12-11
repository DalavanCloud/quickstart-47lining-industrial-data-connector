import boto3
import os

from lambdas.utils import wait_for_athena_query_completion, send_cfnresponse


def make_create_table_query():
    return """
        CREATE EXTERNAL TABLE {database_name}.{table_name} (
            `name` STRING,
            `data_source` STRING,
            `value` DOUBLE,
            `timestamp` TIMESTAMP
        ) PARTITIONED BY (dt STRING)
        ROW FORMAT DELIMITED FIELDS
        TERMINATED BY ','
        ESCAPED BY '\\\\'
        LINES TERMINATED BY '\\n'
        LOCATION '{s3_data_location_dir}';
    """.format(
        database_name=os.environ['ATHENA_DATABASE_NAME'],
        table_name=os.environ['ATHENA_TABLE_NAME'],
        s3_data_location_dir=os.environ['ATHENA_S3_DATA_LOCATION_DIR']
    )


def make_drop_table_query():
    return """
        DROP TABLE IF EXISTS {database_name}.{table_name} PURGE
    """.format(
        database_name=os.environ['ATHENA_DATABASE_NAME'],
        table_name=os.environ['ATHENA_TABLE_NAME']
    )


def run_athena_query(query):
    query_config = dict(
        QueryString=query,
        ResultConfiguration={
            'OutputLocation': os.environ['ATHENA_QUERY_OUTPUT_LOCATION_DIR']
        }
    )
    client = boto3.client('athena', region_name=os.environ['AWS_REGION'])
    response = client.start_query_execution(**query_config)
    query_execution_id = response['QueryExecutionId']
    wait_for_athena_query_completion(client, query_execution_id)


@send_cfnresponse
def lambda_handler(event, context):
    if event['RequestType'] == 'Create':
        query = make_create_table_query()
        run_athena_query(query)
    elif event['RequestType'] == 'Delete':
        query = make_drop_table_query()
        run_athena_query(query)
