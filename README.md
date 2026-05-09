# AI Local Engine

A full-stack AI coding agent that runs locally using Ollama or Claude API.
Works like Claude Code — reads, edits, and creates files in your project.

**[English](README.md)** | [Tiếng Việt](docs/README.vi.md)

## Features

- **Two providers**: Local (Ollama, offline) and API (Claude Opus/Sonnet)
- **Coding tools**: Read, Write, Edit files — Run shell commands — Search files
- **Slash skills**: `/review`, `/refactor`, `/test`, `/fix`, `/docs`, `/commit`, `/lint`
- **Extended tools**: Web search, run tests, git operations, linting
- **System scanner**: Auto-detects your hardware and recommends the best model
- **One-command install**: `python scripts/install.py` sets up everything

## Quick Start

```bash
git clone <repo>
cd ai-local-engine
python scripts/install.py   # installs all deps + pulls best model
python scripts/start.py     # starts backend + frontend
```

Open http://localhost:5173

## Documentation

- [Installation Guide](docs/INSTALL.md) | [Hướng dẫn cài đặt](docs/INSTALL.vi.md)
- [Architecture](docs/README.md) | [Kiến trúc](docs/README.vi.md)
