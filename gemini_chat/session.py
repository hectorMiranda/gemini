"""Persist and restore conversations as JSON."""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

from .config import sessions_dir
from .models import Conversation, Message, Part, Role

_SAFE = re.compile(r"[^A-Za-z0-9._-]+")


def _safe_name(name: str) -> str:
    cleaned = _SAFE.sub("-", name.strip()).strip("-")
    if not cleaned:
        raise ValueError("invalid session name")
    return cleaned


def to_dict(conv: Conversation) -> dict:
    return {
        "system_instruction": conv.system_instruction,
        "messages": [m.to_wire() for m in conv.messages],
    }


def from_dict(data: dict) -> Conversation:
    conv = Conversation(system_instruction=data.get("system_instruction"))
    for m in data.get("messages", []):
        parts = []
        for p in m.get("parts", []):
            if "inlineData" in p:
                inline = p["inlineData"]
                parts.append(Part(mime_type=inline.get("mimeType"), data=base64.b64decode(inline["data"])))
            else:
                parts.append(Part(text=p.get("text", "")))
        conv.messages.append(Message(role=Role(m.get("role", "user")), parts=parts))
    return conv


def _path(name: str, directory: Path | None) -> Path:
    directory = directory or sessions_dir()
    return directory / f"{_safe_name(name)}.json"


def save_session(name: str, conv: Conversation, directory: Path | None = None) -> Path:
    path = _path(name, directory)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(to_dict(conv), indent=2), encoding="utf-8")
    return path


def load_session(name: str, directory: Path | None = None) -> Conversation:
    path = _path(name, directory)
    if not path.exists():
        raise FileNotFoundError(f"no session named '{name}'")
    return from_dict(json.loads(path.read_text(encoding="utf-8")))


def list_sessions(directory: Path | None = None) -> list[str]:
    directory = directory or sessions_dir()
    if not directory.exists():
        return []
    return sorted(p.stem for p in directory.glob("*.json"))


def delete_session(name: str, directory: Path | None = None) -> bool:
    path = _path(name, directory)
    if path.exists():
        path.unlink()
        return True
    return False
