"""
Fully automated installer for AI Local Engine.
Run once: python scripts/install.py

No prompts. Installs everything and reports when done.
"""
import platform
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OS = platform.system()  # "Windows" | "Darwin" | "Linux"


def _step(n: int, total: int, msg: str) -> None:
    print(f"\n[{n}/{total}] {msg}...")


def _run(cmd: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, shell=True, **kwargs)


def _run_live(cmd: str, cwd: Path | None = None) -> None:
    """Run command with live output."""
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def _install_ollama() -> None:
    """Install Ollama automatically based on the OS."""
    if OS == "Windows":
        try:
            _run("winget install --id Ollama.Ollama -e --silent --accept-package-agreements --accept-source-agreements")
        except subprocess.CalledProcessError:
            # Fallback: download installer
            print("  winget failed — attempting direct download...")
            _run(
                'powershell -Command "Invoke-WebRequest -Uri https://ollama.com/download/OllamaSetup.exe -OutFile $env:TEMP\\OllamaSetup.exe; Start-Process $env:TEMP\\OllamaSetup.exe /S -Wait"'
            )
    elif OS == "Darwin":
        _run("brew install ollama")
    else:
        _run("curl -fsSL https://ollama.com/install.sh | sh")


def main() -> None:
    print("=" * 50)
    print("  AI Local Engine — Auto Installer")
    print("=" * 50)

    total_steps = 6

    # Step 1: Python version
    _step(1, total_steps, "Checking Python version")
    if sys.version_info < (3, 10):
        sys.exit("ERROR: Python 3.10+ is required.")
    print(f"  Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ✓")

    # Step 2: Backend dependencies
    _step(2, total_steps, "Installing backend dependencies")
    _run_live(f'"{sys.executable}" -m pip install -r "{ROOT / "backend" / "requirements.txt"}"')
    print("  Backend deps ✓")

    # Step 3: Frontend dependencies
    _step(3, total_steps, "Installing frontend dependencies")
    _run_live("npm install", cwd=ROOT / "frontend")
    print("  Frontend deps ✓")

    # Step 4: Ollama
    _step(4, total_steps, "Checking Ollama")
    result = subprocess.run("ollama --version", shell=True, capture_output=True)
    if result.returncode != 0:
        print("  Ollama not found — installing automatically...")
        _install_ollama()

    ver_out = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
    ollama_version = ver_out.stdout.strip() or "Ollama"
    print(f"  {ollama_version} ✓")

    # Step 5: System scan + pull best model
    _step(5, total_steps, "Scanning system hardware and pulling best model")
    sys.path.insert(0, str(ROOT / "scripts"))
    from scan_system import scan, get_best_model, get_recommendations

    info = scan()
    best = get_best_model(info)
    recs = get_recommendations(info)

    print(f"  RAM: {info['ram_gb']} GB | GPU VRAM: {info['gpu']['vram_gb']} GB")
    print(f"  Selected model: {best}")

    if best not in info.get("models_pulled", []):
        print(f"  Pulling {best} (this may take several minutes)...")
        _run_live(f"ollama pull {best}")
    else:
        print(f"  Model {best} already pulled ✓")

    # Step 6: Create .env
    _step(6, total_steps, "Creating configuration file")
    env_path = ROOT / ".env"
    if not env_path.exists():
        example = (ROOT / ".env.example").read_text(encoding="utf-8")
        example = example.replace("DEFAULT_MODEL=llama3.2", f"DEFAULT_MODEL={best}")
        env_path.write_text(example, encoding="utf-8")
        print("  .env created ✓")
    else:
        print("  .env already exists — skipped ✓")

    # Summary
    print(f"""
╔══════════════════════════════════════════════╗
║     AI Local Engine — Installation Done!    ║
╠══════════════════════════════════════════════╣
║  ✓ Backend deps      installed               ║
║  ✓ Frontend deps     installed               ║
║  ✓ {ollama_version:<41}║
║  ✓ Model  {best:<35}║
║  ✓ Config            .env ready              ║
╠══════════════════════════════════════════════╣
║  To start the app:                          ║
║    python scripts/start.py                  ║
╚══════════════════════════════════════════════╝
""")


if __name__ == "__main__":
    main()
