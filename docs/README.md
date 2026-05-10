# AI Local Engine — Architecture

## Overview

AI Local Engine is a full-stack coding agent with two providers:

| Provider | Engine | Requirements | Use Case |
|---|---|---|---|
| **Local** | Ollama | None (offline) | Privacy, no cost |
| **API** | Claude Agent SDK | `ANTHROPIC_API_KEY` | Higher quality |

## System Architecture

```
┌─────────────────────────────────────────────┐
│              Frontend (React)                │
│  ProviderToggle → ModelSelector              │
│  WorkspaceBar → ChatWindow → InputBar        │
│  Slash commands: /review /refactor /test ... │
└──────────────┬──────────────────────────────┘
               │ HTTP SSE  /api/chat
┌──────────────▼──────────────────────────────┐
│              Backend (FastAPI)               │
│  ┌──────────────┐  ┌──────────────────────┐ │
│  │ OllamaAgent  │  │   ClaudeAgent        │ │
│  │ tool loop    │  │   claude-agent-sdk   │ │
│  └──────┬───────┘  └──────────────────────┘ │
│         │ tools                              │
│  ┌──────▼────────────────────────────┐      │
│  │ file_tools + extended_tools       │      │
│  │ read/write/create/edit/bash/glob/grep    │      │
│  │ web_search/run_tests/run_code/git/lint     │      │
│  └───────────────────────────────────┘      │
└─────────────────────────────────────────────┘
               │
┌──────────────▼──────────────────────────────┐
│         User's Project Directory             │
│  Any folder on the filesystem               │
└─────────────────────────────────────────────┘
```

## SSE Event Protocol

```
POST /api/chat → text/event-stream

data: {"type": "text",        "content": "Reading file..."}
data: {"type": "tool_call",   "name": "read_file", "input": {"path": "main.py"}}
data: {"type": "tool_result", "content": "def main():\n    ..."}
data: {"type": "done"}
```

## Tool Inventory

### File Tools (both providers)
| Tool | Description |
|---|---|
| `read_file(path)` | Read file contents |
| `write_file(path, content)` | Create / overwrite file |
| `create_file(path, content)` | Create a new file with optional content |
| `create_directory(path)` | Create a directory and parents if needed |
| `edit_file(path, old_string, new_string)` | Surgical text replacement |
| `run_bash(command)` | Execute shell command in working dir |
| `list_files(pattern)` | Glob file search |
| `search_in_files(text, pattern)` | Grep-style search |

### Extended Tools
| Tool | Description |
|---|---|
| `web_search(query)` | DuckDuckGo search |
| `http_request(url, method, body)` | HTTP API call |
| `run_tests(path, framework)` | pytest / jest |
| `run_code(command, expect_errors)` | Execute a command and optionally handle errors |
| `git_status()` | git status + diff |
| `git_commit(message)` | Stage all + commit |
| `lint_file(path)` | flake8 / eslint |

## Slash Skills

| Command | Action |
|---|---|
| `/review` | Code review (git diff + analysis) |
| `/refactor <file>` | Refactor for quality |
| `/test <file>` | Generate unit tests |
| `/explain <file>` | Explain code in detail |
| `/fix` | Find and fix bugs |
| `/docs <file>` | Generate documentation |
| `/commit` | Create git commit |
| `/lint` | Lint and fix style issues |
