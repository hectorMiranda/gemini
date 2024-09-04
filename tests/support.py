"""Test doubles."""

from __future__ import annotations

import io

from gemini_chat.transport import HttpResponse


class FakeTransport:
    """A Transport that returns canned responses and records requests."""

    def __init__(self, responses: list[tuple[int, bytes]]):
        self.responses = list(responses)
        self.calls: list[dict] = []

    def request(self, method, url, *, headers=None, body=None) -> HttpResponse:
        self.calls.append({"method": method, "url": url, "headers": headers, "body": body})
        status, data = self.responses.pop(0)
        return HttpResponse(status, {}, io.BytesIO(data))

    @property
    def last_body_json(self) -> dict:
        import json

        return json.loads(self.calls[-1]["body"])
