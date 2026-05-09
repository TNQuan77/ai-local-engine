"""
Fully automated installer for AI Local Engine.
Run once: python scripts/install.py

No prompts. Installs everything and reports when done.
"""
import platform
import subprocess
import sys
from pathlib import Path

# Force UTF-8 output on Windows terminals
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parent.parent
OS = platform.system()  # "Windows" | "Darwin" | "Linux"


def _step(n: int, total: int, msg: str) -> None:
    print(f"\n[{n}/{total}] {msg}...")


def _run(cmd: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, shell=True, **kwargs)


def _run_live(cmd: str, cwd: Path | None = None) -> None:
    """Run command with live output."""
    subprocess.run(cmd, shell=True, check=True, cwd=cwd)


def _refresh_path_windows() -> None:
    """Reload PATH from registry so newly installed tools are found."""
    import os as _os
    result = subprocess.run(
        ["powershell", "-Command",
         "[System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + "
         "[System.Environment]::GetEnvironmentVariable('Path','User')"],
        capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        _os.environ["PATH"] = result.stdout.strip()


def _install_nodejs() -> None:
    """Install Node.js automatically based on the OS."""
    print("  Node.js not found — installing automatically...")
    if OS == "Windows":
        # winget exit 0 = installed, 0x89B40C4B = already installed (both are OK)
        result = subprocess.run(
            "winget install --id OpenJS.NodeJS.LTS -e --silent "
            "--accept-package-agreements --accept-source-agreements",
            shell=True,
        )
        _refresh_path_windows()
        # Verify npm is now available
        if subprocess.run("npm --version", shell=True, capture_output=True).returncode != 0:
            # Fallback: download MSI via urllib (no PowerShell quoting issues)
            print("  winget did not make npm available — downloading MSI directly...")
            import urllib.request, tempfile, os as _os
            msi_path = _os.path.join(tempfile.gettempdir(), "nodejs_lts.msi")
            urllib.request.urlretrieve(
                "https://nodejs.org/dist/lts/node-v20.19.0-x64.msi", msi_path
            )
            subprocess.run(
                f'msiexec /i "{msi_path}" /quiet /norestart',
                shell=True, check=True,
            )
            _refresh_path_windows()
    elif OS == "Darwin":
        _run("brew install node")
    else:
        _run("curl -fsSL https://deb.nodesource.com/setup_lts.x | bash -")
        _run("apt-get install -y nodejs")


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
    if subprocess.run("npm --version", shell=True, capture_output=True).returncode != 0:
        _install_nodejs()
        if OS == "Windows":
            _refresh_path_windows()
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
    node_ver = subprocess.run("node --version", shell=True, capture_output=True, text=True).stdout.strip()
    print(f"""
╔══════════════════════════════════════════════╗
║     AI Local Engine — Installation Done!    ║
╠══════════════════════════════════════════════╣
║  ✓ Backend deps      installed               ║
║  ✓ Frontend deps     installed               ║
║  ✓ Node.js {node_ver:<34}║
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
