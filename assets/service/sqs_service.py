import datetime
import json
import logging
import uuid

log = logging.getLogger(__name__)


class SQSService:

    def __init__(self, incoming_queue=None, outgoing_queue=None):
        self.incoming_queue = incoming_queue
        self.outgoing_queue = outgoing_queue

    def send_structured_message(self, action, payload=None):
        assert self.incoming_queue is not None
        msg = {
            'id': str(uuid.uuid4()),
            'created_at': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%S'),
            'action': action,
        }
        if payload is not None:
            msg['payload'] = payload
        self._send_message_json(msg)
        return msg['id']

    def iter_messages(self, long_polling_seconds=0):
        """
        Get messages from a Queue using long polling
        :return: list of tuples (action of type str, payload of type dict)
        """
        assert self.outgoing_queue is not None
        for message in self.outgoing_queue.receive_messages(WaitTimeSeconds=long_polling_seconds):
            log.info('Received message:\n{}'.format(message.body))
            parsed_message = json.loads(message.body)
            uid = parsed_message['id']
            payload = parsed_message['payload']
            action = parsed_message['action']
            message.delete()
            yield (uid, action, payload)

    def _send_message_text(self, message):
        assert type(message) is str
        try:
            log.info('Sending message:\n{}'.format(message))
            self.incoming_queue.send_message(MessageBody=message)
        except Exception as e:
            logging.error(e)

    def _send_message_json(self, message):
        text = json.dumps(message)
        self._send_message_text(text)
