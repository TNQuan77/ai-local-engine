"""
Ollama local agent with tool-use loop.

Agent loop pattern:
  send messages + tools → get response
  if tool_calls → execute → append tool results → repeat
  until no more tool_calls
"""
import re
from typing import AsyncGenerator, Any
import ollama

from tools.file_tools import make_file_tools
from tools.extended_tools import make_extended_tools


def _clean_assistant_text(text: str) -> str:
    """Remove JSON tool call blocks and internal logging from assistant text."""
    # Remove JSON blocks that look like tool calls (e.g., ```json {...}``` or bare {})
    text = re.sub(r'```json\s*\{[^}]*\}```', '', text, flags=re.DOTALL)
    text = re.sub(r'```\s*\{[^}]*\}```', '', text, flags=re.DOTALL)
    # Remove lines that are just JSON objects
    text = re.sub(r'^\s*\{.*?"name".*?\}\s*$', '', text, flags=re.MULTILINE)
    # Clean up extra whitespace
    text = re.sub(r'\n\s*\n', '\n', text).strip()
    return text

SYSTEM_PROMPT = (
    "You are a helpful coding assistant. "
    "You have access to tools to read, edit, create files and run commands. "
    "Working directory: {working_dir}\n"
    "CRITICAL: When a user asks you to create ANY file, you MUST immediately call the 'create_file' tool with the exact path and content provided. Do not describe or explain - just execute the tool.\n"
    "Available tools: create_file(path, content), create_directory(path), read_file(path), edit_file(path, old_string, new_string), run_bash(command), list_files(pattern), search_in_files(text, file_pattern)\n"
    "When creating HTML files, simply create the file and confirm it's been created. Do not suggest running a web server unless the user explicitly asks for it.\n"
    "When creating files or directories, use the specific create_file or create_directory tools instead of shell commands like 'touch' or 'mkdir', as they provide better cross-platform support and verification.\n"
    "After creating code files, consider running them to test if they work, and if there are errors, attempt to fix them.\n"
    "Before making significant changes or running potentially destructive commands, ask the user for confirmation.\n"
    "Never include tool call names, tool arguments, or internal execution logs in the user-facing response. "
    "Use tools internally only, and summarize the result in plain language. "
    "The final assistant reply should be concise, helpful, and free of debug details."
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
            if msg.tool_calls:
                tool_calls.extend(msg.tool_calls)

        if not tool_calls and content:
            # Check if user asked to create a file but agent didn't call tool
            user_msg = messages[-1]["content"] if messages else ""
            if "create" in user_msg.lower() and "file" in user_msg.lower():
                # Force call create_file tool
                import re
                # Extract filename and content from user message
                filename_match = re.search(r'called?\s+(\w+\.\w+)', user_msg)
                content_match = re.search(r'content\s+[\'"]([^\'"]+)[\'"]', user_msg)
                if filename_match and content_match:
                    filename = filename_match.group(1)
                    file_content = content_match.group(1)
                    tool_calls = [{"function": {"name": "create_file", "arguments": {"path": filename, "content": file_content}}}]

        if not tool_calls:
            break

        for tc in tool_calls:
            name = tc.function.name
            args: dict = tc.function.arguments or {}

            print(f"[DEBUG] Tool call: {name} with args: {args}")  # Debug log

            yield {"type": "tool_call", "name": name, "input": args}

            if name in tool_map:
                try:
                    result = tool_map[name](**args)
                    print(f"[DEBUG] Tool result: {result}")  # Debug log
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
