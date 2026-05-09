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


def _refresh_path_windows() -> None:
    """Reload PATH from registry so tools installed after this process started are found."""
    result = subprocess.run(
        ["powershell", "-Command",
         "[System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + "
         "[System.Environment]::GetEnvironmentVariable('Path','User')"],
        capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        os.environ["PATH"] = result.stdout.strip()


if platform.system() == "Windows":
    _refresh_path_windows()


def main() -> None:
    print("Starting AI Local Engine...\n")

    backend_cmd = f"{sys.executable} -m uvicorn main:app --reload --host 0.0.0.0 --port 8000"
    frontend_cmd = "npm run dev"

    print("  [1] Backend  → http://localhost:8000")
    print("  [2] Frontend → http://localhost:5173")
    print("\nPress Ctrl+C to stop both servers.\n")

    backend = subprocess.Popen(
        backend_cmd,
        shell=True,
        cwd=ROOT / "backend",
    )

    time.sleep(1)  # give backend a moment before starting frontend

    frontend = subprocess.Popen(
        frontend_cmd,
        shell=True,
        cwd=ROOT / "frontend",
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
