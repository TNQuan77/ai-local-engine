import json
from typing import AsyncGenerator

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from schemas import ChatRequest
from skills.registry import get_skill_prompt

router = APIRouter()


async def _event_stream(gen: AsyncGenerator) -> AsyncGenerator[str, None]:
    async for event in gen:
        yield f"data: {json.dumps(event)}\n\n"


@router.post("/chat")
async def chat(request: ChatRequest):
    skill_prompt: str | None = None
    if request.skill:
        skill_prompt = get_skill_prompt(
            request.skill,
            request.working_dir,
            request.skill_args or "",
        )

    messages = [m.model_dump() for m in request.messages]

    if request.provider == "local":
        from agents.ollama_agent import run
        gen = run(
            messages=messages,
            model=request.model,
            working_dir=request.working_dir,
            skill_prompt=skill_prompt,
        )
    else:
        from agents.claude_agent import run
        gen = run(
            messages=messages,
            model=request.model,
            working_dir=request.working_dir,
            skill_prompt=skill_prompt,
        )

    return StreamingResponse(
        _event_stream(gen),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
