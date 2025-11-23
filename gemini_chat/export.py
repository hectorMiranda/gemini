"""Export a conversation to Markdown, JSON or HTML."""

from __future__ import annotations

import html
import json
from pathlib import Path

from .models import Conversation, Role

_LABELS = {Role.USER: "You", Role.MODEL: "Gemini"}


def to_markdown(conv: Conversation, title: str = "Conversation") -> str:
    lines = [f"# {title}", ""]
    if conv.system_instruction:
        lines += [f"> **System:** {conv.system_instruction}", ""]
    for msg in conv.messages:
        lines.append(f"**{_LABELS.get(msg.role, msg.role.value)}:**")
        lines.append("")
        text = msg.text_content
        attachments = sum(1 for p in msg.parts if p.data is not None)
        lines.append(text if text else "_(no text)_")
        if attachments:
            lines.append("")
            lines.append(f"_({attachments} attachment{'s' if attachments != 1 else ''})_")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def to_json(conv: Conversation) -> str:
    data = {
        "system_instruction": conv.system_instruction,
        "messages": [{"role": m.role.value, "text": m.text_content} for m in conv.messages],
    }
    return json.dumps(data, indent=2)


def to_html(conv: Conversation, title: str = "Conversation") -> str:
    rows = []
    for msg in conv.messages:
        who = _LABELS.get(msg.role, msg.role.value)
        body = html.escape(msg.text_content).replace("\n", "<br>")
        rows.append(f'<div class="msg {msg.role.value}"><b>{who}</b><p>{body}</p></div>')
    sys_block = (
        f'<div class="sys">System: {html.escape(conv.system_instruction)}</div>'
        if conv.system_instruction
        else ""
    )
    return (
        f"<!doctype html><html><head><meta charset='utf-8'><title>{html.escape(title)}</title>"
        "<style>body{font-family:system-ui;max-width:760px;margin:2rem auto;line-height:1.5}"
        ".msg{margin:1rem 0;padding:.5rem 1rem;border-radius:8px}.user{background:#eef}"
        ".model{background:#efe}.sys{color:#666;font-style:italic}</style></head>"
        f"<body><h1>{html.escape(title)}</h1>{sys_block}{''.join(rows)}</body></html>\n"
    )


def write_export(conv: Conversation, path: str | Path) -> str:
    """Write the conversation to a file, choosing the format from its extension."""
    p = Path(path).expanduser()
    suffix = p.suffix.lower()
    if suffix == ".json":
        content = to_json(conv)
    elif suffix in (".html", ".htm"):
        content = to_html(conv)
    else:
        content = to_markdown(conv)
    p.write_text(content, encoding="utf-8")
    return suffix.lstrip(".") or "md"
