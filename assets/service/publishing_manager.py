import functools
import itertools

import datetime
from concurrent.futures import ThreadPoolExecutor

import boto3


class PublishingManager:

    def __init__(self, s3_resource):
        self.s3_resource = s3_resource

    @staticmethod
    def create_manager():
        session = boto3.session.Session()
        s3_resource = session.resource('s3')
        return PublishingManager(s3_resource)

    @staticmethod
    def _iter_date_range(from_datetime, to_datetime, timedelta_step):
        while from_datetime < to_datetime:
            yield from_datetime
            from_datetime += timedelta_step

    def _iter_prefixes_to_publish(self, from_datetime, to_datetime, data_prefix):

        def make_hour_prefix(dt):
            return dt.strftime(data_prefix + '/%Y/%m/%d/%H')

        def make_day_prefix(dt):
            return dt.strftime(data_prefix + '/%Y/%m/%d')

        first_day_end = (from_datetime + datetime.timedelta(days=1)).replace(hour=0)
        last_day_start = to_datetime.replace(hour=0)
        last_day_end = to_datetime.replace(minute=1)
        first_day_hours = self._iter_date_range(from_datetime, first_day_end, datetime.timedelta(hours=1))
        days = self._iter_date_range(first_day_end, last_day_start, datetime.timedelta(days=1))
        last_day_hours = self._iter_date_range(last_day_start, last_day_end, datetime.timedelta(hours=1))
        return itertools.chain(
            map(make_hour_prefix, first_day_hours),
            map(make_day_prefix, days),
            map(make_hour_prefix, last_day_hours)
        )

    def _iter_object_keys_to_publish(self, from_datetime, to_datetime, curated_bucket_name, data_prefix):
        for prefix in self._iter_prefixes_to_publish(from_datetime, to_datetime, data_prefix):
            for source_object in self.s3_resource.Bucket(curated_bucket_name).objects.filter(Prefix=prefix):
                yield source_object.key

    def _make_publish_job(self, curated_bucket_name, publishing_bucket_name, object_key):
        # It is recommended to create a resource instance for each thread in a multithreaded applications
        # https://boto3.readthedocs.io/en/latest/guide/resources.html#multithreading-multiprocessing
        session = boto3.session.Session()
        s3_resource = session.resource('s3')
        destination_object = s3_resource.ObjectSummary(publishing_bucket_name, object_key)
        return functools.partial(
            destination_object.copy_from, CopySource='{}/{}'.format(curated_bucket_name, object_key)
        )

    def publish_firehose_data(self, from_datetime, to_datetime, curated_bucket_name, publishing_bucket_name,
                              data_prefix):
        assert (from_datetime <= to_datetime)
        object_keys = self._iter_object_keys_to_publish(from_datetime, to_datetime, curated_bucket_name, data_prefix)
        object_keys = list(object_keys)
        with ThreadPoolExecutor(max_workers=15) as executor:
            futures = []
            for object_key in object_keys:
                publish_job = self._make_publish_job(curated_bucket_name, publishing_bucket_name, object_key)
                future = executor.submit(publish_job)
                futures.append(future)
        for future in futures:
            exception = future.exception()
            if exception is not None:
                raise exception

