"""Exception hierarchy for the client."""

from __future__ import annotations


class GeminiError(Exception):
    """Base class for all client errors."""


class ApiError(GeminiError):
    def __init__(self, status: int, message: str, body: str | None = None):
        super().__init__(f"API error {status}: {message}")
        self.status = status
        self.message = message
        self.body = body


class AuthError(ApiError):
    """401/403 — bad or missing API key."""


class RateLimitError(ApiError):
    """429 — quota or rate limit exceeded."""
