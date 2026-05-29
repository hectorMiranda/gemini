# Changelog

## 1.0.0 — 2026-05-28

First stable release. A complete, dependency-free terminal chat client for the
Google Gemini API.

### Core
- HTTP client over the standard library (`urllib`) with an injectable transport,
  non-streaming and **streaming** (SSE) completions, and **retry with backoff**
  on transient failures.
- Conversation model with multimodal parts, configuration from
  `config.toml` + environment, and a token estimator.

### Terminal UX
- Interactive REPL with slash commands: `/new`, `/system`, `/persona`, `/model`,
  `/temp`, `/max`, `/attach`, `/save`, `/load`, `/sessions`, `/export`,
  `/usage`, `/retry`, `/help`, `/exit`.
- Live streaming output, ANSI Markdown rendering, color themes, persona presets.
- One-shot and piped (stdin) modes for scripting.

### Data
- JSON session save/recall; export to **Markdown / JSON / HTML**.
- Function-calling scaffolding (tool declarations).

### Project
- 43 tests (`unittest`), GitHub Actions CI on Python 3.11–3.13, `py.typed`,
  examples and a contributing guide.

### Earlier milestones
- 0.1.0 (2024-08) — scaffolding, config, models, client, sessions, basic REPL.
