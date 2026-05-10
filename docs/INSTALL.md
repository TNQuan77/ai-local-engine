# Installation Guide

## Requirements

Only **Python 3.10+** is required. Everything else (Node.js, Ollama, models) is installed automatically.

## One-Command Install

```bash
python scripts/install.py
```

The installer runs 6 steps automatically with no prompts:

| Step | Action |
|---|---|
| 1/6 | Check Python version (≥ 3.10) |
| 2/6 | Install backend Python dependencies |
| 3/6 | Install frontend Node.js dependencies (auto-installs Node.js if missing) |
| 4/6 | Check / install Ollama |
| 5/6 | Scan hardware → pick best model → pull it |
| 6/6 | Create `.env` config file |

When done you'll see a summary box confirming everything is ready.

## Start the App

```bash
python scripts/start.py
```

This starts both servers simultaneously:
- **Backend API**: http://localhost:8000
- **Frontend UI**: http://localhost:5173

Press `Ctrl+C` to stop both.

## What Gets Auto-Installed

### Node.js
- **Windows**: via `winget install OpenJS.NodeJS.LTS`, falls back to MSI download
- **macOS**: via `brew install node`
- **Linux**: via NodeSource setup script

### Ollama
- **Windows**: via `winget install Ollama.Ollama`, falls back to `.exe` download
- **macOS**: via `brew install ollama`
- **Linux**: via `curl -fsSL https://ollama.com/install.sh | sh`

### Model Selection (automatic)
The installer scans your hardware and picks the best model:

| RAM | GPU VRAM | Auto-selected Model |
|---|---|---|
| 4–6 GB | any | `llama3.2:1b` |
| 6–10 GB | 0 | `llama3.2:3b` |
| 10–16 GB | 0 | `qwen2.5:7b` |
| 16+ GB | 0 | `qwen2.5:14b` |
| any | 6–8 GB | `llama3.2:8b` |
| any | 10+ GB | `qwen2.5:14b` |

To check what your system would choose before installing:
```bash
python scripts/scan_system.py
```

## Configuration

The installer creates `.env` automatically. To customize it:

```env
# Local provider (default — no API key needed)
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2:3b
DEFAULT_PROVIDER=local

# API provider (optional — needed only for Claude models)
ANTHROPIC_API_KEY=sk-ant-...
```

## Manual Installation (if needed)

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install

# Pull a model manually
ollama pull llama3.2:3b
```
