# Installation Guide

## Requirements

- Python 3.10+
- Node.js 18+
- Ollama (auto-installed by the installer)
- (Optional) Anthropic API key for Claude models

## One-Command Install

```bash
python scripts/install.py
```

This will automatically:
1. Check Python version
2. Install backend Python dependencies
3. Install frontend Node.js dependencies
4. Install Ollama if not already installed
5. Scan your hardware and pull the best compatible model
6. Create `.env` with correct defaults

## Start the App

```bash
python scripts/start.py
```

- Backend: http://localhost:8000
- Frontend: http://localhost:5173

## Manual Installation

### Backend
```bash
cd backend
pip install -r requirements.txt
```

### Frontend
```bash
cd frontend
npm install
```

### Ollama
Download from https://ollama.com/download, then pull a model:
```bash
ollama pull llama3.2        # lightweight
ollama pull qwen2.5:7b      # balanced
ollama pull qwen2.5:14b     # high quality (needs 16GB+ RAM)
```

## Configuration

Copy `.env.example` to `.env` and edit:

```env
# Local provider (default)
OLLAMA_BASE_URL=http://localhost:11434
DEFAULT_MODEL=llama3.2
DEFAULT_PROVIDER=local

# API provider (optional)
ANTHROPIC_API_KEY=sk-ant-...
```

## Recommended Models by Hardware

| RAM | GPU VRAM | Recommended |
|---|---|---|
| 4–6 GB | any | `llama3.2:1b` |
| 6–10 GB | 0 | `llama3.2:3b` |
| 10–16 GB | 0 | `qwen2.5:7b` |
| 16+ GB | 0 | `qwen2.5:14b` |
| any | 6–8 GB | `llama3.2:8b` |
| any | 10+ GB | `qwen2.5:14b` |

Run the scanner to get a personalized recommendation:
```bash
python scripts/scan_system.py
```
