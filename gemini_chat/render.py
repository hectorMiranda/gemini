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


_CODE_SPLIT = re.compile(r"(`[^`]+`)")


def _inline(text: str, color: bool) -> str:
    # Split out inline-code spans first so their contents are never treated as
    # bold/italic markup (e.g. `a*b*c` must stay literal).
    out: list[str] = []
    for i, seg in enumerate(_CODE_SPLIT.split(text)):
        if i % 2 == 1:  # an inline-code span including backticks
            inner = seg[1:-1]
            out.append(f"{CYAN}{inner}{RESET}" if color else inner)
        elif color:
            seg = _BOLD.sub(lambda m: f"{BOLD}{m.group(1)}{RESET}", seg)
            seg = _ITALIC.sub(lambda m: f"{ITALIC}{m.group(1)}{RESET}", seg)
            out.append(seg)
        else:
            seg = _BOLD.sub(r"\1", seg)
            seg = _ITALIC.sub(r"\1", seg)
            out.append(seg)
    return "".join(out)


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
