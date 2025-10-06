"""Function-calling scaffolding.

Declares tools to the model in the Gemini ``tools`` format. Executing returned
function calls is left to the caller; this provides the declaration plumbing and
a couple of example tools.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict  # JSON-schema object
    handler: Callable[..., str] | None = None

    def to_declaration(self) -> dict:
        return {"name": self.name, "description": self.description, "parameters": self.parameters}


def to_request(tools: list[Tool]) -> list[dict]:
    """Build the request ``tools`` array from a list of Tools."""
    return [{"functionDeclarations": [t.to_declaration() for t in tools]}]


# A couple of example tools.
CALCULATOR = Tool(
    name="calculate",
    description="Evaluate a basic arithmetic expression and return the result.",
    parameters={
        "type": "object",
        "properties": {"expression": {"type": "string", "description": "e.g. '2 * (3 + 4)'"}},
        "required": ["expression"],
    },
)
