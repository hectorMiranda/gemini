"""A tiny HTTP transport abstraction over urllib.

The client depends only on the :class:`Transport` protocol, so tests can inject a
fake and we never need a third-party HTTP library.
"""

from __future__ import annotations

import urllib.error
import urllib.request
from typing import IO, Iterator, Protocol


class TransportError(Exception):
    """Network-level failure (DNS, connection refused, timeout)."""


class HttpResponse:
    """Wraps a readable byte stream with status + headers and line iteration."""

    def __init__(self, status: int, headers: dict[str, str], raw: IO[bytes]):
        self.status = status
        self.headers = headers
        self._raw = raw

    def read(self) -> bytes:
        return self._raw.read()

    def text(self) -> str:
        return self.read().decode("utf-8", "replace")

    def iter_lines(self) -> Iterator[str]:
        for line in self._raw:
            yield line.decode("utf-8", "replace").rstrip("\r\n")

    def close(self) -> None:
        try:
            self._raw.close()
        except Exception:
            pass


class Transport(Protocol):
    def request(
        self, method: str, url: str, *, headers: dict[str, str] | None = None, body: bytes | None = None
    ) -> HttpResponse: ...


class UrllibTransport:
    """Default transport backed by urllib.request."""

    def __init__(self, timeout: float = 60.0):
        self.timeout = timeout

    def request(
        self, method: str, url: str, *, headers: dict[str, str] | None = None, body: bytes | None = None
    ) -> HttpResponse:
        req = urllib.request.Request(url, data=body, method=method, headers=headers or {})
        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            return HttpResponse(resp.status, dict(resp.headers), resp)
        except urllib.error.HTTPError as e:
            # HTTPError is itself a readable response — surface it to the client.
            return HttpResponse(e.code, dict(e.headers or {}), e)
        except urllib.error.URLError as e:
            raise TransportError(str(e.reason)) from e
