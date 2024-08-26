"""Conversation data model and (de)serialization to the Gemini wire format."""

from __future__ import annotations

import base64
from dataclasses import dataclass, field
from enum import Enum


class Role(str, Enum):
    USER = "user"
    MODEL = "model"


@dataclass
class Part:
    """A single piece of content: text, or inline binary data (image, etc.)."""

    text: str | None = None
    mime_type: str | None = None
    data: bytes | None = None

    def to_wire(self) -> dict:
        if self.data is not None:
            return {
                "inlineData": {
                    "mimeType": self.mime_type or "application/octet-stream",
                    "data": base64.b64encode(self.data).decode("ascii"),
                }
            }
        return {"text": self.text or ""}


@dataclass
class Message:
    role: Role
    parts: list[Part] = field(default_factory=list)

    @classmethod
    def text(cls, role: Role, text: str) -> "Message":
        return cls(role=role, parts=[Part(text=text)])

    @property
    def text_content(self) -> str:
        return "".join(p.text for p in self.parts if p.text)

    def to_wire(self) -> dict:
        return {"role": self.role.value, "parts": [p.to_wire() for p in self.parts]}


@dataclass
class Conversation:
    messages: list[Message] = field(default_factory=list)
    system_instruction: str | None = None

    def add_user(self, text: str, parts: list[Part] | None = None) -> Message:
        msg = Message(role=Role.USER, parts=parts or [Part(text=text)])
        self.messages.append(msg)
        return msg

    def add_model(self, text: str) -> Message:
        msg = Message.text(Role.MODEL, text)
        self.messages.append(msg)
        return msg

    def to_contents(self) -> list[dict]:
        return [m.to_wire() for m in self.messages]

    def clear(self) -> None:
        self.messages.clear()
