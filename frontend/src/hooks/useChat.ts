import { useState, useCallback, useRef } from "react";
import { streamChat, SSEEvent } from "../api/client";

export interface ChatMessage {
  id: string;
  role: "user" | "assistant";
  content: string;
  events: SSEEvent[];
  isStreaming: boolean;
}

let msgCounter = 0;
const nextId = () => `msg-${++msgCounter}`;

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const abortRef = useRef<boolean>(false);

  const sendMessage = useCallback(
    async (params: {
      content: string;
      provider: "local" | "api";
      model: string;
      workingDir: string;
      skill?: string;
      skillArgs?: string;
    }) => {
      const { content, provider, model, workingDir, skill, skillArgs } = params;

      const userMsg: ChatMessage = {
        id: nextId(),
        role: "user",
        content,
        events: [],
        isStreaming: false,
      };

      const assistantMsg: ChatMessage = {
        id: nextId(),
        role: "assistant",
        content: "",
        events: [],
        isStreaming: true,
      };

      setMessages((prev) => [...prev, userMsg, assistantMsg]);
      setIsLoading(true);
      abortRef.current = false;

      const history = messages
        .filter((m) => !m.isStreaming)
        .map((m) => ({ role: m.role, content: m.content }));

      try {
        const gen = streamChat({
          provider,
          model,
          messages: [...history, { role: "user", content }],
          working_dir: workingDir,
          skill,
          skill_args: skillArgs,
        });

        for await (const event of gen) {
          if (abortRef.current) break;

          setMessages((prev) =>
            prev.map((m) => {
              if (m.id !== assistantMsg.id) return m;
              const newEvents = [...m.events, event];
              const newContent =
                event.type === "text" ? m.content + (event.content ?? "") : m.content;
              return { ...m, content: newContent, events: newEvents };
            })
          );

          if (event.type === "done") break;
        }
      } catch (err) {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsg.id
              ? { ...m, content: `Error: ${err}`, events: [...m.events, { type: "error" as const, content: String(err) }] }
              : m
          )
        );
      } finally {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === assistantMsg.id ? { ...m, isStreaming: false } : m
          )
        );
        setIsLoading(false);
      }
    },
    [messages]
  );

  const cancelMessage = useCallback(() => {
    abortRef.current = true;
    setIsLoading(false);
    setMessages((prev) =>
      prev.map((m) =>
        m.isStreaming ? { ...m, isStreaming: false, content: m.content + " [Cancelled]" } : m
      )
    );
  }, []);

  const clearMessages = useCallback(() => setMessages([]), []);

  return { messages, isLoading, sendMessage, cancelMessage, clearMessages };
}
