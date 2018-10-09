import json
import os

import boto3

from source.utils import send_cfnresponse, make_elasticsearch_client

KIBANA_ASSETS_PATH_KINESIS = 'kibana/managed-feeds-visualizations-kinesis.json'
KIBANA_ASSETS_PATH_IOT = 'kibana/managed-feeds-visualizations-iot.json'

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
    {  # Connector statuses
        'template': 'status*',
        'settings': {'number_of_shards': 3}
    }
]


@send_cfnresponse
def lambda_handler_kinesis(event, context):
    s3_resource = boto3.resource('s3')
    elasticsearch_endpoint = None
    old_elasticsearch_endpoint = None
    if 'ResourceProperties' in event:
        properties = event['ResourceProperties']
        elasticsearch_endpoint = properties.get('ElasticsearchEndpoint')
    if 'OldResourceProperties' in event:
        properties = event['OldResourceProperties']
        old_elasticsearch_endpoint = properties.get('ElasticsearchEndpoint')
    es_client = make_elasticsearch_client(os.environ['ELASTICSEARCH_ENDPOINT'])
    kibana_visualization = _get_kibana_visualization(s3_resource, KIBANA_ASSETS_PATH_KINESIS)

    if event['RequestType'] == 'Create' or \
            (event['RequestType'] == 'Update' and elasticsearch_endpoint != old_elasticsearch_endpoint):
        _register_index_templates(es_client, ES_INDICES_TMPL)
        _register_indices(es_client, KIBANA_INDICES_KINESIS)
        _register_visuals(es_client, kibana_visualization)


@send_cfnresponse
def lambda_handler_iot(event, context):
    s3_resource = boto3.resource('s3')
    elasticsearch_endpoint = None
    old_elasticsearch_endpoint = None
    if 'ResourceProperties' in event:
        properties = event['ResourceProperties']
        elasticsearch_endpoint = properties.get('ElasticsearchEndpoint')
    if 'OldResourceProperties' in event:
        properties = event['OldResourceProperties']
        old_elasticsearch_endpoint = properties.get('ElasticsearchEndpoint')
    es_client = make_elasticsearch_client(os.environ['ELASTICSEARCH_ENDPOINT'])
    kibana_visualization = _get_kibana_visualization(s3_resource, KIBANA_ASSETS_PATH_IOT)

    if event['RequestType'] == 'Create' or \
            (event['RequestType'] == 'Update' and elasticsearch_endpoint != old_elasticsearch_endpoint):
        _register_index_templates(es_client, ES_INDICES_TMPL)
        _register_indices(es_client, KIBANA_INDICES_IOT)
        _register_visuals(es_client, kibana_visualization)


def _get_kibana_visualization(s3_resource, kibana_assets_path):
    regional_bucket_name = os.environ['REGIONAL_LAMBDA_BUCKET_NAME']
    regional_key_prefix = ''
    kibana_export_key = os.path.join(regional_key_prefix, kibana_assets_path)

    kibana_visualization = s3_resource.Object(regional_bucket_name, kibana_export_key).get()['Body'].read().decode()
    return json.loads(kibana_visualization)


def _register_indices(es_client, indices):
    # Initial config must be created first!
    initial_config = {
        'type': 'config',
        'config': {
            'buildNum': 16108
        }
    }
    es_client.index(index='.kibana', doc_type='doc', id='config:6.0.1', body=json.dumps(initial_config))
    es_client.indices.refresh('.kibana')

    for index in indices:
        index_pattern = {
            'type': 'index-pattern',
            'index-pattern': {
                'title': index['name'],
                'timeFieldName': 'timestamp'
            }
        }
        # Kibana uses prefixed ids
        id = 'index-pattern:' + index['name']
        es_client.index(index='.kibana', doc_type='doc', id=id, body=json.dumps(index_pattern))
        es_client.indices.refresh('.kibana')

        if index.get('is_default'):
            config = {
                'doc': {
                    'type': 'config',
                    'config': {
                        'defaultIndex': index['name']
                    }
                }
            }
            es_client.update(index='.kibana', doc_type='doc', id='config:6.0.1', body=json.dumps(config))


def _register_visuals(es_client, kibana_visualization):
    for visual in kibana_visualization:
        visualization = {
            'type': visual['_type'],
            visual['_type']: visual['_source']
        }
        es_client.index(
            index='.kibana',
            doc_type='doc',
            id=visual['_id'],
            body=json.dumps(visualization))


def _register_index_templates(es_client, indices_tmpl):
    for index_tmpl in indices_tmpl:
        es_client.indices.put_template(name=index_tmpl['template'], body=index_tmpl)
