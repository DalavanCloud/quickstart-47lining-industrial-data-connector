import logging
import os
from io import BytesIO

import boto3
from botocore.exceptions import ClientError

from source.configuration.input_stream import additional_columns_stream
from source.utils import send_cfnresponse, make_additional_assets_columns_without_join_column, get_join_column, \
    get_additional_assets_columns_with_join_column, get_input_stream_record_columns

log = logging.getLogger()


def _create_managed_feeds_application_config(app_name, input_stream_arn, input_stream_record_columns,
                                             output_elasticsearch_stream_arn, output_s3_numeric_stream_arn,
                                             output_s3_text_stream_arn, role_arn, connector_type):
    additional_columns = make_additional_assets_columns_without_join_column(connector_type)
    join_column_name = get_join_column(connector_type)

    columns = ['"{column_name}" {kinesis_type}'.format(
        column_name=column['column_name'],
        kinesis_type=column['kinesis_type']
    ) for column in additional_columns]
    columns_string = (',' + ',\n                '.join(columns)) if len(columns) > 0 else ''

    columns_names_string = [column['column_name'] for column in additional_columns]
    additional_columns_stream_names = [x['column_name'] for x in additional_columns_stream]

    return dict(
        ApplicationName=app_name,
        Inputs=[
            {
                'NamePrefix': 'MANAGED_FEED_INPUT',
                'KinesisStreamsInput': {
                    'ResourceARN': input_stream_arn,
                    'RoleARN': role_arn
                },
                'InputParallelism': {
                    'Count': 1
                },
                'InputSchema': {
                    'RecordFormat': {
                        'RecordFormatType': 'CSV',
                        'MappingParameters': {
                            'CSVMappingParameters': {
                                'RecordRowDelimiter': '\n',
                                'RecordColumnDelimiter': ','
                            }
                        }
                    },
                    'RecordEncoding': 'UTF-8',
                    'RecordColumns': input_stream_record_columns
                }
            },
        ],
        Outputs=[
            {
                'Name': 'MANAGED_FEEDS_ES_OUTPUT',
                'KinesisFirehoseOutput': {
                    'ResourceARN': output_elasticsearch_stream_arn,
                    'RoleARN': role_arn
                },
                'DestinationSchema': {
                    'RecordFormatType': 'JSON'
                }
            },
            {
                'Name': 'MANAGED_FEEDS_S3_NUMERIC_OUTPUT',
                'KinesisFirehoseOutput': {
                    'ResourceARN': output_s3_numeric_stream_arn,
                    'RoleARN': role_arn
                },
                'DestinationSchema': {
                    'RecordFormatType': 'CSV'
                }
            },
            {
                'Name': 'MANAGED_FEEDS_S3_TEXT_OUTPUT',
                'KinesisFirehoseOutput': {
                    'ResourceARN': output_s3_text_stream_arn,
                    'RoleARN': role_arn
                },
                'DestinationSchema': {
                    'RecordFormatType': 'CSV'
                }
            }
        ],
        ApplicationCode="""
            CREATE STREAM "MANAGED_FEEDS_ES_OUTPUT" (
                "name" VARCHAR(64),
                "value" DOUBLE,
                "timestamp" VARCHAR(64)
                {additional_columns}
            );

            CREATE STREAM "MANAGED_FEEDS_S3_NUMERIC_OUTPUT" (
                "name" VARCHAR(64),
                "value" DOUBLE,
                "timestamp" VARCHAR(64)
                {additional_columns}
            );

            CREATE STREAM "MANAGED_FEEDS_S3_TEXT_OUTPUT" (
                "name" VARCHAR(64),
                "value" VARCHAR(128),
                "timestamp" VARCHAR(64)
                {additional_columns}
            );

            CREATE PUMP "STREAM_PUMP1" AS INSERT INTO "MANAGED_FEEDS_ES_OUTPUT"
            SELECT "name", CAST("feed_value" AS DOUBLE), "feed_timestamp"
              {columns_names_string} {columns_names_string_with_prefix}
            FROM "MANAGED_FEED_INPUT_001" s
            LEFT OUTER JOIN
              "REFERENCE_DATA" r ON s."name" = r."{join_column_name}"
            WHERE "feed_value" SIMILAR TO '-?[0-9]+.?[0-9]*(E_[0-9]{{2}})?';

            CREATE PUMP "STREAM_PUMP2" AS INSERT INTO "MANAGED_FEEDS_S3_NUMERIC_OUTPUT"
            SELECT STREAM
                s."name",
                CAST(s."feed_value" AS DOUBLE),
                REGEX_REPLACE(s."feed_timestamp", 'T', ' ', 1, 0)
                {columns_names_string} {columns_names_string_with_prefix}
            FROM "MANAGED_FEED_INPUT_001" s
            LEFT OUTER JOIN
              "REFERENCE_DATA" r ON s."name" = r."{join_column_name}"
            WHERE "feed_value" SIMILAR TO '-?[0-9]+.?[0-9]*(E_[0-9]{{2}})?';

            CREATE PUMP "STREAM_PUMP3" AS INSERT INTO "MANAGED_FEEDS_S3_TEXT_OUTPUT"
            SELECT STREAM
                s."name",
                "feed_value",
                REGEX_REPLACE(s."feed_timestamp", 'T', ' ', 1, 0)
                {columns_names_string} {columns_names_string_with_prefix}
            FROM "MANAGED_FEED_INPUT_001" s
            LEFT OUTER JOIN
              "REFERENCE_DATA" r ON s."name" = r."{join_column_name}"
            WHERE NOT ("feed_value" SIMILAR TO '-?[0-9]+.?[0-9]*(E_[0-9]{{2}})?');
        """.format(
            additional_columns=columns_string,
            columns_names_string=_get_columns_names_string(columns_names_string, additional_columns_stream_names),
            columns_names_string_with_prefix=_get_columns_names_string_with_prefix(columns_names_string,
                                                                                   additional_columns_stream_names),
            join_column_name=join_column_name
        )
    )


