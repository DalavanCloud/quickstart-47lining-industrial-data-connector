import os
import datetime

from source.utils import make_elasticsearch_client


def get_all_indexes_by_prefix(es_client, index_prefix):
    return list(es_client.indices.get_settings(
        index='{}*'.format(index_prefix),
        params={'expand_wildcards': 'open,closed'}))


def filter_indexes_by_name_and_age(indexes, index_prefix, max_index_age):
    filtered_indexes = []
    current_date = datetime.datetime.today()
    index_date_pattern = '{}-%Y-%m-%d'.format(index_prefix)
    for index in indexes:
        index_date = datetime.datetime.strptime(index, index_date_pattern)
        if (current_date - index_date).days > max_index_age:
            filtered_indexes.append(index)
    return filtered_indexes


def delete_indexes_by_name_and_age(es_client, index_prefix, max_index_age):
    indexes = get_all_indexes_by_prefix(es_client, index_prefix)
    indexes_to_delete = filter_indexes_by_name_and_age(indexes, index_prefix, max_index_age)

    if indexes_to_delete:
        indexes_to_delete_formatted = ','.join(indexes_to_delete)
        print('Found {} indexes to delete'.format(len(indexes_to_delete)))
        print('{} will be deleted'.format(indexes_to_delete_formatted))
        es_client.indices.delete(indexes_to_delete_formatted)


def es_index_clean_handler(event, context):
    index_prefix = os.environ['INDEX_PREFIX']
    max_index_age = int(os.environ['MAX_INDEX_AGE'])
    es_client = make_elasticsearch_client(os.environ['ELASTICSEARCH_ENDPOINT'])

    delete_indexes_by_name_and_age(es_client, index_prefix, max_index_age)
