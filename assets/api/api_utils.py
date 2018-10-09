from functools import wraps
import logging
import traceback


logger = logging.getLogger(__name__)


class BackendException(Exception):
    """Base class for exceptions raised by API methods
    Makes easier to handle exceptions in webapp
    """

    def __init__(self, message, status_code=500, payload=None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        result = dict(self.payload or ())
        result['message'] = self.message
        return result


def compose_error_payload(exception):
    tb = traceback.format_exc()
    error_payload = {
        'exception': exception.__class__.__name__,
        'description': str(exception),
        'traceback': tb
    }
    return error_payload


def raise_backend_exception(error_message):

    def outer(fun):
        @wraps(fun)
        def inner(*args, **kwargs):
            try:
                response = fun(*args, **kwargs)
            except Exception as e:
                if isinstance(e, BackendException):
                    raise

                payload = compose_error_payload(e)
                logger.exception("%s:\n%s", error_message, payload['traceback'])
                raise BackendException(error_message, payload=payload)
            return response

        return inner

    return outer
