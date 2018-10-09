import os

from source.utils import send_cfnresponse, make_drop_table_query, run_athena_query, \
    make_additional_assets_columns_without_join_column


def _make_additional_columns_string(connector_type):
    additional_columns = make_additional_assets_columns_without_join_column(connector_type)
    columns = ['`{column_name}` {athena_type}'.format(
        column_name=column['column_name'],
        athena_type=column['athena_type']
    ) for column in additional_columns]
    return (',\n' + ',\n            '.join(columns)) if len(columns) > 0 else ''


def make_create_table_query_csv(event, additional_columns_string):
    return """
        CREATE EXTERNAL TABLE {database_name}.{table_name} (
            `name` STRING,
            `value` {managed_feed_type},
            `timestamp` TIMESTAMP
            {additional_columns_string}
        ) PARTITIONED BY (dt STRING)
        ROW FORMAT DELIMITED FIELDS
        TERMINATED BY ','
        ESCAPED BY '\\\\'
        LINES TERMINATED BY '\\n'
        LOCATION '{s3_data_location_dir}';
    """.format(
        managed_feed_type=event['ResourceProperties']['ManagedFeedType'],
        additional_columns_string=additional_columns_string,
        database_name=event['ResourceProperties']['AthenaDatabaseName'],
        table_name=event['ResourceProperties']['AthenaTableName'],
        s3_data_location_dir=event['ResourceProperties']['S3DataLocationDir']
    )


def make_create_table_query_json(event, additional_columns_string):
    return """
        CREATE EXTERNAL TABLE {database_name}.{table_name} (
            `name` STRING,
            `value` {managed_feed_type},
            `timestamp` TIMESTAMP
            {additional_columns_string}
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
        additional_columns_string=additional_columns_string,
        database_name=event['ResourceProperties']['AthenaDatabaseName'],
        table_name=event['ResourceProperties']['AthenaTableName'],
        s3_data_location_dir=event['ResourceProperties']['S3DataLocationDir']
    )


@send_cfnresponse
def lambda_handler(event, _):
    query = ''
    if event['RequestType'] == 'Create':
        additional_columns_string = _make_additional_columns_string(os.environ['CONNECTOR_TYPE'])

        if os.environ['DATA_TRANSPORT_SERVICE'] == 'Amazon Kinesis':
            query = make_create_table_query_csv(event, additional_columns_string)
        else:
            query = make_create_table_query_json(event, additional_columns_string)

    if event['RequestType'] == 'Delete':
        query = make_drop_table_query(
            database_name=event['ResourceProperties']['AthenaDatabaseName'],
            table_name=event['ResourceProperties']['AthenaTableName']
        )

    if event['RequestType'] == 'Create' or event['RequestType'] == 'Delete':
        run_athena_query(
            query=query,
            query_output_location_dir=event['ResourceProperties']['AthenaQueryOutputLocationDir'],
            region=os.environ['AWS_REGION']
        )