def _get_columns_names_string(columns_names_string, additional_columns_stream_names):
    column_names = [f'"{c}"' for c in columns_names_string if c not in additional_columns_stream_names]
    return (',' + ', '.join(column_names)) if len(column_names) > 0 else ''


def _get_columns_names_string_with_prefix(columns_names_string, additional_columns_stream_names):
    column_names_with_prefix = [f's."{c}"' for c in columns_names_string if c in additional_columns_stream_names]
    return (', ' + ', '.join(column_names_with_prefix)) if len(column_names_with_prefix) > 0 else ''


def _create_managed_feed_metrics_application_config(app_name, input_stream_arn, input_stream_record_columns,
                                                    output_updates_per_second_stream_arn,
                                                    output_updates_per_managed_feed_stream_arn, role_arn):
    return dict(
        ApplicationName=app_name,
        Inputs=[
            {
                'NamePrefix': 'MANAGED_FEED_INPUT',
                'KinesisStreamsInput': {
                    'ResourceARN': input_stream_arn,
                    'RoleARN': role_arn
                },
                'InputParallelism': {
                    'Count': 1
                },
                'InputSchema': {
                    'RecordFormat': {
                        'RecordFormatType': 'CSV',
                        'MappingParameters': {
                            'CSVMappingParameters': {
                                'RecordRowDelimiter': '\n',
                                'RecordColumnDelimiter': ','
                            }
                        }
                    },
                    'RecordEncoding': 'UTF-8',
                    'RecordColumns': input_stream_record_columns
                }
            },
        ],
        Outputs=[
            {
                'Name': 'UPDATES_PER_SECOND',
                'KinesisFirehoseOutput': {
                    'ResourceARN': output_updates_per_second_stream_arn,
                    'RoleARN': role_arn
                },
                'DestinationSchema': {
                    'RecordFormatType': 'JSON'
                }
            },
            {
                'Name': 'UPDATES_PER_MANAGED_FEED',
                'KinesisFirehoseOutput': {
                    'ResourceARN': output_updates_per_managed_feed_stream_arn,
                    'RoleARN': role_arn
                },
                'DestinationSchema': {
                    'RecordFormatType': 'JSON'
                }
            }
        ],
        ApplicationCode="""
            CREATE STREAM "UPDATES_PER_SECOND" (
                "timestamp" VARCHAR(64),
                "updates_count" INTEGER
            );

            CREATE STREAM "UPDATES_PER_MANAGED_FEED" (
                "timestamp" VARCHAR(64),
                "updates_count" INTEGER,
                "name" VARCHAR(64)
            );

            CREATE PUMP "STREAM_PUMP3" AS INSERT INTO "UPDATES_PER_SECOND"
            SELECT STREAM TIMESTAMP_TO_CHAR('YYYY-MM-dd''T''HH:mm:ss', 
            FLOOR("MANAGED_FEED_INPUT_001".ROWTIME TO SECOND)) AS "timestamp", COUNT(*) AS "updates_count"
            FROM "MANAGED_FEED_INPUT_001"
            GROUP BY FLOOR("MANAGED_FEED_INPUT_001".ROWTIME TO SECOND);

            CREATE PUMP "STREAM_PUMP4" AS INSERT INTO "UPDATES_PER_MANAGED_FEED"
            SELECT STREAM TIMESTAMP_TO_CHAR('YYYY-MM-dd''T''HH:mm:ss', 
            FLOOR("MANAGED_FEED_INPUT_001".ROWTIME TO SECOND)) AS "timestamp", COUNT(*) AS "updates_count", "name"
            FROM "MANAGED_FEED_INPUT_001"
            GROUP BY FLOOR("MANAGED_FEED_INPUT_001".ROWTIME TO SECOND), "name";
        """  # noqa
    )


