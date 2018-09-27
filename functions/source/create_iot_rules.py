import os

import boto3

from source.utils import send_cfnresponse, make_additional_assets_columns_without_join_column


def create_action_s3(data_bucket_name, role_arn, data_type):
    return {
        "s3": {
            "bucketName": data_bucket_name,
            "key": "data/%s/${parse_time(\"yyyy/MM/dd/HH\", timestamp())}/${topic()}-${timestamp()}" % data_type,
            "roleArn": role_arn
        }
    }


def create_action_cw_individual(metric_namespace_name, role_arn):
    return {
        "cloudwatchMetric": {
            "metricName": "${topic()}",
            "metricNamespace": metric_namespace_name,
            "metricUnit": "Count",
            "metricValue": "1",
            "roleArn": role_arn
        }
    }


def create_action_cw_total(metric_namespace_name, role_arn):
    return {
        "cloudwatchMetric": {
            "metricName": "allUpdates",
            "metricNamespace": metric_namespace_name,
            "metricUnit": "Count",
            "metricValue": "1",
            "roleArn": role_arn
        }
    }


def create_rules(data_bucket_name, metric_namespace_name, role_arn, data_type, use_detailed_cw):
    rules = []
    rules.append(create_action_s3(data_bucket_name, role_arn, data_type))
    rules.append(create_action_cw_total(metric_namespace_name, role_arn))

    if use_detailed_cw.lower() == 'yes':
        rules.append(create_action_cw_individual(metric_namespace_name, role_arn))

    return rules


@send_cfnresponse
def lambda_handler(event, _):
    if event['RequestType'] == 'Create':
        role_arn = os.environ['IoTRuleRoleArn']
        data_bucket_name = os.environ['DataBucketName']
        metric_namespace_name = os.environ['MetricNamespaceName']
        pi_server = os.environ['PiServer']
        deployment_suffix = os.environ['QSDeploymentSuffix']
        elasticsearch_endpoint = os.environ['ElasticsearchEndpoint']
        use_detailed_cw = os.environ['CreateIndividualLogs']
        connector_type = os.environ['CONNECTOR_TYPE']

        client = boto3.client('iot')

        additional_columns = make_additional_assets_columns_without_join_column(connector_type)
        additional_columns_names_string = (',' + ', '.join([column["column_name"] for column in additional_columns])) \
            if len(additional_columns) > 0 else ''

        numeric_rules = create_rules(data_bucket_name, metric_namespace_name, role_arn, "numeric", use_detailed_cw)
        text_rules = create_rules(data_bucket_name, metric_namespace_name, role_arn, "text", use_detailed_cw)

        client.create_topic_rule(
            ruleName=f'PI2AWSRule_numeric_{deployment_suffix}',
            topicRulePayload={
                "actions": numeric_rules,
                "awsIotSqlVersion": "2016-03-23",
                "ruleDisabled": False,
                "sql": f"""SELECT cast(value AS DECIMAL) AS value, name {additional_columns_names_string}, timestamp
                           FROM '{pi_server}/#'
                           WHERE ISUNDEFINED(CAST(value AS DECIMAL)) <> TRUE
                        """
            }
        )

        client.create_topic_rule(
            ruleName=f'PI2AWSRule_text_{deployment_suffix}',
            topicRulePayload={
                "actions": text_rules,
                "awsIotSqlVersion": "2016-03-23",
                "ruleDisabled": False,
                "sql": f"""SELECT *
                           FROM '{pi_server}/#'
                           WHERE ISUNDEFINED(CAST(value AS DECIMAL))"""

            }
        )

        client.create_topic_rule(
            ruleName=f'PI2AWSRule_numeric_elasticsearch_{deployment_suffix}',
            topicRulePayload={
                "actions": [
                    {
                        "elasticsearch": {
                            "endpoint": f'https://{elasticsearch_endpoint}',
                            "id": "${newuuid()}",
                            "index": "managed_feeds-${parse_time(\"yyyy-MM-dd\", timestamp())}",
                            "roleArn": role_arn,
                            "type": "ManagedFeedStream"
                        }
                    }
                ],
                "awsIotSqlVersion": "2016-03-23",
                "ruleDisabled": False,
                "sql": f"""SELECT cast(value AS DECIMAL) AS value, name, {additional_columns_names_string}, es_timestamp as timestamp
                           FROM '{pi_server}/#'
                           WHERE ISUNDEFINED(CAST(value AS DECIMAL)) <> TRUE"""

            }
        )
