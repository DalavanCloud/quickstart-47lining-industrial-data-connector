import os
from source.utils import send_cfnresponse, make_drop_table_query, run_athena_query


def make_create_feed_mapping_table_query(database_name, table_name, s3_as_table_location):
    return """
        CREATE EXTERNAL TABLE {database_name}.{table_name}(
            `aspath` STRING,
            `asset` STRING,
            `categories` array<string> ,
            `description` STRING,
            `name` STRING,
            `uom` STRING,
            `feedname` STRING,
            `feedpath` STRING,
            `template` STRING
        )
        ROW FORMAT SERDE
          'org.openx.data.jsonserde.JsonSerDe'
        STORED AS INPUTFORMAT
          'org.apache.hadoop.mapred.TextInputFormat'
        OUTPUTFORMAT
          'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
        LOCATION '{s3_as_table_location}'
    """.format(
        s3_as_table_location=s3_as_table_location,
        database_name=database_name,
        table_name=table_name,
    )


def make_create_static_attributes_mapping_table_query(database_name, table_name, s3_static_attributes_table_location):
    return """
        CREATE EXTERNAL TABLE {database_name}.{table_name}(
            `aspath` STRING,
            `asset` STRING,
            `categories` array<string> ,
            `description` STRING,
            `name` STRING,
            `uom` STRING,
            `value` STRING,
            `valuetimestamp` STRING,
            `template` STRING
        )
        ROW FORMAT SERDE
          'org.openx.data.jsonserde.JsonSerDe'
        STORED AS INPUTFORMAT
          'org.apache.hadoop.mapred.TextInputFormat'
        OUTPUTFORMAT
          'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat'
        LOCATION '{s3_static_attributes_table_location}'
    """.format(
        s3_static_attributes_table_location=s3_static_attributes_table_location,
        database_name=database_name,
        table_name=table_name,
    )


@send_cfnresponse
def lambda_handler(event, context):
    feed_mapping_table_query = ''
    static_attributes_mapping_table_query = ''

    if event['RequestType'] == 'Create':
        feed_mapping_table_query = make_create_feed_mapping_table_query(
            event['ResourceProperties']['AthenaDatabaseName'],
            event['ResourceProperties']['AthenaTableName'],
            event['ResourceProperties']['S3DataLocationDir']
        )

        static_attributes_mapping_table_query = make_create_static_attributes_mapping_table_query(
            event['ResourceProperties']['AthenaDatabaseName'],
            event['ResourceProperties']['StaticAttributesAthenaTableName'],
            event['ResourceProperties']['StaticAttributesS3DataLocationDir']
        )

    if event['RequestType'] == 'Delete':
        feed_mapping_table_query = make_drop_table_query(
            database_name=event['ResourceProperties']['AthenaDatabaseName'],
            table_name=event['ResourceProperties']['AthenaTableName']
        )

        static_attributes_mapping_table_query = make_drop_table_query(
            database_name=event['ResourceProperties']['AthenaDatabaseName'],
            table_name=event['ResourceProperties']['StaticAttributesAthenaTableName']
        )

    if event['RequestType'] == 'Create' or event['RequestType'] == 'Delete':
        run_athena_query(
            query=feed_mapping_table_query,
            query_output_location_dir=event['ResourceProperties']['AthenaQueryOutputLocationDir'],
            region=os.environ['AWS_REGION']
        )

        run_athena_query(
            query=static_attributes_mapping_table_query,
            query_output_location_dir=event['ResourceProperties']['AthenaQueryOutputLocationDir'],
            region=os.environ['AWS_REGION']
        )
