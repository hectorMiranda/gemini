# gemini

A fast, dependency-free **terminal chat client for the Google Gemini API**.

Talk to Gemini from your shell: streaming replies, saved conversations, slash
commands, model switching, personas, file attachments and a readable
markdown-in-the-terminal renderer — all with **zero third-party runtime
dependencies** (it speaks HTTP over the Python standard library).

```
$ gemini
gemini › explain a kalman filter in one paragraph
… (streams the answer) …
gemini › /save notes
saved session 'notes'
gemini › /model gemini-1.5-pro
gemini › /exit
```

## Install

```bash
pip install -e .
export GEMINI_API_KEY=your_key_here   # from https://aistudio.google.com/apikey
gemini
```

## One-shot mode

```bash
gemini "summarize this file" < notes.txt
echo "translate to spanish: good morning" | gemini
```

## Why

The official SDK is great, but sometimes you just want a snappy REPL in your
terminal with history and sessions, nothing to install, and no surprises. That's
this.

## Commands

| Command | Description |
| --- | --- |
| `/new` | start a fresh conversation |
| `/system <text>` | set the system instruction / persona |
| `/model [name]` | show or switch the model |
| `/temp <0-2>` · `/max <n>` | generation settings |
| `/attach <path>` | attach a text or image file to the next message |
| `/save <name>` · `/load <name>` · `/sessions` | manage saved conversations |
| `/export <file.md>` | export the conversation to Markdown |
| `/usage` | rough token estimate |
| `/help` · `/exit` | help / quit |

## Configuration

Settings come from `~/.config/gemini-chat/config.toml`, overridden by environment
variables:

```toml
model = "gemini-1.5-flash"
temperature = 0.7
retries = 2
```

| Env var | Meaning |
| --- | --- |
| `GEMINI_API_KEY` | API key (required) |
| `GEMINI_MODEL` | default model |
| `GEMINI_SYSTEM` | default system instruction |

Requires Python 3.11+.
