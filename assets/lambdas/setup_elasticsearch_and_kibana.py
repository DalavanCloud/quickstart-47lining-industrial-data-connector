import json
import os

import boto3

from lambdas.utils import send_cfnresponse, make_elasticsearch_client

KIBANA_ASSETS_PATH_KINESIS = 'assets/kibana/managed-feeds-visualizations-kinesis.json'
KIBANA_ASSETS_PATH_IOT = 'assets/kibana/managed-feeds-visualizations-iot.json'

KIBANA_INDICES_KINESIS = [
    {'name': 'managed_feeds*', 'is_default': True},
    {'name': 'updates_per_managed_feed'},
    {'name': 'updates_per_second'}
]

KIBANA_INDICES_IOT = [
    {'name': 'managed_feeds*', 'is_default': True}
]

ES_INDICES_TMPL = [
    {  # Daily Cloud Watch Logs
        'template': 'cwl*',
        'settings': {'number_of_shards': 1}
    },
    {  # Managed feeds
        'template': 'managed_feeds*',
        'settings': {'number_of_shards': 3}
    },
]

@send_cfnresponse
def lambda_handler_kinesis(event, context):
    s3_resource = boto3.resource('s3')
    es_client = make_elasticsearch_client(os.environ['ELASTICSEARCH_ENDPOINT'])
    kibana_visualization = _get_kibana_visualization(s3_resource, KIBANA_ASSETS_PATH_KINESIS)

    if event['RequestType'] == 'Create':
        _register_index_templates(es_client, ES_INDICES_TMPL)
        _register_indices(es_client, KIBANA_INDICES_KINESIS)
        _register_visuals(es_client, kibana_visualization)


@send_cfnresponse
def lambda_handler_iot(event, context):
    s3_resource = boto3.resource('s3')
    es_client = make_elasticsearch_client(os.environ['ELASTICSEARCH_ENDPOINT'])
    kibana_visualization = _get_kibana_visualization(s3_resource, KIBANA_ASSETS_PATH_IOT)

    if event['RequestType'] == 'Create':
        _register_index_templates(es_client, ES_INDICES_TMPL)
        _register_indices(es_client, KIBANA_INDICES_IOT)
        _register_visuals(es_client, kibana_visualization)



def _get_kibana_visualization(s3_resource, kibana_assets_path):
    qs_s3_bucket, qs_s3_key_prefix = os.environ['QSS3_BUCKET_NAME'], os.environ['QSS3_KEY_PREFIX']
    kibana_export_key = os.path.join(qs_s3_key_prefix, kibana_assets_path)

    kibana_visualization = s3_resource.Object(qs_s3_bucket, kibana_export_key).get()['Body'].read().decode()
    return json.loads(kibana_visualization)


def _register_indices(es_client, indices):
    for index in indices:
        if index.get('is_default'):
            default_data = {'defaultIndex': index['name']}
            es_client.index(index='.kibana', doc_type='config', id='5.1.1', body=json.dumps(default_data))
        data = {'title': index['name'], 'timeFieldName': 'timestamp'}
        es_client.index(index='.kibana', doc_type='index-pattern', id=index['name'], body=json.dumps(data))


def _register_visuals(es_client, kibana_visualization):
    for visual in kibana_visualization:
        es_client.index(
            index='.kibana',
            doc_type=visual['_type'],
            id=visual['_id'],
            body=json.dumps(visual['_source'])
        )


def _register_index_templates(es_client, indices_tmpl):
    for index_tmpl in indices_tmpl:
        es_client.indices.put_template(name=index_tmpl['template'], body=index_tmpl)
