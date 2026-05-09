import { useState } from "react";
import { FolderOpen } from "lucide-react";

interface Props {
  workingDir: string;
  onChange: (dir: string) => void;
}

export function WorkspaceBar({ workingDir, onChange }: Props) {
  const [draft, setDraft] = useState(workingDir);

  const commit = () => {
    onChange(draft.trim());
  };

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-gray-900 border-b border-gray-800">
      <FolderOpen size={16} className="text-gray-400 shrink-0" />
      <input
        type="text"
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && commit()}
        onBlur={commit}
        placeholder="Enter project directory path (e.g. C:/Users/you/my-project)"
        className="flex-1 bg-transparent text-sm text-gray-300 placeholder-gray-600 focus:outline-none"
        spellCheck={false}
      />
      {workingDir && (
        <span className="text-xs text-green-500">✓ workspace set</span>
      )}
    </div>
  );
}
