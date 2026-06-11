"""
Fully automated installer for AI Local Engine.
Run once: python scripts/install.py

No prompts. Installs everything and reports when done.
"""
import os
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
VENV = ROOT / ".venv"


def _step(n: int, total: int, msg: str) -> None:
    print(f"\n[{n}/{total}] {msg}...")


def _run(cmd: str, **kwargs) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, check=True, shell=True, **kwargs)


def _run_live(cmd: str, cwd: Path | None = None, extra_env: dict | None = None) -> None:
    """Run command with live output."""
    env = os.environ.copy()
    if extra_env:
        env.update(extra_env)
    subprocess.run(cmd, shell=True, check=True, cwd=cwd, env=env)


def _venv_python() -> str:
    """Return the venv Python executable path."""
    if OS == "Windows":
        return str(VENV / "Scripts" / "python.exe")
    return str(VENV / "bin" / "python")


def _ensure_venv() -> None:
    """Create .venv using current interpreter if it doesn't exist."""
    if VENV.exists():
        print("  .venv already exists ✓")
        return
    print("  Creating virtual environment (.venv)...")
    subprocess.run([sys.executable, "-m", "venv", str(VENV)], check=True)
    print("  .venv created ✓")


def _npm() -> str:
    """Return the npm executable, checking Homebrew paths on macOS."""
    for candidate in ["/opt/homebrew/bin/npm", "/usr/local/bin/npm"]:
        if Path(candidate).exists():
            return candidate
    return "npm"


