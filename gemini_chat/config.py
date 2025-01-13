"""Runtime configuration, sourced from the environment with sensible defaults."""

from __future__ import annotations

import os
import tomllib
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


def config_file() -> Path:
    return config_dir() / "config.toml"


# Keys that may appear in config.toml, with their parsers.
_FILE_FIELDS = {
    "model": str,
    "base_url": str,
    "temperature": float,
    "max_output_tokens": int,
    "system_instruction": str,
    "stream": bool,
    "theme": str,
    "retries": int,
    "color": bool,
}


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
    retries: int = 2
    color: bool = True
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

    def apply_file(self, data: dict) -> "Config":
        """Overlay values parsed from a config.toml dict onto this config."""
        for key, parse in _FILE_FIELDS.items():
            if key in data and data[key] is not None:
                setattr(self, key, parse(data[key]))
        return self

    @classmethod
    def load(cls, path: Path | None = None, env: dict | None = None) -> "Config":
        """File first, then environment overrides (env wins)."""
        path = path or config_file()
        config = cls()
        if path.exists():
            config.apply_file(tomllib.loads(path.read_text(encoding="utf-8")))
        env_config = cls.from_env(env)
        # Env overrides only where it actually carries a value.
        e = os.environ if env is None else env
        if e.get("GEMINI_API_KEY") or e.get("GOOGLE_API_KEY"):
            config.api_key = env_config.api_key
        else:
            config.api_key = env_config.api_key or config.api_key
        for key in ("GEMINI_MODEL", "GEMINI_BASE_URL", "GEMINI_TEMPERATURE", "GEMINI_MAX_TOKENS", "GEMINI_SYSTEM"):
            if key in e:
                attr = {
                    "GEMINI_MODEL": "model",
                    "GEMINI_BASE_URL": "base_url",
                    "GEMINI_TEMPERATURE": "temperature",
                    "GEMINI_MAX_TOKENS": "max_output_tokens",
                    "GEMINI_SYSTEM": "system_instruction",
                }[key]
                setattr(config, attr, getattr(env_config, attr))
        return config

    def require_api_key(self) -> str:
        if not self.api_key:
            raise RuntimeError(
                "No API key. Set GEMINI_API_KEY (get one at https://aistudio.google.com/apikey)."
            )
        return self.api_key
