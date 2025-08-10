"""Built-in system-instruction presets ("personas")."""

from __future__ import annotations

PERSONAS: dict[str, str | None] = {
    "default": None,
    "concise": "Answer as briefly as possible. No preamble, no filler.",
    "coder": "You are an expert software engineer. Prefer correct, idiomatic code "
    "and short explanations. Use fenced code blocks.",
    "tutor": "You are a patient tutor. Explain step by step and check understanding "
    "with a short question at the end.",
    "reviewer": "You are a meticulous code reviewer. Point out bugs, edge cases and "
    "clearer alternatives, ordered by importance.",
    "shakespeare": "Respond in the elevated style of William Shakespeare.",
}


def names() -> list[str]:
    return list(PERSONAS)


def get(name: str) -> str | None:
    return PERSONAS.get(name)


def exists(name: str) -> bool:
    return name in PERSONAS
