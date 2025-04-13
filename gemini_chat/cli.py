"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys
from typing import TextIO

from . import __version__
from .client import GeminiClient
from .config import Config
from .errors import GeminiError
from .models import Conversation
from .repl import Repl


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gemini", description="Terminal chat client for the Google Gemini API.")
    p.add_argument("prompt", nargs="*", help="one-shot prompt; omit for interactive mode")
    p.add_argument("-m", "--model", help="model name (e.g. gemini-1.5-pro)")
    p.add_argument("-s", "--system", help="system instruction / persona")
    p.add_argument("-t", "--temperature", type=float, help="sampling temperature")
    p.add_argument("--version", action="version", version=f"gemini-chat {__version__}")
    return p


def run_once(config: Config, prompt: str, client: GeminiClient | None = None, out: TextIO = sys.stdout) -> int:
    """Non-interactive: send one prompt, stream the reply, exit."""
    client = client or GeminiClient(config)
    conv = Conversation(system_instruction=config.system_instruction)
    conv.add_user(prompt)
    try:
        if config.stream and hasattr(client, "stream"):
            for delta in client.stream(conv):
                out.write(delta)
                out.flush()
            out.write("\n")
        else:
            out.write(client.generate(conv).text + "\n")
    except GeminiError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = Config.load()
    if args.model:
        config.model = args.model
    if args.system:
        config.system_instruction = args.system
    if args.temperature is not None:
        config.temperature = args.temperature

    # Assemble a one-shot prompt from positional args and/or piped stdin.
    pieces = list(args.prompt)
    if not sys.stdin.isatty():
        piped = sys.stdin.read().strip()
        if piped:
            pieces.append(piped)
    prompt = " ".join(pieces).strip()

    try:
        if prompt:
            return run_once(config, prompt)
        Repl(config).run()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0
