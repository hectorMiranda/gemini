"""Command-line entry point."""

from __future__ import annotations

import argparse
import sys

from . import __version__
from .config import Config
from .repl import Repl


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog="gemini", description="Terminal chat client for the Google Gemini API.")
    p.add_argument("-m", "--model", help="model name (e.g. gemini-1.5-pro)")
    p.add_argument("-s", "--system", help="system instruction / persona")
    p.add_argument("-t", "--temperature", type=float, help="sampling temperature")
    p.add_argument("--version", action="version", version=f"gemini-chat {__version__}")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    config = Config.load()
    if args.model:
        config.model = args.model
    if args.system:
        config.system_instruction = args.system
    if args.temperature is not None:
        config.temperature = args.temperature

    try:
        Repl(config).run()
    except RuntimeError as e:
        print(f"error: {e}", file=sys.stderr)
        return 1
    return 0