def _add_reference_data_source(client, app_name, bucket, key, role_arn, connector_type):
    response_describe_application = client.describe_application(
        ApplicationName=app_name
    )
    application_version_id = response_describe_application['ApplicationDetail']['ApplicationVersionId']
    additional_assets_columns_with_join_column = get_additional_assets_columns_with_join_column(connector_type)

    response = client.add_application_reference_data_source(
        ApplicationName=app_name,
        CurrentApplicationVersionId=application_version_id,
        ReferenceDataSource={
            'TableName': 'REFERENCE_DATA',
            'S3ReferenceDataSource': {
                'BucketARN': 'arn:aws:s3:::%s' % bucket,
                'FileKey': key,
                'ReferenceRoleARN': role_arn
            },
            'ReferenceSchema': {
                'RecordFormat': {
                    'RecordFormatType': 'JSON',
                    'MappingParameters': {
                        'JSONMappingParameters': {
                            'RecordRowPath': '$'
                        }
                    }
                },
                'RecordEncoding': 'UTF-8',
                'RecordColumns': [_create_record_column(x) for x in additional_assets_columns_with_join_column]
            }
        }
    )
    return response


def _create_record_column(x):
    return {
        'Name': x['column_name'],
        'Mapping': x['Mapping'],
        'SqlType': x['kinesis_type']
    }


def _start_application(client, app_name):
    app_description = client.describe_application(ApplicationName=app_name)
    input_id = app_description['ApplicationDetail']['InputDescriptions'][0]['InputId']
    return client.start_application(
        ApplicationName=app_name,
        InputConfigurations=[
            {
                'Id': input_id,
                'InputStartingPositionConfiguration': {
                    'InputStartingPosition': 'NOW'
                }
            },
        ]
    )


def _put_empty_object_if_doesnt_exists(bucket, key):
    s3 = boto3.resource('s3')

    try:
        s3.Object(bucket, key).load()
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            bucket = s3.Bucket(bucket)
            f = BytesIO(b'')
            bucket.upload_fileobj(f, key)
        else:
            raise


def _create_and_start_application(client, app_name, app_config, connector_type, add_reference_data=False,
                                  bucket=None, key=None, role_arn=None):
    response = client.create_application(**app_config)
    log.info(response)
    if add_reference_data:
        _put_empty_object_if_doesnt_exists(bucket, key)
        response = _add_reference_data_source(client, app_name, bucket, key, role_arn, connector_type)
        log.info(response)
    response = _start_application(client, app_name)
    log.info(response)


