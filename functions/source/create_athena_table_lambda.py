import boto3
import os

from source.utils import wait_for_athena_query_completion, send_cfnresponse


def make_create_table_query_csv(event):
    return """
        CREATE EXTERNAL TABLE {database_name}.{table_name} (
            `name` STRING,
            `data_source` STRING,
            `value` {managed_feed_type},
            `timestamp` TIMESTAMP
        ) PARTITIONED BY (dt STRING)
        ROW FORMAT DELIMITED FIELDS
        TERMINATED BY ','
        ESCAPED BY '\\\\'
        LINES TERMINATED BY '\\n'
        LOCATION '{s3_data_location_dir}';
    """.format(
        managed_feed_type=event['ResourceProperties']['ManagedFeedType'],
        database_name=event['ResourceProperties']['AthenaDatabaseName'],
        table_name=event['ResourceProperties']['AthenaTableName'],
        s3_data_location_dir=event['ResourceProperties']['S3DataLocationDir']
    )

def make_create_table_query_json(event):
    return """
        CREATE EXTERNAL TABLE {database_name}.{table_name} (
            `name` STRING,
            `data_source` STRING,
            `value` {managed_feed_type},
            `timestamp` TIMESTAMP
        ) PARTITIONED BY (dt STRING)
        ROW FORMAT SERDE 
          'org.openx.data.jsonserde.JsonSerDe' 
        STORED AS INPUTFORMAT 
          'org.apache.hadoop.mapred.TextInputFormat' 
        OUTPUTFORMAT 
          'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
        LOCATION '{s3_data_location_dir}';
    """.format(
        managed_feed_type=event['ResourceProperties']['ManagedFeedType'],
        database_name=event['ResourceProperties']['AthenaDatabaseName'],
        table_name=event['ResourceProperties']['AthenaTableName'],
        s3_data_location_dir=event['ResourceProperties']['S3DataLocationDir']
    )


def make_drop_table_query(event):
    return """
        DROP TABLE IF EXISTS {database_name}.{table_name} PURGE
    """.format(
        database_name=event['ResourceProperties']['AthenaDatabaseName'],
        table_name=event['ResourceProperties']['AthenaTableName']
    )


def run_athena_query(event, query):
    query_config = dict(
        QueryString=query,
        ResultConfiguration={
            'OutputLocation': event['ResourceProperties']['AthenaQueryOutputLocationDir']
        }
    )
    client = boto3.client('athena', region_name=os.environ['AWS_REGION'])
    response = client.start_query_execution(**query_config)
    query_execution_id = response['QueryExecutionId']
    wait_for_athena_query_completion(client, query_execution_id)


@send_cfnresponse
def lambda_handler(event, context):
    if event['RequestType'] == 'Create':
        if os.environ['DATA_TRANSPORT_SERVICE'] == 'Amazon Kinesis':
            query = make_create_table_query_csv(event)
        else:
            query = make_create_table_query_json(event)
        run_athena_query(event, query)
    elif event['RequestType'] == 'Delete':
        query = make_drop_table_query(event)
        run_athena_query(event, query)
