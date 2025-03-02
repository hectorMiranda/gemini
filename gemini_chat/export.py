"""Export a conversation to Markdown."""

from __future__ import annotations

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
