FEED_GROUP_EVENT_ID_SEPARATOR = '|'


def get_feed_group_message_id(id, event_id):
    return '{}{}{}'.format(event_id, FEED_GROUP_EVENT_ID_SEPARATOR, id)


def split_feed_group_message_id(msg_id):
    parts = msg_id.split(FEED_GROUP_EVENT_ID_SEPARATOR)
    return {
        'id': int(parts[1]),
        'event_id': parts[0]
    }
