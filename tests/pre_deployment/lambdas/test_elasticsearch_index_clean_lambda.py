import pytest
from time import sleep
from freezegun import freeze_time
from elasticsearch import Elasticsearch
from source.elasticsearch_index_clean_lambda import get_all_indexes_by_prefix, filter_indexes_by_name_and_age, \
    delete_indexes_by_name_and_age


def _setup_indexes(elasticsearch_client, indexes_names):
    for index_name in indexes_names:
        elasticsearch_client.indices.create(index=index_name, ignore=[400, 404])
    sleep(1)


@pytest.fixture()
def elasticsearch_client(request):
    def clean_es():
        es.indices.delete('*')

    es = Elasticsearch(
        endpoint='localhost',
        port=9200,
        http_auth=('elastic', 'changeme')
    )
    request.addfinalizer(clean_es)
    return es


def test_get_all_indexes(elasticsearch_client):
    indexes_names = ['test-index-1', 'test-index-2', 'test-index-3']
    _setup_indexes(elasticsearch_client, indexes_names)

    assert(indexes_names == sorted(get_all_indexes_by_prefix(elasticsearch_client, 'test-index')))


@freeze_time('2017-11-15 00:00:00')
def test_filter_by_name_and_age():
    indexes_names = ['test-index-2017-11-15', 'test-index-2017-11-14',
                     'test-index-2017-11-13', 'test-index-2017-11-12',
                     'test-index-2017-11-11', 'test-index-2017-11-10']

    filtered_indexes = filter_indexes_by_name_and_age(indexes_names, 'test-index', 3)

    assert(['test-index-2017-11-10', 'test-index-2017-11-11'] == sorted(filtered_indexes))


@freeze_time('2017-11-15 00:00:00')
def test_delete_indexes_by_name_and_age(elasticsearch_client):
    indexes_names = ['test-index-2017-11-15', 'test-index-2017-11-14',
                     'test-index-2017-11-13', 'test-index-2017-11-12',
                     'test-index-2017-11-11', 'test-index-2017-11-10']
    _setup_indexes(elasticsearch_client, indexes_names)

    delete_indexes_by_name_and_age(elasticsearch_client, 'test-index', 3)
    all_indexes = get_all_indexes_by_prefix(elasticsearch_client, 'test-index')

    assert(['test-index-2017-11-12', 'test-index-2017-11-13',
            'test-index-2017-11-14', 'test-index-2017-11-15'] == sorted(all_indexes))
