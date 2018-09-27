import datetime
import json
import logging
import uuid

log = logging.getLogger(__name__)


class SQSService:

    def __init__(self, incoming_queue=None, backfill_queue=None, interpolation_queue=None, subscription_queue=None,
                 outgoing_queue=None):
        self.outgoing_queue = outgoing_queue
        self.actions_queues_mapping = {
            'backfill': backfill_queue,
            'interpolate': interpolation_queue,
            'subscribe': subscription_queue,
            'unsubscribe': subscription_queue,
            'sync_as': incoming_queue,
            'sync_feeds': incoming_queue
        }

    def send_message(self, payload, action, id=None):
        return self._send_structured_message(
            action=action,
            queue=self.actions_queues_mapping[action],
            payload=payload,
            id=id
        )

    def generate_unique_id(self):
        return str(uuid.uuid4())

    def _send_structured_message(self, action, queue, payload=None, id=None):
        msg = {
            'id': id if id is not None else self.generate_unique_id(),
            'created_at': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
            'action': action,
        }
        if payload is not None:
            msg['payload'] = payload
        self._send_message_json(msg, queue)
        return msg['id']

    @staticmethod
    def _send_message_text(message, queue):
        assert type(message) is str
        try:
            log.info('Sending message:\n{}'.format(message))
            queue.send_message(MessageBody=message)
        except Exception as e:
            logging.error(e)

    def _send_message_json(self, message, queue):
        text = json.dumps(message)
        self._send_message_text(text, queue)

    def _get_queues(self):
        unique_queues = list(set(self.actions_queues_mapping.values()))
        return [self.outgoing_queue] + unique_queues

    @staticmethod
    def _purge_queue(queue):
        queue.purge()

    def purge_all_queues(self):
        [self._purge_queue(queue) for queue in self._get_queues() if queue is not None]
