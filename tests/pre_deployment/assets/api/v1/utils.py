import json
from copy import deepcopy


def parse_response(raw_response):
    responses = list(raw_response.response)
    assert len(responses) == 1
    response = responses[0]
    raw_response.response = json.loads(response)
    return raw_response


def copy_db_objects(objects):
    return [deepcopy(object) for object in objects]
