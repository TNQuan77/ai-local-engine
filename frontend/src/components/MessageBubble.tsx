import { useState } from "react";
import { ChevronDown, ChevronRight, Terminal, FileEdit, Search } from "lucide-react";
import { ChatMessage } from "../hooks/useChat";
import { SSEEvent } from "../api/client";

const TOOL_ICONS: Record<string, React.ReactNode> = {
  run_bash: <Terminal size={12} />,
  edit_file: <FileEdit size={12} />,
  write_file: <FileEdit size={12} />,
  search_in_files: <Search size={12} />,
  Bash: <Terminal size={12} />,
  Edit: <FileEdit size={12} />,
  Grep: <Search size={12} />,
};

function ToolCallBlock({ event, resultEvent }: { event: SSEEvent; resultEvent?: SSEEvent }) {
  const [open, setOpen] = useState(false);
  const icon = TOOL_ICONS[event.name ?? ""] ?? <Terminal size={12} />;

  return (
    <div className="my-1 rounded border border-gray-700 bg-gray-900 text-xs">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-2 w-full px-3 py-1.5 text-left text-amber-400 hover:bg-gray-800 rounded"
      >
        {open ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
        {icon}
        <span className="font-mono font-semibold">{event.name}</span>
        {event.input && (
          <span className="text-gray-500 truncate max-w-xs">
            {Object.entries(event.input)
              .map(([k, v]) => `${k}=${JSON.stringify(v).slice(0, 40)}`)
              .join(", ")}
          </span>
        )}
      </button>
      {open && (
        <div className="px-3 pb-2 space-y-1">
          {event.input && (
            <pre className="text-gray-400 overflow-x-auto">
              {JSON.stringify(event.input, null, 2)}
            </pre>
          )}
          {resultEvent?.content && (
            <>
              <div className="text-gray-600 text-xs mt-1">Result:</div>
              <pre className="text-green-400 overflow-x-auto max-h-48">
                {resultEvent.content}
              </pre>
            </>
          )}
        </div>
      )}
    </div>
  );
}

interface Props {
  message: ChatMessage;
}

export function MessageBubble({ message }: Props) {
  const isUser = message.role === "user";

  if (isUser) {
    return (
      <div className="flex justify-end mb-4">
        <div className="max-w-[75%] bg-blue-600 text-white rounded-2xl rounded-br-sm px-4 py-2 text-sm whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    );
  }

  // Build assistant content with inline tool call blocks
  const toolCallEvents = message.events.filter((e) => e.type === "tool_call");
  const toolResultEvents = message.events.filter((e) => e.type === "tool_result");

  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[85%] w-full">
        <div className="inline-flex items-center gap-1.5 mb-1">
          <div className="w-5 h-5 rounded-full bg-purple-600 flex items-center justify-center text-xs font-bold">A</div>
          <span className="text-xs text-gray-500">Assistant</span>
          {message.isStreaming && (
            <span className="inline-block w-1.5 h-3 bg-gray-400 animate-pulse ml-1" />
          )}
        </div>

        {message.content && (
          <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-2 text-sm text-gray-100 whitespace-pre-wrap mb-1">
            {message.content}
          </div>
        )}

        {toolCallEvents.map((tc, i) => (
          <ToolCallBlock
            key={i}
            event={tc}
            resultEvent={toolResultEvents[i]}
          />
        ))}
      </div>
    </div>
  );
}
