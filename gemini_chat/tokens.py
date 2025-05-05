"""Rough token estimation (no tokenizer dependency).

Uses a hybrid of word and character counts that tracks the real Gemini tokenizer
closely enough for a usage indicator. Not exact — labelled as an estimate in the UI.
"""

from __future__ import annotations

import re

from .models import Conversation

_WORD = re.compile(r"\w+|[^\w\s]")


def estimate_tokens(text: str) -> int:
    if not text:
        return 0
    tokens = len(_WORD.findall(text))
    # Blend token-ish word count with a chars/4 floor for long words.
    return max(tokens, len(text) // 4)


def conversation_tokens(conv: Conversation) -> int:
    total = estimate_tokens(conv.system_instruction or "")
    for msg in conv.messages:
        total += estimate_tokens(msg.text_content)
    return total