def _refresh_path_windows() -> None:
    """Reload PATH from registry so newly installed tools are found."""
    result = subprocess.run(
        ["powershell", "-Command",
         "[System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + "
         "[System.Environment]::GetEnvironmentVariable('Path','User')"],
        capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        os.environ["PATH"] = result.stdout.strip()


def _find_external_ssd() -> Path | None:
    """Return the first writable external volume on macOS, or None."""
    if OS != "Darwin":
        return None
    skip = {"Macintosh HD", "Macintosh HD - Data"}
    try:
        for vol in sorted(Path("/Volumes").iterdir()):
            if vol.name in skip or vol.name.startswith("."):
                continue
            if os.access(vol, os.W_OK):
                return vol
    except PermissionError:
        pass
    return None


def _install_nodejs() -> None:
    """Install Node.js automatically based on the OS."""
    print("  Node.js not found — installing automatically...")
    if OS == "Windows":
        result = subprocess.run(
            "winget install --id OpenJS.NodeJS.LTS -e --silent "
            "--accept-package-agreements --accept-source-agreements",
            shell=True,
        )
        _refresh_path_windows()
        if subprocess.run("npm --version", shell=True, capture_output=True).returncode != 0:
            print("  winget did not make npm available — downloading MSI directly...")
            import urllib.request, tempfile
            msi_path = os.path.join(tempfile.gettempdir(), "nodejs_lts.msi")
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


def _install_ollama_macos(ssd: Path | None) -> Path:
    """
    Install Ollama.app to external SSD if available, otherwise /Applications.
    Returns the ollama CLI path.
    """
    app_dest = (ssd if ssd else Path("/Applications")) / "Ollama.app"
    cli = app_dest / "Contents" / "Resources" / "ollama"

    if cli.exists():
        print(f"  Ollama.app already at {app_dest} ✓")
    else:
        zip_path = Path("/tmp/Ollama-darwin.zip")
        print(f"  Downloading Ollama.app to {app_dest.parent} ...")
        _run(f'curl -L https://ollama.com/download/Ollama-darwin.zip -o "{zip_path}"')
        _run(f'unzip -o "{zip_path}" -d "{app_dest.parent}"')
        zip_path.unlink(missing_ok=True)

    # Symlink CLI into Homebrew bin so `ollama` works in PATH
    link = Path("/opt/homebrew/bin/ollama")
    if not link.exists() or link.resolve() != cli:
        link.unlink(missing_ok=True)
        link.symlink_to(cli)
        print(f"  Symlinked ollama → {link}")

    return cli


def _install_ollama(ssd: Path | None = None) -> None:
    """Install Ollama based on OS."""
    if OS == "Windows":
        try:
            _run("winget install --id Ollama.Ollama -e --silent --accept-package-agreements --accept-source-agreements")
        except subprocess.CalledProcessError:
            print("  winget failed — attempting direct download...")
            _run(
                'powershell -Command "Invoke-WebRequest -Uri https://ollama.com/download/OllamaSetup.exe '
                '-OutFile $env:TEMP\\OllamaSetup.exe; Start-Process $env:TEMP\\OllamaSetup.exe /S -Wait"'
            )
    elif OS == "Darwin":
        _install_ollama_macos(ssd)
    else:
        _run("curl -fsSL https://ollama.com/install.sh | sh")


def _start_ollama_server(models_dir: str | None) -> None:
    """Start ollama serve in the background if not already running."""
    if subprocess.run("curl -s http://localhost:11434/api/tags", shell=True, capture_output=True).returncode == 0:
        print("  Ollama server already running ✓")
        return
    env = os.environ.copy()
    if models_dir:
        env["OLLAMA_MODELS"] = models_dir
    if OS == "Darwin":
        ollama_bin = "/opt/homebrew/bin/ollama"
    else:
        ollama_bin = "ollama"
    subprocess.Popen(
        f'"{ollama_bin}" serve',
        shell=True, env=env,
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    import time
    for _ in range(10):
        time.sleep(1)
        if subprocess.run("curl -s http://localhost:11434/api/tags", shell=True, capture_output=True).returncode == 0:
            print("  Ollama server started ✓")
            return
    print("  WARNING: Ollama server may not be ready yet — continuing anyway")


def main() -> None:
    print("=" * 50)
    print("  AI Local Engine — Auto Installer")
    print("=" * 50)

    total_steps = 7

    # Step 1: Python version
    _step(1, total_steps, "Checking Python version")
    if sys.version_info < (3, 10):
        sys.exit("ERROR: Python 3.10+ is required. On macOS run: brew install python3")
    print(f"  Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro} ✓")

    # Step 2: Virtual environment (required on macOS with Homebrew Python)
    _step(2, total_steps, "Setting up virtual environment")
    _ensure_venv()

    # Step 3: Backend dependencies (always installed into venv)
    _step(3, total_steps, "Installing backend dependencies")
    _run_live(f'"{_venv_python()}" -m pip install -r "{ROOT / "backend" / "requirements.txt"}"')
    print("  Backend deps ✓")

    # Step 4: Frontend dependencies
    _step(4, total_steps, "Installing frontend dependencies")
    npm = _npm()
    if subprocess.run(f'"{npm}" --version', shell=True, capture_output=True).returncode != 0:
        _install_nodejs()
        if OS == "Windows":
            _refresh_path_windows()
        npm = _npm()
    _run_live(f'"{npm}" install', cwd=ROOT / "frontend")
    print("  Frontend deps ✓")

    # Step 5: Ollama — detect external SSD on macOS
    _step(5, total_steps, "Installing Ollama")
    ssd = _find_external_ssd()
    if ssd:
        print(f"  External SSD detected: {ssd} — Ollama will be installed there")

    if subprocess.run("ollama --version", shell=True, capture_output=True).returncode != 0:
        print("  Ollama not found — installing...")
        _install_ollama(ssd)

    ver_out = subprocess.run("ollama --version", shell=True, capture_output=True, text=True)
    ollama_version = ver_out.stdout.strip() or "Ollama"
    print(f"  {ollama_version} ✓")

    # Step 6: System scan + pull best model
    _step(6, total_steps, "Scanning system hardware and pulling best model")
    sys.path.insert(0, str(ROOT / "scripts"))
    from scan_system import scan, get_best_model

    info = scan()
    best = get_best_model(info)

    print(f"  RAM: {info['ram_gb']} GB | GPU VRAM: {info['gpu']['vram_gb']} GB")
    print(f"  Selected model: {best}")

    models_dir = str(ssd / "ollama-models") if ssd else None
    if models_dir:
        Path(models_dir).mkdir(parents=True, exist_ok=True)
        print(f"  Models directory: {models_dir}")

    _start_ollama_server(models_dir)

    if best not in info.get("models_pulled", []):
        print(f"  Pulling {best} (this may take several minutes)...")
        pull_env = {"OLLAMA_MODELS": models_dir} if models_dir else None
        _run_live(f"ollama pull {best}", extra_env=pull_env)
    else:
        print(f"  Model {best} already pulled ✓")

    # Step 7: Create .env
    _step(7, total_steps, "Creating configuration file")
    env_path = ROOT / ".env"
    if not env_path.exists():
        example = (ROOT / ".env.example").read_text(encoding="utf-8")
        example = example.replace("DEFAULT_MODEL=llama3.2", f"DEFAULT_MODEL={best}")
        if models_dir:
            example = example.replace("OLLAMA_MODELS=", f"OLLAMA_MODELS={models_dir}")
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
║  ✓ Virtual env       .venv                  ║
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
