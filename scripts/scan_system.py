"""
System scanner: detects hardware specs and recommends the best Ollama model.
Can run standalone: python scripts/scan_system.py
"""
import platform
import subprocess
from pathlib import Path


def _run(cmd: str) -> str:
    try:
        return subprocess.check_output(cmd, shell=True, text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        return ""


def detect_gpu() -> dict:
    os_name = platform.system()

    # NVIDIA (Windows + Linux)
    out = _run("nvidia-smi --query-gpu=name,memory.total --format=csv,noheader,nounits")
    if out:
        parts = out.split(", ", 1)
        if len(parts) == 2:
            name, vram_mb = parts
            return {"vendor": "NVIDIA", "name": name.strip(), "vram_gb": round(int(vram_mb) / 1024, 1)}

    # AMD (Linux)
    if os_name == "Linux":
        out = _run("rocm-smi --showmeminfo vram --json")
        if out:
            try:
                import json
                data = json.loads(out)
                for card_data in data.values():
                    vram_bytes = int(card_data.get("VRAM Total Memory (B)", 0))
                    if vram_bytes:
                        return {"vendor": "AMD", "name": "AMD GPU", "vram_gb": round(vram_bytes / 1e9, 1)}
            except Exception:
                pass

    # Apple Silicon (macOS)
    if os_name == "Darwin":
        out = _run("system_profiler SPDisplaysDataType")
        if "Apple M" in out:
            import psutil
            # Apple Silicon shares RAM with GPU; use total RAM as approximation
            ram_gb = round(psutil.virtual_memory().total / 1e9, 1)
            return {"vendor": "Apple Silicon", "name": "Metal GPU", "vram_gb": ram_gb}

    return {"vendor": "CPU-only", "name": "", "vram_gb": 0}


def check_ollama() -> bool:
    return bool(_run("ollama --version"))


def list_ollama_models() -> list[str]:
    out = _run("ollama list")
    models = []
    for line in out.splitlines()[1:]:  # skip header
        parts = line.split()
        if parts:
            models.append(parts[0])
    return models


def scan() -> dict:
    import psutil

    return {
        "os": platform.system(),
        "os_version": platform.version(),
        "cpu_cores": psutil.cpu_count(logical=True),
        "ram_gb": round(psutil.virtual_memory().total / 1e9, 1),
        "disk_free_gb": round(psutil.disk_usage(Path.home()).free / 1e9, 1),
        "gpu": detect_gpu(),
        "ollama_installed": check_ollama(),
        "models_pulled": list_ollama_models(),
    }


# Model catalog: (id, min_ram_gb, min_vram_gb, quality_score, description)
MODEL_CATALOG = [
    ("qwen2.5:14b",   16, 10, 90, "Best quality for mid-range GPU"),
    ("llama3.1:8b",   12,  6, 80, "Fast, GPU accelerated"),
    ("qwen2.5:7b",    10,  5, 75, "Good balance of speed and quality"),
    ("llama3.2:3b",    6,  0, 60, "Lightweight, CPU friendly"),
    ("llama3.2:1b",    4,  0, 40, "Minimal resource usage"),
    ("qwen2.5:0.5b",   3,  0, 30, "Ultra lightweight fallback"),
]


def get_recommendations(info: dict) -> list[dict]:
    ram = info["ram_gb"]
    vram = info["gpu"]["vram_gb"]
    recs = []
    for model_id, min_ram, min_vram, score, desc in MODEL_CATALOG:
        if ram >= min_ram and (vram >= min_vram or min_vram == 0):
            recs.append({
                "id": model_id,
                "score": score,
                "reason": desc,
                "already_pulled": model_id in info.get("models_pulled", []),
            })
    recs.sort(key=lambda x: -x["score"])
    return recs[:5]


def get_best_model(info: dict) -> str:
    # If a model is already pulled and meets requirements, prefer it
    for m in info.get("models_pulled", []):
        for model_id, min_ram, min_vram, _, _ in MODEL_CATALOG:
            if m == model_id and info["ram_gb"] >= min_ram:
                return m

    recs = get_recommendations(info)
    return recs[0]["id"] if recs else "llama3.2:1b"


if __name__ == "__main__":
    info = scan()
    recs = get_recommendations(info)
    best = get_best_model(info)

    print("=== AI Local Engine — System Scan ===\n")
    print(f"  OS:          {info['os']} {info['os_version'][:40]}")
    print(f"  CPU Cores:   {info['cpu_cores']}")
    print(f"  RAM:         {info['ram_gb']} GB")
    gpu = info["gpu"]
    if gpu["vram_gb"]:
        print(f"  GPU:         {gpu['vendor']} {gpu['name']} ({gpu['vram_gb']} GB VRAM)")
    else:
        print(f"  GPU:         {gpu['vendor']}")
    print(f"  Disk Free:   {info['disk_free_gb']} GB")
    print(f"  Ollama:      {'Installed ✓' if info['ollama_installed'] else 'Not installed ✗'}")
    if info["models_pulled"]:
        print(f"  Models:      {', '.join(info['models_pulled'])}")

    print("\n=== Recommended Models ===\n")
    for r in recs:
        star = "★" if r["id"] == best else " "
        pulled = " (already pulled)" if r["already_pulled"] else ""
        print(f"  {star} {r['id']:<25} — {r['reason']}{pulled}")

    print(f"\nBest model for this system: {best}")
    if not info["ollama_installed"]:
        print("\nInstall Ollama first: https://ollama.com/download")
    else:
        print(f"\nRun to install: ollama pull {best}")
