"""Render a subset of Markdown to ANSI for the terminal.

Deliberately small: headings, bold/italic, inline code and fenced code blocks.
With color disabled it strips the markers so piped/redirected output stays clean.
"""

from __future__ import annotations

import re

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
ITALIC = "\033[3m"
CYAN = "\033[36m"

_FENCE = re.compile(r"^```")
_INLINE_CODE = re.compile(r"`([^`]+)`")
_BOLD = re.compile(r"\*\*([^*]+)\*\*")
_ITALIC = re.compile(r"(?<!\*)\*([^*]+)\*(?!\*)")
_HEADING = re.compile(r"^(#{1,6})\s+(.*)$")


def _inline(text: str, color: bool) -> str:
    if color:
        text = _INLINE_CODE.sub(lambda m: f"{CYAN}{m.group(1)}{RESET}", text)
        text = _BOLD.sub(lambda m: f"{BOLD}{m.group(1)}{RESET}", text)
        text = _ITALIC.sub(lambda m: f"{ITALIC}{m.group(1)}{RESET}", text)
    else:
        text = _INLINE_CODE.sub(r"\1", text)
        text = _BOLD.sub(r"\1", text)
        text = _ITALIC.sub(r"\1", text)
    return text


def render(text: str, color: bool = True) -> str:
    out: list[str] = []
    in_code = False
    for line in text.splitlines():
        if _FENCE.match(line):
            in_code = not in_code
            continue
        if in_code:
            out.append(f"{DIM}    {line}{RESET}" if color else f"    {line}")
            continue
        heading = _HEADING.match(line)
        if heading:
            body = heading.group(2)
            out.append(f"{BOLD}{body}{RESET}" if color else body)
            continue
        out.append(_inline(line, color))
    return "\n".join(out)
