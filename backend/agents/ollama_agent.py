"""
Ollama local agent with tool-use loop.

Agent loop pattern:
  send messages + tools → get response
  if tool_calls → execute → append tool results → repeat
  until no more tool_calls
"""
from typing import AsyncGenerator, Any
import ollama

from tools.file_tools import make_file_tools
from tools.extended_tools import make_extended_tools

SYSTEM_PROMPT = (
    "You are a helpful coding assistant. "
    "You have access to tools to read, edit, create files and run commands. "
    "Working directory: {working_dir}\n"
    "Use tools whenever needed to answer the user's request accurately."
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
    client = ollama.AsyncClient()

    file_tools = make_file_tools(working_dir) if working_dir else []
    ext_tools = make_extended_tools(working_dir) if working_dir else []
    all_tools = file_tools + ext_tools
    tool_map: dict[str, Any] = {fn.__name__: fn for fn in all_tools}

    system_content = SYSTEM_PROMPT.format(working_dir=working_dir or "(none)")
    if skill_prompt:
        system_content += f"\n\n{skill_prompt}"

    full_messages: list[dict] = [{"role": "system", "content": system_content}] + [
        m if isinstance(m, dict) else m.model_dump() for m in messages
    ]

    while True:
        stream = await client.chat(
            model=model,
            messages=full_messages,
            tools=all_tools if all_tools else None,
            stream=True,
        )

        content = ""
        tool_calls: list = []

        async for chunk in stream:
            msg = chunk.message
            if msg.content:
                content += msg.content
                yield {"type": "text", "content": msg.content}
            if msg.tool_calls:
                tool_calls.extend(msg.tool_calls)

        full_messages.append({
            "role": "assistant",
            "content": content,
            "tool_calls": tool_calls,
        })

        if not tool_calls:
            break

        for tc in tool_calls:
            name = tc.function.name
            args: dict = tc.function.arguments or {}

            yield {"type": "tool_call", "name": name, "input": args}

            if name in tool_map:
                try:
                    result = tool_map[name](**args)
                except Exception as exc:
                    result = f"ERROR: {exc}"
            else:
                result = f"ERROR: unknown tool '{name}'"

            yield {"type": "tool_result", "content": str(result)}

            full_messages.append({
                "role": "tool",
                "tool_name": name,
                "content": str(result),
            })

    yield {"type": "done"}
