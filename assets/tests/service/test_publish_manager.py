from datetime import datetime
from io import BytesIO

from mock import mock
from tests.fixtures import *


def test_publish_firehose_data(publishing_manager, s3_resource):
    keys = [
        'data/2017/11/28/00/stream-a',
        'data/2017/11/28/23/stream-b',
        'data/2017/11/29/15/stream-c',
        'data/2017/11/30/00/stream-d',
        'data/2017/11/30/12/stream-e',
        'data/2017/11/30/13/stream-f'
    ]
    for key in keys:
        s3_resource.Bucket('curated-datasets-bucket').upload_fileobj(
            Fileobj=BytesIO(b'data'),
            Key=key
        )

    publishing_manager.publish_firehose_data(
        from_datetime=datetime(2017, 11, 28, 0),
        to_datetime=datetime(2017, 11, 30, 12),
        curated_bucket_name='curated-datasets-bucket',
        publishing_bucket_name='published-data-bucket',
        data_prefix='data'
    )

    published_objects = set(obj.key for obj in s3_resource.Bucket('published-data-bucket').objects.all())

    assert published_objects == {
        'data/2017/11/28/00/stream-a',
        'data/2017/11/28/23/stream-b',
        'data/2017/11/29/15/stream-c',
        'data/2017/11/30/00/stream-d',
        'data/2017/11/30/12/stream-e'
    }