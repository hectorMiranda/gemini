"""Interactive read-eval-print loop for chatting with Gemini."""

from __future__ import annotations

import mimetypes
import sys
from pathlib import Path
from typing import Callable, TextIO

from .client import GeminiClient
from .config import Config
from .errors import GeminiError
from .models import Conversation, Part, Role
from . import export, personas, session, tokens

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
        self.pending: list[Part] = []
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
            "attach": self.cmd_attach,
            "export": self.cmd_export,
            "usage": self.cmd_usage,
            "temp": self.cmd_temp,
            "max": self.cmd_max,
            "persona": self.cmd_persona,
            "retry": self.cmd_retry,
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
        parts = [Part(text=text), *self.pending]
        self.conversation.add_user(text, parts=parts)
        self.pending = []
        self._complete(drop_on_error=True)

    def _complete(self, drop_on_error: bool = False) -> None:
        """Generate a model reply for the current conversation (which must end with a user turn)."""
        try:
            if self.config.stream and hasattr(self.client, "stream"):
                reply = self._stream_reply()
            else:
                reply = self.client.generate(self.conversation).text
                self._print(reply)
        except GeminiError as e:
            self._print(f"error: {e}")
            if drop_on_error and self.conversation.messages:
                self.conversation.messages.pop()
            return
        self.conversation.add_model(reply)

    def _stream_reply(self) -> str:
        chunks: list[str] = []
        for delta in self.client.stream(self.conversation):
            chunks.append(delta)
            self.out.write(delta)
            self.out.flush()
        self.out.write("\n")
        return "".join(chunks)

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

    def cmd_attach(self, arg: str) -> None:
        if not arg:
            self._print("usage: /attach <path>")
            return
        path = Path(arg).expanduser()
        if not path.exists():
            self._print(f"error: no such file: {path}")
            return
        mime, _ = mimetypes.guess_type(str(path))
        mime = mime or "application/octet-stream"
        if mime.startswith("text/") or mime in ("application/json", "application/xml"):
            self.pending.append(Part(text=f"[file {path.name}]\n{path.read_text(errors='replace')}"))
        else:
            self.pending.append(Part(mime_type=mime, data=path.read_bytes()))
        self._print(f"attached {path.name} ({mime}); will send with your next message")

    def cmd_export(self, arg: str) -> None:
        if not arg:
            self._print("usage: /export <path.md>")
            return
        try:
            Path(arg).expanduser().write_text(export.to_markdown(self.conversation), encoding="utf-8")
            self._print(f"exported to {arg}")
        except OSError as e:
            self._print(f"error: {e}")

    def cmd_usage(self, _arg: str) -> None:
        approx = tokens.conversation_tokens(self.conversation)
        self._print(f"{len(self.conversation.messages)} messages, ~{approx} tokens (estimate)")

    def cmd_persona(self, arg: str) -> None:
        if not arg:
            self._print("personas: " + ", ".join(personas.names()))
            return
        if not personas.exists(arg):
            self._print(f"unknown persona '{arg}' (try: {', '.join(personas.names())})")
            return
        self.conversation.system_instruction = personas.get(arg)
        self._print(f"persona set to '{arg}'")

    def cmd_retry(self, _arg: str) -> None:
        if self.conversation.messages and self.conversation.messages[-1].role == Role.MODEL:
            self.conversation.messages.pop()
        if not self.conversation.messages or self.conversation.messages[-1].role != Role.USER:
            self._print("nothing to retry")
            return
        self._complete()

    def cmd_temp(self, arg: str) -> None:
        if not arg:
            self._print(f"temperature: {self.config.temperature}")
            return
        try:
            self.config.temperature = max(0.0, min(2.0, float(arg)))
            self._print(f"temperature set to {self.config.temperature}")
        except ValueError:
            self._print("usage: /temp <0.0-2.0>")

    def cmd_max(self, arg: str) -> None:
        if not arg:
            self._print(f"max output tokens: {self.config.max_output_tokens or 'default'}")
            return
        try:
            self.config.max_output_tokens = max(1, int(arg))
            self._print(f"max output tokens set to {self.config.max_output_tokens}")
        except ValueError:
            self._print("usage: /max <int>")

    def _print(self, text: str) -> None:
        print(text, file=self.out)
