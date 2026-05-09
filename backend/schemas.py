from typing import Literal, Any
from pydantic import BaseModel


class Message(BaseModel):
    role: Literal["user", "assistant", "system", "tool"]
    content: str


class ChatRequest(BaseModel):
    provider: Literal["local", "api"] = "local"
    model: str = "llama3.2"
    messages: list[Message]
    working_dir: str = ""
    skill: str | None = None
    skill_args: str | None = None


class ModelInfo(BaseModel):
    id: str
    provider: Literal["local", "api"]
    name: str


class SSEEvent(BaseModel):
    type: Literal["text", "tool_call", "tool_result", "error", "done"]
    content: str | None = None
    name: str | None = None
    input: dict[str, Any] | None = None
