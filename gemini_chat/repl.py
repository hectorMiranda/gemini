"""Interactive read-eval-print loop for chatting with Gemini."""

from __future__ import annotations

import sys
from typing import Callable, TextIO

from .client import GeminiClient
from .config import Config
from .errors import GeminiError
from .models import Conversation

PROMPT = "gemini › "
BANNER = "gemini-chat — type a message, or /help for commands. Ctrl-D to quit."


class Repl:
    def __init__(
        self,
        config: Config,
        client: GeminiClient | None = None,
        conversation: Conversation | None = None,
        out: TextIO = sys.stdout,
        read: Callable[[str], str] = input,
    ):
        self.config = config
        self.client = client or GeminiClient(config)
        self.conversation = conversation or Conversation(system_instruction=config.system_instruction)
        self.out = out
        self._read = read

    def run(self) -> None:
        print(BANNER, file=self.out)
        while True:
            try:
                line = self._read(PROMPT).strip()
            except (EOFError, KeyboardInterrupt):
                print(file=self.out)
                break
            if not line:
                continue
            self.handle(line)

    def handle(self, line: str) -> None:
        self.send(line)

    def send(self, text: str) -> None:
        self.conversation.add_user(text)
        try:
            result = self.client.generate(self.conversation)
        except GeminiError as e:
            print(f"error: {e}", file=self.out)
            # Drop the unanswered user turn so the history stays consistent.
            self.conversation.messages.pop()
            return
        self.conversation.add_model(result.text)
        print(result.text, file=self.out)
