"""
Claude API agent using claude-agent-sdk.

Uses ClaudeSDKClient with built-in coding tools:
  Read, Write, Edit, Bash, Glob, Grep
"""
import re
from typing import AsyncGenerator, Any

from claude_agent_sdk import ClaudeSDKClient, ClaudeAgentOptions


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
    "Working directory: {working_dir}\n"
    "CRITICAL: When a user asks you to create ANY file, you MUST immediately call the 'create_file' tool with the exact path and content provided. Do not describe or explain - just execute the tool.\n"
    "Available tools: create_file(path, content), create_directory(path), read_file(path), edit_file(path, old_string, new_string), run_bash(command), list_files(pattern), search_in_files(text, file_pattern)\n"
    "When creating HTML files, simply create the file and confirm it's been created. Do not suggest running a web server unless the user explicitly asks for it.\n"
    "When creating files or directories, use the specific create_file or create_directory tools instead of shell commands like 'touch' or 'mkdir', as they provide better cross-platform support and verification.\n"
    "After creating code files, consider running them to test if they work, and if there are errors, attempt to fix them.\n"
    "Before making significant changes or running potentially destructive commands, ask the user for confirmation.\n"
    "Do not expose tool call names, tool inputs, or internal execution logs in the user-facing response. "
    "Keep the final assistant answer focused on the result and free of debug details."
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
        text_content = ""
        async for event in client.stream(prompt):
            event_type = getattr(event, "type", None)

            if event_type == "text":
                text_content += event.text or ""

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

        if text_content:
            cleaned = _clean_assistant_text(text_content)
            if cleaned:
                yield {"type": "text", "content": cleaned}

    yield {"type": "done"}
