from __future__ import annotations
import typing as _typing
import urllib.parse


class ByteStream:
    def __init__(self, data: bytes):
        self._data = data

    def read(self) -> bytes:
        return self._data


class Response:
    def __init__(
        self,
        status_code: int = 200,
        headers: _typing.Iterable[_typing.Tuple[str, str]] | None = None,
        stream: ByteStream | bytes | None = None,
        request: "Request" | None = None,
    ):
        self.status_code = status_code
        self.headers = list(headers or [])
        if isinstance(stream, ByteStream):
            self._content = stream.read()
        elif hasattr(stream, "read"):
            self._content = stream.read()
        else:
            self._content = stream or b""
        self.request = request

    def json(self):
        import json

        return json.loads(self._content.decode()) if self._content else None


class URL:
    def __init__(self, url: str):
        self._url = url
        parsed = urllib.parse.urlsplit(url)
        self.scheme = parsed.scheme
        host = parsed.hostname or ""
        if parsed.port:
            self.netloc = f"{host}:{parsed.port}".encode("ascii")
        else:
            self.netloc = host.encode("ascii")
        self.path = parsed.path
        self.raw_path = parsed.path.encode("ascii")
        self.query = parsed.query.encode("ascii")

    def join(self, other: _typing.Union[str, "URL"]):
        other_url = str(other) if not isinstance(other, URL) else other._url
        joined = urllib.parse.urljoin(self._url, other_url)
        return URL(joined)

    def __str__(self):
        return self._url


class Request:
    def __init__(
        self,
        method: str,
        url: _typing.Union[str, URL],
        headers: dict[str, str] | None = None,
        content: _typing.Any = None,
    ):
        self.method = method
        self.url = URL(url) if not isinstance(url, URL) else url
        self.headers = headers or {}
        self._content = content

    def read(self) -> bytes:
        if hasattr(self._content, "read"):
            return self._content.read()
        if isinstance(self._content, str):
            return self._content.encode()
        return self._content or b""


class BaseTransport:
    def handle_request(self, request: Request) -> Response:
        raise NotImplementedError


class Client:
    def __init__(
        self,
        *,
        app=None,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
        transport: BaseTransport | None = None,
        follow_redirects: bool = True,
        cookies=None,
        **kwargs,
    ):
        self.app = app
        self.base_url = URL(base_url) if base_url else None
        self.headers = headers or {}
        self._transport = transport
        self.follow_redirects = follow_redirects
        self.cookies = cookies

    def build_url(self, url: _typing.Union[str, URL]) -> URL:
        url_obj = url if isinstance(url, URL) else URL(url)
        if self.base_url and not url_obj.scheme:
            return self.base_url.join(url_obj)
        return url_obj

    def request(
        self,
        method: str,
        url: _typing.Union[str, URL],
        *,
        headers: dict[str, str] | None = None,
        content=None,
        data=None,
        json=None,
        params=None,
        files=None,
        cookies=None,
        auth=None,
        follow_redirects=None,
        timeout=None,
        extensions=None,
    ) -> Response:
        all_headers = {**self.headers, **(headers or {})}
        req = Request(
            method, self.build_url(url), headers=all_headers, content=content or data
        )
        if not self._transport:
            raise RuntimeError("No transport configured")
        return self._transport.handle_request(req)

    def get(self, url, **kwargs):
        return self.request("GET", url, **kwargs)

    def post(self, url, **kwargs):
        return self.request("POST", url, **kwargs)

    def put(self, url, **kwargs):
        return self.request("PUT", url, **kwargs)

    def patch(self, url, **kwargs):
        return self.request("PATCH", url, **kwargs)

    def delete(self, url, **kwargs):
        return self.request("DELETE", url, **kwargs)

    def options(self, url, **kwargs):
        return self.request("OPTIONS", url, **kwargs)

    def head(self, url, **kwargs):
        return self.request("HEAD", url, **kwargs)

    def close(self):
        pass

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.close()


# Submodules for typing compatibility
from types import SimpleNamespace

_types = SimpleNamespace(
    URLTypes=_typing.Any,
    RequestContent=_typing.Any,
    RequestFiles=_typing.Any,
    QueryParamTypes=_typing.Any,
    HeaderTypes=_typing.Any,
    CookieTypes=_typing.Any,
    AuthTypes=_typing.Any,
    TimeoutTypes=_typing.Any,
)
_client = SimpleNamespace(
    USE_CLIENT_DEFAULT=object(),
    UseClientDefault=object,
    CookieTypes=_typing.Any,
    TimeoutTypes=_typing.Any,
    AuthTypes=_typing.Any,
)

# Add missing constants for compatibility
USE_CLIENT_DEFAULT = _client.USE_CLIENT_DEFAULT

__all__ = [
    "ByteStream",
    "Response", 
    "URL",
    "Request",
    "BaseTransport",
    "Client",
    "_types",
    "_client",
    "USE_CLIENT_DEFAULT",
]
