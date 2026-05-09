export interface ModelInfo {
  id: string;
  provider: "local" | "api";
  name: string;
}

export interface SkillInfo {
  name: string;
  description: string;
}

export interface SSEEvent {
  type: "text" | "tool_call" | "tool_result" | "error" | "done";
  content?: string;
  name?: string;
  input?: Record<string, unknown>;
}

export async function fetchModels(): Promise<ModelInfo[]> {
  const res = await fetch("/api/models");
  if (!res.ok) throw new Error("Failed to fetch models");
  return res.json();
}

export async function fetchSkills(): Promise<SkillInfo[]> {
  const res = await fetch("/api/skills");
  if (!res.ok) return [];
  return res.json();
}

export interface ChatPayload {
  provider: "local" | "api";
  model: string;
  messages: { role: string; content: string }[];
  working_dir: string;
  skill?: string;
  skill_args?: string;
}

export async function* streamChat(payload: ChatPayload): AsyncGenerator<SSEEvent> {
  const res = await fetch("/api/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });

  if (!res.ok) {
    yield { type: "error", content: `HTTP error ${res.status}` };
    return;
  }

  const reader = res.body!.getReader();
  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split("\n");
    buffer = lines.pop() ?? "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const jsonStr = line.slice(6).trim();
        if (!jsonStr) continue;
        try {
          yield JSON.parse(jsonStr) as SSEEvent;
        } catch {
          // ignore malformed events
        }
      }
    }
  }
}
