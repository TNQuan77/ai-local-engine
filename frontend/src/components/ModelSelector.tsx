import { ModelInfo } from "../api/client";

interface Props {
  models: ModelInfo[];
  provider: "local" | "api";
  selectedModel: string;
  onChange: (id: string) => void;
}

export function ModelSelector({ models, provider, selectedModel, onChange }: Props) {
  const filtered = models.filter((m) => m.provider === provider);

  return (
    <select
      value={selectedModel}
      onChange={(e) => onChange(e.target.value)}
      className="bg-gray-800 border border-gray-700 text-gray-200 text-sm rounded-lg px-3 py-1.5 focus:outline-none focus:ring-2 focus:ring-blue-500 min-w-[180px]"
    >
      {filtered.length === 0 && (
        <option value="" disabled>
          {provider === "local" ? "No local models — run ollama pull" : "No API models available"}
        </option>
      )}
      {filtered.map((m) => (
        <option key={m.id} value={m.id}>
          {m.name}
        </option>
      ))}
    </select>
  );
}
