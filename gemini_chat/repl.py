"""Interactive read-eval-print loop for chatting with Gemini."""

from __future__ import annotations

import sys
from typing import Callable, TextIO

from .client import GeminiClient
from .config import Config
from .errors import GeminiError
from .models import Conversation
from . import session

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
        self.running = True
        self.commands = {
            "help": self.cmd_help,
            "exit": self.cmd_exit,
            "quit": self.cmd_exit,
            "new": self.cmd_new,
            "clear": self.cmd_new,
            "system": self.cmd_system,
            "model": self.cmd_model,
            "save": self.cmd_save,
            "load": self.cmd_load,
            "sessions": self.cmd_sessions,
        }

    def run(self) -> None:
        self._print(BANNER)
        while self.running:
            try:
                line = self._read(PROMPT).strip()
            except (EOFError, KeyboardInterrupt):
                self._print("")
                break
            if not line:
                continue
            self.handle(line)

    def handle(self, line: str) -> None:
        if line.startswith("/"):
            self.command(line[1:])
        else:
            self.send(line)

    def command(self, raw: str) -> None:
        name, _, arg = raw.partition(" ")
        handler = self.commands.get(name.lower())
        if handler is None:
            self._print(f"unknown command: /{name} (try /help)")
            return
        handler(arg.strip())

    def send(self, text: str) -> None:
        self.conversation.add_user(text)
        try:
            result = self.client.generate(self.conversation)
        except GeminiError as e:
            self._print(f"error: {e}")
            self.conversation.messages.pop()
            return
        self.conversation.add_model(result.text)
        self._print(result.text)

    # --- commands ----------------------------------------------------------
    def cmd_help(self, _arg: str) -> None:
        self._print(
            "commands:\n"
            "  /new            start a fresh conversation\n"
            "  /system <text>  set the system instruction\n"
            "  /model <name>   switch model\n"
            "  /help           this help\n"
            "  /exit           quit"
        )

    def cmd_exit(self, _arg: str) -> None:
        self.running = False

    def cmd_new(self, _arg: str) -> None:
        self.conversation.clear()
        self._print("started a new conversation")

    def cmd_system(self, arg: str) -> None:
        self.conversation.system_instruction = arg or None
        self._print(f"system instruction {'set' if arg else 'cleared'}")

    def cmd_model(self, arg: str) -> None:
        if not arg:
            self._print(f"current model: {self.config.model}")
            return
        self.config.model = arg
        self._print(f"model set to {arg}")

    def cmd_save(self, arg: str) -> None:
        if not arg:
            self._print("usage: /save <name>")
            return
        try:
            session.save_session(arg, self.conversation)
            self._print(f"saved session '{arg}'")
        except (OSError, ValueError) as e:
            self._print(f"error: {e}")

    def cmd_load(self, arg: str) -> None:
        if not arg:
            self._print("usage: /load <name>")
            return
        try:
            self.conversation = session.load_session(arg)
            self._print(f"loaded session '{arg}' ({len(self.conversation.messages)} messages)")
        except (OSError, ValueError) as e:
            self._print(f"error: {e}")

    def cmd_sessions(self, _arg: str) -> None:
        names = session.list_sessions()
        self._print("\n".join(names) if names else "no saved sessions")

    def _print(self, text: str) -> None:
        print(text, file=self.out)
