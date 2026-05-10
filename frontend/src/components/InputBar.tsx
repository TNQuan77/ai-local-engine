import { useState, KeyboardEvent } from "react";
import { Send, Loader2, X } from "lucide-react";

interface ParsedInput {
  skill?: string;
  skillArgs?: string;
  content: string;
}

function parseInput(text: string): ParsedInput {
  const match = text.match(/^\/(\w+)\s*(.*)/s);
  if (match) {
    return { skill: match[1], skillArgs: match[2].trim(), content: text };
  }
  return { content: text };
}

interface Props {
  onSend: (parsed: ParsedInput) => void;
  onCancel: () => void;
  disabled: boolean;
  isStreaming: boolean;
}

export function InputBar({ onSend, onCancel, disabled, isStreaming }: Props) {
  const [value, setValue] = useState("");

  const handleSend = () => {
    const trimmed = value.trim();
    if (!trimmed || disabled) return;
    onSend(parseInput(trimmed));
    setValue("");
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const isSkill = value.trimStart().startsWith("/");

  return (
    <div className="px-4 py-3 border-t border-gray-800 bg-gray-950">
      <div className={`flex items-end gap-2 bg-gray-800 rounded-xl px-4 py-2 border ${isSkill ? "border-amber-600" : "border-gray-700"} focus-within:border-blue-500 transition-colors`}>
        <textarea
          value={value}
          onChange={(e) => setValue(e.target.value)}
          onKeyDown={handleKeyDown}
          placeholder='Message the agent… or use /review, /refactor, /test, /fix, /docs, /commit'
          disabled={disabled}
          rows={1}
          style={{ resize: "none", minHeight: "36px", maxHeight: "160px" }}
          className="flex-1 bg-transparent text-sm text-gray-100 placeholder-gray-600 focus:outline-none overflow-y-auto"
          onInput={(e) => {
            const t = e.currentTarget;
            t.style.height = "auto";
            t.style.height = `${Math.min(t.scrollHeight, 160)}px`;
          }}
        />
        <button
          onClick={handleSend}
          disabled={disabled || !value.trim()}
          className="shrink-0 p-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 disabled:opacity-40 disabled:cursor-not-allowed transition-colors"
        >
          {disabled ? <Loader2 size={16} className="animate-spin" /> : <Send size={16} />}
        </button>
        {isStreaming && (
          <button
            onClick={onCancel}
            className="shrink-0 p-1.5 rounded-lg bg-red-600 hover:bg-red-500 transition-colors"
            title="Cancel current response"
          >
            <X size={16} />
          </button>
        )}
      </div>
      {isSkill && (
        <p className="text-xs text-amber-500 mt-1 px-1">Skill command detected</p>
      )}
    </div>
  );
}
