# Contributing

Thanks for your interest! gemini-chat is intentionally small and dependency-free.

## Setup

```bash
pip install -e ".[dev]"
python -m unittest discover -s tests -t .
```

## Guidelines

- **No third-party runtime dependencies.** The client speaks HTTP over the
  standard library; keep it that way. Dev/test tools are fine.
- Add a test for any behavior change (we use `unittest`).
- Keep the transport injectable so tests never hit the network.
- Run `mypy gemini_chat` before opening a PR.

## Layout

| Module | Responsibility |
| --- | --- |
| `config` | settings (file + env) |
| `models` | conversation data + wire format |
| `transport` | HTTP over urllib (mockable) |
| `client` | Gemini API calls, retries |
| `repl` / `cli` | terminal UX |
| `render` / `colors` | terminal formatting |
| `session` / `export` | persistence and export |
