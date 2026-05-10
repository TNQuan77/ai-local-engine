import React from "react";
import { ChatMessage } from "../hooks/useChat";
import hljs from "highlight.js";
import "highlight.js/styles/atom-one-dark.css";
import { Copy } from "lucide-react";

interface CodeBlockProps {
  language: string;
  code: string;
}

function CodeBlock({ language, code }: CodeBlockProps) {
  const highlighted =
    language && hljs.getLanguage(language)
      ? hljs.highlight(code, { language, ignoreIllegals: true }).value
      : hljs.highlightAuto(code).value;

  const [copied, setCopied] = React.useState(false);
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="my-3 rounded-lg overflow-hidden bg-gray-900 border border-gray-700">
      <div className="flex items-center justify-between px-3 py-2 bg-gray-800">
        <span className="text-xs font-mono text-gray-400">{language || "code"}</span>
        <button
          onClick={handleCopy}
          className="p-1.5 hover:bg-gray-700 rounded transition-colors"
          title="Copy code"
        >
          <Copy size={14} className={copied ? "text-green-400" : "text-gray-400"} />
        </button>
      </div>
      <pre className="p-3 overflow-x-auto">
        <code
          dangerouslySetInnerHTML={{ __html: highlighted }}
          className={`language-${language} text-xs`}
        />
      </pre>
    </div>
  );
}

function parseContent(content: string) {
  const parts: React.ReactNode[] = [];
  const codeBlockRegex = /```(\w*)\n([\s\S]*?)```/g;
  let lastIndex = 0;
  let match;

  while ((match = codeBlockRegex.exec(content)) !== null) {
    // Add text before code block
    if (match.index > lastIndex) {
      parts.push(
        <div key={`text-${lastIndex}`} className="whitespace-pre-wrap">
          {content.slice(lastIndex, match.index)}
        </div>
      );
    }
    // Add code block
    parts.push(
      <CodeBlock
        key={`code-${match.index}`}
        language={match[1]}
        code={match[2].trim()}
      />
    );
    lastIndex = match.index + match[0].length;
  }

  // Add remaining text
  if (lastIndex < content.length) {
    parts.push(
      <div key={`text-${lastIndex}`} className="whitespace-pre-wrap">
        {content.slice(lastIndex)}
      </div>
    );
  }

  return parts.length > 0 ? parts : <div className="whitespace-pre-wrap">{content}</div>;
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
          <div className="bg-gray-800 rounded-2xl rounded-tl-sm px-4 py-2 text-sm text-gray-100">
            {parseContent(message.content)}
          </div>
        )}
      </div>
    </div>
  );
}
