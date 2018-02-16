import boto3
from itertools import islice


def iter_pi_points_from_s3(pi_points_s3_bucket, pi_points_s3_key, buff_size=8192):
    """
    Fetch pi points from file stored on s3.

    :param pi_points_s3_bucket:  s3 bucket where the file is stored
    :param pi_points_s3_key:     s3 key where the file is stored in the bucket
    :param buff_size:            The maximum size of the buffer that will be read from the stream
    :return:                     Yields successive pi points names from the file
    """
    s3 = boto3.resource('s3')
    raw = s3.Object(pi_points_s3_bucket, pi_points_s3_key).get()['Body']

    tail = b''
    stream_part = raw.read(buff_size)
    while stream_part:
        pi_point_list = stream_part.split(b'\n')
        pi_point_list[0] = tail + pi_point_list[0]
        tail = pi_point_list.pop()

        for pi in pi_point_list:
            yield pi.decode()

        stream_part = raw.read(buff_size)

    if tail:
        yield tail.decode()


def iter_list_chunks(l, group_size):
    """
    :param l:           list or iterable
    :param group_size:  size of each group
    :return:            Yields successive group-sized lists from l.
    """
    it = iter(l)
    item = list(islice(it, group_size))
    while item:
        yield item
        item = list(islice(it, group_size))
