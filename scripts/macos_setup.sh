#!/usr/bin/env bash
# One-shot macOS setup: installs everything and starts the app.
# Usage: bash scripts/macos_setup.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"

echo "================================================"
echo "  AI Local Engine — macOS Setup"
echo "================================================"

# ── 1. Require Homebrew ───────────────────────────────────────────────────────
if ! command -v brew &>/dev/null; then
  echo "ERROR: Homebrew is required. Install it from https://brew.sh then re-run."
  exit 1
fi

# ── 2. Resolve Python 3.10+ (prefer Homebrew) ────────────────────────────────
PYTHON=""
for candidate in \
  "$(brew --prefix)/bin/python3" \
  "$(brew --prefix)/bin/python3.14" \
  "$(brew --prefix)/bin/python3.13" \
  "$(brew --prefix)/bin/python3.12" \
  "$(brew --prefix)/bin/python3.11" \
  "$(brew --prefix)/bin/python3.10" \
  "/usr/bin/python3"; do
  if [[ -x "$candidate" ]]; then
    ver=$("$candidate" -c "import sys; print(sys.version_info >= (3,10))" 2>/dev/null || echo False)
    if [[ "$ver" == "True" ]]; then
      PYTHON="$candidate"
      break
    fi
  fi
done

if [[ -z "$PYTHON" ]]; then
  echo "Python 3.10+ not found — installing via Homebrew..."
  brew install python3
  PYTHON="$(brew --prefix)/bin/python3"
fi

echo "Using Python: $PYTHON ($("$PYTHON" --version))"

# ── 3. Run the installer ──────────────────────────────────────────────────────
"$PYTHON" "$ROOT/scripts/install.py"

# ── 4. Start the app ─────────────────────────────────────────────────────────
echo ""
echo "Installation complete. Starting the app..."
echo "Open http://localhost:5173 in your browser."
echo ""
"$PYTHON" "$ROOT/scripts/start.py"
