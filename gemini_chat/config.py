"""Runtime configuration, sourced from the environment with sensible defaults."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_MODEL = "gemini-1.5-flash"
DEFAULT_BASE_URL = "https://generativelanguage.googleapis.com/v1beta"


def config_dir() -> Path:
    """Return the config directory, honoring XDG_CONFIG_HOME."""
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(Path.home(), ".config")
    return Path(base) / "gemini-chat"


def sessions_dir() -> Path:
    """Where saved conversations live."""
    return config_dir() / "sessions"


@dataclass
class Config:
    api_key: str | None = None
    model: str = DEFAULT_MODEL
    base_url: str = DEFAULT_BASE_URL
    temperature: float = 0.7
    max_output_tokens: int | None = None
    system_instruction: str | None = None
    stream: bool = True
    theme: str = "default"
    extra: dict = field(default_factory=dict)

    @classmethod
    def from_env(cls, env: dict | None = None) -> "Config":
        env = os.environ if env is None else env
        temp = env.get("GEMINI_TEMPERATURE")
        max_tok = env.get("GEMINI_MAX_TOKENS")
        return cls(
            api_key=env.get("GEMINI_API_KEY") or env.get("GOOGLE_API_KEY"),
            model=env.get("GEMINI_MODEL", DEFAULT_MODEL),
            base_url=env.get("GEMINI_BASE_URL", DEFAULT_BASE_URL),
            temperature=float(temp) if temp else 0.7,
            max_output_tokens=int(max_tok) if max_tok else None,
            system_instruction=env.get("GEMINI_SYSTEM"),
        )

    def require_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError(
                "No API key. Set GEMINI_API_KEY (get one at https://aistudio.google.com/apikey)."
            )
        return self.api_key
