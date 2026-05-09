import sys
from pathlib import Path

from fastapi import APIRouter

router = APIRouter()


@router.get("/system-scan")
async def system_scan():
    """Run system scan and return hardware info + model recommendations."""
    scripts_dir = Path(__file__).resolve().parent.parent.parent / "scripts"
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))

    try:
        from scan_system import scan, get_recommendations, get_best_model
        info = scan()
        return {
            "system": info,
            "recommendations": get_recommendations(info),
            "best_model": get_best_model(info),
        }
    except Exception as e:
        return {"error": str(e)}
