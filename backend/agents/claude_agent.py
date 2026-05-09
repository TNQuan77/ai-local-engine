"""
Claude API agent using claude-agent-sdk.

Uses ClaudeSDKClient with built-in coding tools:
  Read, Write, Edit, Bash, Glob, Grep
"""
from typing import AsyncGenerator, Any

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions

CODING_TOOLS = [
    "Read",
    "Write",
    "Edit",
    "Bash",
    "Glob",
    "Grep",
]

SYSTEM_PROMPT = (
    "You are a helpful coding assistant. "
    "Use the provided tools to read, edit, and create files, run shell commands, "
    "and search through codebases. "
    "Working directory: {working_dir}"
)


async def run(
    messages: list[dict],
    model: str,
    working_dir: str,
    skill_prompt: str | None = None,
) -> AsyncGenerator[dict[str, Any], None]:
    """
    Yield SSE event dicts:
      {"type": "text",        "content": "..."}
      {"type": "tool_call",   "name": "...", "input": {...}}
      {"type": "tool_result", "content": "..."}
      {"type": "done"}
    """
    system = SYSTEM_PROMPT.format(working_dir=working_dir or "(none)")
    if skill_prompt:
        system += f"\n\n{skill_prompt}"

    # Build prompt from messages list
    user_messages = [m if isinstance(m, dict) else m.model_dump() for m in messages]
    prompt = user_messages[-1]["content"] if user_messages else ""

    options = ClaudeAgentOptions(
        model=model,
        allowed_tools=CODING_TOOLS,
        cwd=working_dir or None,
        system_prompt=system,
    )

    async with ClaudeSDKClient(options=options) as client:
        async for event in client.stream(prompt):
            event_type = getattr(event, "type", None)

            if event_type == "text":
                yield {"type": "text", "content": event.text}

            elif event_type == "tool_use":
                yield {
                    "type": "tool_call",
                    "name": event.name,
                    "input": event.input or {},
                }

            elif event_type == "tool_result":
                content = event.content
                if isinstance(content, list):
                    content = "\n".join(
                        c.get("text", "") if isinstance(c, dict) else str(c)
                        for c in content
                    )
                yield {"type": "tool_result", "content": str(content)}

    yield {"type": "done"}
