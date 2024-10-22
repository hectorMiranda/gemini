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


class FakeClient:
    """A GeminiClient stand-in that returns scripted replies."""

    def __init__(self, replies: list[str] | None = None):
        self.replies = list(replies or [])
        self.seen: list = []

    def generate(self, conversation):
        from gemini_chat.client import GenerateResult

        self.seen.append(list(conversation.messages))
        text = self.replies.pop(0) if self.replies else "ok"
        return GenerateResult(text=text, total_tokens=1)

    def stream(self, conversation):
        self.seen.append(list(conversation.messages))
        text = self.replies.pop(0) if self.replies else "ok"
        # Yield in a couple of chunks to exercise streaming assembly.
        mid = max(1, len(text) // 2)
        yield text[:mid]
        yield text[mid:]
