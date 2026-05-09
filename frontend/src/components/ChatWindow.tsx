import { useEffect, useRef } from "react";
import { ChatMessage } from "../hooks/useChat";
import { MessageBubble } from "./MessageBubble";
import { Bot } from "lucide-react";

interface Props {
  messages: ChatMessage[];
}

export function ChatWindow({ messages }: Props) {
  const bottomRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  if (messages.length === 0) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center text-gray-600 gap-3">
        <Bot size={48} strokeWidth={1} />
        <p className="text-sm">Set a workspace path above, then start chatting.</p>
        <p className="text-xs text-gray-700">Try: <span className="font-mono text-gray-500">/review</span>, <span className="font-mono text-gray-500">/refactor src/main.py</span>, <span className="font-mono text-gray-500">/test</span></p>
      </div>
    );
  }

  return (
    <div className="flex-1 overflow-y-auto px-4 py-4 space-y-1">
      {messages.map((msg) => (
        <MessageBubble key={msg.id} message={msg} />
      ))}
      <div ref={bottomRef} />
    </div>
  );
}
