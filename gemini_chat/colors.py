"""Terminal color themes for the prompt and role labels."""

from __future__ import annotations

RESET = "\033[0m"

THEMES: dict[str, dict[str, str]] = {
    "default": {"prompt": "\033[36m", "model": "\033[32m"},
    "warm": {"prompt": "\033[33m", "model": "\033[35m"},
    "mono": {"prompt": "", "model": ""},
}

_BASE_PROMPT = "gemini › "


def prompt_label(theme: str = "default", color: bool = True) -> str:
    if not color:
        return _BASE_PROMPT
    code = THEMES.get(theme, THEMES["default"]).get("prompt", "")
    return f"{code}{_BASE_PROMPT}{RESET}" if code else _BASE_PROMPT