def create_applications(region, input_stream_arn, output_elasticsearch_stream_arn, output_s3_numeric_stream_arn,
                        output_s3_text_stream_arn, output_updates_per_second_stream_arn,
                        output_updates_per_managed_feed_stream_arn, role_arn, deployment_suffix,
                        structure_bucket, structure_key, connector_type):
    client = boto3.client('kinesisanalytics', region_name=region)
    app_name = 'managed-feeds-app-{}'.format(deployment_suffix)

    input_stream_record_columns = get_input_stream_record_columns(connector_type)

    app_config = _create_managed_feeds_application_config(
        app_name=app_name,
        input_stream_arn=input_stream_arn,
        input_stream_record_columns=input_stream_record_columns,
        output_elasticsearch_stream_arn=output_elasticsearch_stream_arn,
        output_s3_numeric_stream_arn=output_s3_numeric_stream_arn,
        output_s3_text_stream_arn=output_s3_text_stream_arn,
        role_arn=role_arn,
        connector_type=connector_type
    )
    _create_and_start_application(
        client=client,
        app_name=app_name,
        app_config=app_config,
        connector_type=connector_type,
        add_reference_data=True,
        bucket=structure_bucket,
        key=structure_key,
        role_arn=role_arn
    )
    app_name = 'managed-feeds-metrics-{}'.format(deployment_suffix)
    app_config = _create_managed_feed_metrics_application_config(
        app_name=app_name,
        input_stream_arn=input_stream_arn,
        input_stream_record_columns=input_stream_record_columns,
        output_updates_per_second_stream_arn=output_updates_per_second_stream_arn,
        output_updates_per_managed_feed_stream_arn=output_updates_per_managed_feed_stream_arn,
        role_arn=role_arn
    )
    _create_and_start_application(client, app_name, app_config, connector_type)


def _delete_application(client, app_name):
    try:
        response = client.describe_application(ApplicationName=app_name)
        create_timestamp = response['ApplicationDetail']['CreateTimestamp']
        client.delete_application(ApplicationName=app_name, CreateTimestamp=create_timestamp)
    except ClientError as e:
        log.exception(e)


def delete_applications(region, deployment_suffix):
    client = boto3.client('kinesisanalytics', region_name=region)
    feeds_app_name = 'managed-feeds-app-{}'.format(deployment_suffix)
    metrics_app_name = 'managed-feeds-metrics-{}'.format(deployment_suffix)
    _delete_application(client, feeds_app_name)
    _delete_application(client, metrics_app_name)


@send_cfnresponse
def lambda_handler(event, _):
    if event['RequestType'] == 'Create':
        create_applications(
            region=os.environ['AWS_REGION'],
            input_stream_arn=os.environ['INPUT_STREAM_ARN'],
            output_elasticsearch_stream_arn=os.environ['OUTPUT_ES_STREAM_ARN'],
            output_s3_numeric_stream_arn=os.environ['OUTPUT_S3_NUMERIC_STREAM_ARN'],
            output_s3_text_stream_arn=os.environ['OUTPUT_S3_TEXT_STREAM_ARN'],
            output_updates_per_second_stream_arn=os.environ['OUTPUT_UPDATES_PER_SECOND_STREAM_ARN'],
            output_updates_per_managed_feed_stream_arn=os.environ['OUTPUT_UPDATES_PER_MANAGED_FEED_ARN'],
            role_arn=os.environ['ROLE_ARN'],
            deployment_suffix=os.environ['DEPLOYMENT_SUFFIX'],
            structure_bucket=os.environ['STRUCTURE_DATA_BUCKET'],
            structure_key=os.environ['STRUCTURE_DATA_KEY'],
            connector_type=os.environ['CONNECTOR_TYPE'],
        )
    elif event['RequestType'] == 'Delete':
        delete_applications(
            region=os.environ['AWS_REGION'],
            deployment_suffix=os.environ['DEPLOYMENT_SUFFIX']
        )
