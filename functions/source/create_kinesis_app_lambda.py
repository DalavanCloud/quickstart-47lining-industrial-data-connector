import os

import boto3
import logging

from botocore.exceptions import ClientError

from source.utils import send_cfnresponse

log = logging.getLogger()


def _create_managed_feeds_application_config(app_name, input_stream_arn, output_elasticsearch_stream_arn,
                                             output_s3_numeric_stream_arn, output_s3_text_stream_arn, role_arn):
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
                    'RecordColumns': [
                        {
                            'Name': 'name',
                            'SqlType': 'VARCHAR(64)'
                        },
                        {
                            'Name': 'data_source',
                            'SqlType': 'VARCHAR(64)'
                        },
                        {
                            'Name': 'feed_value',
                            'SqlType': 'VARCHAR(128)'
                        },
                        {
                            'Name': 'feed_timestamp',
                            'SqlType': 'VARCHAR(64)'
                        }
                    ]
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
                "data_source" VARCHAR(64),
                "value" DOUBLE,
                "timestamp" VARCHAR(64)
            );

            CREATE STREAM "MANAGED_FEEDS_S3_NUMERIC_OUTPUT" (
                "name" VARCHAR(64),
                "data_source" VARCHAR(64),
                "value" DOUBLE,
                "timestamp" VARCHAR(64)
            );
            
            CREATE STREAM "MANAGED_FEEDS_S3_TEXT_OUTPUT" (
                "name" VARCHAR(64),
                "data_source" VARCHAR(64),
                "value" VARCHAR(128),
                "timestamp" VARCHAR(64)
            );

            CREATE PUMP "STREAM_PUMP1" AS INSERT INTO "MANAGED_FEEDS_ES_OUTPUT"
            SELECT "name", "data_source", CAST("feed_value" AS DOUBLE), "feed_timestamp"
            FROM "MANAGED_FEED_INPUT_001"
            WHERE "feed_value" SIMILAR TO '-?[0-9]+.?[0-9]*(E_[0-9]{2})?';

            CREATE PUMP "STREAM_PUMP2" AS INSERT INTO "MANAGED_FEEDS_S3_NUMERIC_OUTPUT"
            SELECT "name", "data_source", CAST("feed_value" AS DOUBLE), REGEX_REPLACE("feed_timestamp", 'T', ' ', 1, 0)
            FROM "MANAGED_FEED_INPUT_001"
            WHERE "feed_value" SIMILAR TO '-?[0-9]+.?[0-9]*(E_[0-9]{2})?';
            
            CREATE PUMP "STREAM_PUMP3" AS INSERT INTO "MANAGED_FEEDS_S3_TEXT_OUTPUT"
            SELECT "name", "data_source", "feed_value", REGEX_REPLACE("feed_timestamp", 'T', ' ', 1, 0)
            FROM "MANAGED_FEED_INPUT_001"
            WHERE NOT ("feed_value" SIMILAR TO '-?[0-9]+.?[0-9]*(E_[0-9]{2})?');
        """
    )


def _create_managed_feed_metrics_application_config(app_name, input_stream_arn, output_updates_per_second_stream_arn,
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
                    'RecordColumns': [
                        {
                            'Name': 'name',
                            'SqlType': 'VARCHAR(64)'
                        },
                        {
                            'Name': 'data_source',
                            'SqlType': 'VARCHAR(64)'
                        },
                        {
                            'Name': 'feed_value',
                            'SqlType': 'VARCHAR(128)'
                        },
                        {
                            'Name': 'feed_timestamp',
                            'SqlType': 'VARCHAR(64)'
                        }
                    ]
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
            SELECT STREAM TIMESTAMP_TO_CHAR('YYYY-MM-dd''T''HH:mm:ss', FLOOR("MANAGED_FEED_INPUT_001".ROWTIME TO SECOND)) AS "timestamp", COUNT(*) AS "updates_count"
            FROM "MANAGED_FEED_INPUT_001"
            GROUP BY FLOOR("MANAGED_FEED_INPUT_001".ROWTIME TO SECOND);

            CREATE PUMP "STREAM_PUMP4" AS INSERT INTO "UPDATES_PER_MANAGED_FEED"
            SELECT STREAM TIMESTAMP_TO_CHAR('YYYY-MM-dd''T''HH:mm:ss', FLOOR("MANAGED_FEED_INPUT_001".ROWTIME TO SECOND)) AS "timestamp", COUNT(*) AS "updates_count", "name"
            FROM "MANAGED_FEED_INPUT_001"
            GROUP BY FLOOR("MANAGED_FEED_INPUT_001".ROWTIME TO SECOND), "name";
        """
    )


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


def _create_and_start_application(client, app_name, app_config):
    response = client.create_application(**app_config)
    log.info(response)
    response = _start_application(client, app_name)
    log.info(response)


def create_applications(region, input_stream_arn, output_elasticsearch_stream_arn, output_s3_numeric_stream_arn,
                        output_s3_text_stream_arn, output_updates_per_second_stream_arn,
                        output_updates_per_managed_feed_stream_arn, role_arn, deployment_suffix):
    client = boto3.client('kinesisanalytics', region_name=region)
    app_name = 'managed-feeds-app-{}'.format(deployment_suffix)
    app_config = _create_managed_feeds_application_config(
        app_name,
        input_stream_arn,
        output_elasticsearch_stream_arn,
        output_s3_numeric_stream_arn,
        output_s3_text_stream_arn,
        role_arn
    )
    _create_and_start_application(client, app_name, app_config)
    app_name = 'managed-feeds-metrics-{}'.format(deployment_suffix)
    app_config = _create_managed_feed_metrics_application_config(
        app_name,
        input_stream_arn,
        output_updates_per_second_stream_arn,
        output_updates_per_managed_feed_stream_arn,
        role_arn
    )
    _create_and_start_application(client, app_name, app_config)


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
def lambda_handler(event, context):
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
            deployment_suffix=os.environ['DEPLOYMENT_SUFFIX']
        )
    elif event['RequestType'] == 'Delete':
        delete_applications(
            region=os.environ['AWS_REGION'],
            deployment_suffix=os.environ['DEPLOYMENT_SUFFIX']
        )
