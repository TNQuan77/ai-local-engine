"""
Start both backend and frontend servers simultaneously.
Run: python scripts/start.py
"""
import os
import platform
import subprocess
import sys
import time
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OS = platform.system()
VENV = ROOT / ".venv"


def _refresh_path_windows() -> None:
    result = subprocess.run(
        ["powershell", "-Command",
         "[System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + "
         "[System.Environment]::GetEnvironmentVariable('Path','User')"],
        capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        os.environ["PATH"] = result.stdout.strip()


if OS == "Windows":
    _refresh_path_windows()


def _venv_python() -> str:
    """Return venv Python if available, otherwise fall back to current interpreter."""
    candidate = VENV / ("Scripts/python.exe" if OS == "Windows" else "bin/python")
    return str(candidate) if candidate.exists() else sys.executable


def _npm() -> str:
    """Return npm executable, checking Homebrew paths on macOS."""
    for p in ["/opt/homebrew/bin/npm", "/usr/local/bin/npm"]:
        if Path(p).exists():
            return p
    return "npm"


def _load_env() -> dict:
    """Read key=value pairs from .env and return as dict."""
    env_file = ROOT / ".env"
    result = {}
    if not env_file.exists():
        return result
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, _, v = line.partition("=")
            result[k.strip()] = v.strip()
    return result


def _ensure_ollama_running(env_vars: dict) -> None:
    """Start ollama serve in background if not already listening."""
    check = subprocess.run(
        "curl -s http://localhost:11434/api/tags",
        shell=True, capture_output=True,
    )
    if check.returncode == 0:
        return

    print("  Ollama not running — starting it...")
    env = os.environ.copy()
    env.update(env_vars)
    ollama_bin = "/opt/homebrew/bin/ollama" if OS == "Darwin" else "ollama"
    subprocess.Popen(
        f'"{ollama_bin}" serve',
        shell=True, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    for _ in range(10):
        time.sleep(1)
        if subprocess.run("curl -s http://localhost:11434/api/tags", shell=True, capture_output=True).returncode == 0:
            print("  Ollama started ✓")
            return
    print("  WARNING: Ollama may not be ready yet — continuing anyway")


def main() -> None:
    cfg = _load_env()
    provider = cfg.get("DEFAULT_PROVIDER", "local")

    # Build subprocess environment: inherit current env + .env overrides
    child_env = os.environ.copy()
    child_env.update(cfg)

    print("Starting AI Local Engine...\n")
    print(f"  Provider: {provider}")

    # Start Ollama automatically when using local provider
    if provider == "local":
        _ensure_ollama_running(child_env)

    python = _venv_python()
    npm = _npm()

    backend_cmd = f'"{python}" -m uvicorn main:app --reload --host 0.0.0.0 --port 8000'
    frontend_cmd = f'"{npm}" run dev'

    print("  [1] Backend  → http://localhost:8000")
    print("  [2] Frontend → http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers.\n")

    backend = subprocess.Popen(
        backend_cmd,
        shell=True,
        cwd=ROOT / "backend",
        env=child_env,
    )

    time.sleep(2)  # give backend a moment before starting frontend

    frontend = subprocess.Popen(
        frontend_cmd,
        shell=True,
        cwd=ROOT / "frontend",
        env=child_env,
    )

    try:
        backend.wait()
        frontend.wait()
    except KeyboardInterrupt:
        print("\nStopping servers...")
        backend.terminate()
        frontend.terminate()
        backend.wait()
        frontend.wait()
        print("Stopped.")


if __name__ == "__main__":
    main()
