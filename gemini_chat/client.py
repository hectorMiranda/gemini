"""Gemini API client built on the transport abstraction."""

from __future__ import annotations

import json
import time
import urllib.parse
from dataclasses import dataclass
from typing import Callable

from .config import Config
from .errors import ApiError, AuthError, GeminiError, RateLimitError
from .models import Conversation
from .transport import HttpResponse, Transport, TransportError, UrllibTransport


@dataclass
class GenerateResult:
    text: str
    prompt_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str | None = None
    raw: dict | None = None


class GeminiClient:
    # Status codes worth retrying (transient).
    _RETRYABLE = {429, 500, 502, 503, 504}

    def __init__(
        self,
        config: Config,
        transport: Transport | None = None,
        sleep: Callable[[float], None] = time.sleep,
        tools: list | None = None,
    ):
        self.config = config
        self.transport = transport or UrllibTransport()
        self._sleep = sleep
        self.tools = tools or []

    def _request(self, method: str, url: str, body: bytes) -> HttpResponse:
        """Issue a request, retrying transient failures with exponential backoff."""
        attempts = max(0, self.config.retries) + 1
        headers = {"Content-Type": "application/json"}
        last: HttpResponse | None = None
        for attempt in range(attempts):
            try:
                resp = self.transport.request(method, url, headers=headers, body=body)
            except TransportError:
                if attempt + 1 >= attempts:
                    raise
                self._sleep(2**attempt * 0.5)
                continue
            if resp.status in self._RETRYABLE and attempt + 1 < attempts:
                resp.close()
                self._sleep(2**attempt * 0.5)
                last = resp
                continue
            return resp
        return last  # type: ignore[return-value]

    def _url(self, action: str, query: dict | None = None) -> str:
        params = {"key": self.config.require_api_key(), **(query or {})}
        qs = urllib.parse.urlencode(params)
        return f"{self.config.base_url}/models/{self.config.model}:{action}?{qs}"

    def _generation_config(self) -> dict:
        cfg: dict = {"temperature": self.config.temperature}
        if self.config.max_output_tokens:
            cfg["maxOutputTokens"] = self.config.max_output_tokens
        return cfg

    def _request_body(self, conversation: Conversation) -> dict:
        body: dict = {
            "contents": conversation.to_contents(),
            "generationConfig": self._generation_config(),
        }
        system = conversation.system_instruction or self.config.system_instruction
        if system:
            body["systemInstruction"] = {"parts": [{"text": system}]}
        if self.tools:
            from .tools import to_request

            body["tools"] = to_request(self.tools)
        return body

    def generate(self, conversation: Conversation) -> GenerateResult:
        """Single (non-streaming) completion for the current conversation."""
        url = self._url("generateContent")
        payload = json.dumps(self._request_body(conversation)).encode("utf-8")
        resp = self._request("POST", url, payload)
        raw = resp.read()
        if resp.status != 200:
            self._raise_for_status(resp.status, raw)
        data = json.loads(raw)
        return self._parse_result(data)

    def stream(self, conversation: Conversation):
        """Yield text deltas as the model produces them (Server-Sent Events)."""
        url = self._url("streamGenerateContent", {"alt": "sse"})
        payload = json.dumps(self._request_body(conversation)).encode("utf-8")
        resp = self._request("POST", url, payload)
        if resp.status != 200:
            self._raise_for_status(resp.status, resp.read())
        for line in resp.iter_lines():
            if not line.startswith("data:"):
                continue
            data = line[len("data:"):].strip()
            if not data or data == "[DONE]":
                continue
            try:
                obj = json.loads(data)
            except json.JSONDecodeError:
                continue
            for cand in obj.get("candidates", []):
                for part in cand.get("content", {}).get("parts", []):
                    text = part.get("text")
                    if text:
                        yield text

    @staticmethod
    def _raise_for_status(status: int, body: bytes) -> None:
        text = body.decode("utf-8", "replace")
        message = text
        try:
            message = json.loads(text).get("error", {}).get("message", text)
        except Exception:
            pass
        if status in (401, 403):
            raise AuthError(status, message, text)
        if status == 429:
            raise RateLimitError(status, message, text)
        raise ApiError(status, message, text)

    @staticmethod
    def _parse_result(data: dict) -> GenerateResult:
        candidates = data.get("candidates") or []
        if not candidates:
            feedback = data.get("promptFeedback", {})
            raise GeminiError(f"No candidates returned (feedback: {feedback})")
        cand = candidates[0]
        parts = cand.get("content", {}).get("parts", [])
        text = "".join(p.get("text", "") for p in parts)
        usage = data.get("usageMetadata", {})
        return GenerateResult(
            text=text,
            prompt_tokens=usage.get("promptTokenCount", 0),
            output_tokens=usage.get("candidatesTokenCount", 0),
            total_tokens=usage.get("totalTokenCount", 0),
            finish_reason=cand.get("finishReason"),
            raw=data,
        )
