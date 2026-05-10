# AI Local Engine

A full-stack AI coding agent that works like Claude Code — reads, edits, and creates files in your project. Runs locally with Ollama or via Claude API.

**[English](README.md)** | [Tiếng Việt](docs/README.vi.md)

## Features

- **Two providers**: Local (Ollama, fully offline) and API (Claude Opus/Sonnet)
- **Coding tools**: Read, Write, Edit files — Run shell commands — Search files
- **Slash skills**: `/review`, `/refactor`, `/test`, `/fix`, `/docs`, `/commit`, `/lint`
- **Extended tools**: Web search, run tests, git operations, linting
- **System scanner**: Auto-detects your hardware and pulls the best model
- **One-command install**: `python scripts/install.py` — installs Node.js, Ollama, and the model automatically

## Requirements

Only **Python 3.10+**. Everything else is installed automatically.

## Quick Start

```bash
git clone https://github.com/TNQuan77/ai-local-engine.git
cd ai-local-engine
python scripts/install.py   # auto-installs all deps + pulls best model
python scripts/start.py     # starts backend + frontend
```

Open **http://localhost:5173**

## Usage

1. Enter your project directory path in the workspace bar
2. Select **Local** (Ollama) or **API** (Claude) provider
3. Chat with the agent or use slash commands:

```
/review                    → review code changes
/refactor src/main.py      → refactor a file
/test src/utils.py         → generate unit tests
/fix                       → find and fix bugs
/docs src/api.py           → generate documentation
/commit                    → create a git commit
/lint                      → lint and fix style issues
```

## Documentation

- [Installation Guide](docs/INSTALL.md) | [Hướng dẫn cài đặt](docs/INSTALL.vi.md)
- [Architecture](docs/README.md) | [Kiến trúc hệ thống](docs/README.vi.md)
