"""Gemini API client built on the transport abstraction."""

from __future__ import annotations

import json
import urllib.parse
from dataclasses import dataclass

from .config import Config
from .errors import ApiError, AuthError, GeminiError, RateLimitError
from .models import Conversation
from .transport import Transport, UrllibTransport


@dataclass
class GenerateResult:
    text: str
    prompt_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    finish_reason: str | None = None
    raw: dict | None = None


class GeminiClient:
    def __init__(self, config: Config, transport: Transport | None = None):
        self.config = config
        self.transport = transport or UrllibTransport()

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
        return body

    def generate(self, conversation: Conversation) -> GenerateResult:
        """Single (non-streaming) completion for the current conversation."""
        url = self._url("generateContent")
        payload = json.dumps(self._request_body(conversation)).encode("utf-8")
        resp = self.transport.request(
            "POST", url, headers={"Content-Type": "application/json"}, body=payload
        )
        raw = resp.read()
        if resp.status != 200:
            self._raise_for_status(resp.status, raw)
        data = json.loads(raw)
        return self._parse_result(data)

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
