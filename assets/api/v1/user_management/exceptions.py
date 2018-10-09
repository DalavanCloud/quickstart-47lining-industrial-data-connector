from api.api_utils import BackendException, compose_error_payload


class CognitoException(BackendException):
    def __init__(self, message, exception):
        payload = compose_error_payload(exception)
        super().__init__(message=message, payload=payload)

    @classmethod
    def from_client_error(cls, client_error):
        message = client_error.response['Error']['Message']
        return cls(message, client_error)
