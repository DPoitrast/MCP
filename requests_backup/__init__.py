class RequestException(Exception):
    """Base class for request-related exceptions."""


class HTTPError(RequestException):
    def __init__(self, message="HTTP error", response=None):
        super().__init__(message)
        self.response = response


class ConnectionError(RequestException):
    pass


class Response:
    def __init__(self, status_code=200, reason="OK", json_data=None):
        self.status_code = status_code
        self.reason = reason
        self._json = json_data

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise HTTPError(response=self)


# Namespace for exceptions
class _Exceptions:
    RequestException = RequestException
    HTTPError = HTTPError
    ConnectionError = ConnectionError


exceptions = _Exceptions()


def get(*args, **kwargs):
    raise NotImplementedError("HTTP requests not supported in stub")
