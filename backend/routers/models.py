import httpx
from fastapi import APIRouter

from config import settings
from schemas import ModelInfo
from skills.registry import list_skills

router = APIRouter()

CLAUDE_MODELS = [
    ModelInfo(id="claude-opus-4-7",   provider="api", name="Claude Opus 4.7"),
    ModelInfo(id="claude-sonnet-4-6", provider="api", name="Claude Sonnet 4.6"),
    ModelInfo(id="claude-haiku-4-5",  provider="api", name="Claude Haiku 4.5"),
]


async def _get_ollama_models() -> list[ModelInfo]:
    try:
        async with httpx.AsyncClient(timeout=5) as client:
            resp = await client.get(f"{settings.ollama_base_url}/api/tags")
            data = resp.json()
            return [
                ModelInfo(
                    id=m["name"],
                    provider="local",
                    name=m["name"].replace(":", " ").title(),
                )
                for m in data.get("models", [])
            ]
    except Exception:
        return []


@router.get("/models", response_model=list[ModelInfo])
async def get_models():
    local_models = await _get_ollama_models()
    api_models = CLAUDE_MODELS if settings.anthropic_api_key else []
    return local_models + api_models


@router.get("/skills")
async def get_skills():
    return list_skills()
