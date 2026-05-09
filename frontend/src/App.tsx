import { useState, useEffect } from "react";
import { Trash2, RefreshCw } from "lucide-react";
import { fetchModels, fetchSkills, ModelInfo, SkillInfo } from "./api/client";
import { useChat } from "./hooks/useChat";
import { ProviderToggle } from "./components/ProviderToggle";
import { ModelSelector } from "./components/ModelSelector";
import { WorkspaceBar } from "./components/WorkspaceBar";
import { ChatWindow } from "./components/ChatWindow";
import { InputBar } from "./components/InputBar";

export default function App() {
  const [provider, setProvider] = useState<"local" | "api">("local");
  const [selectedModel, setSelectedModel] = useState("");
  const [workingDir, setWorkingDir] = useState(() => localStorage.getItem("workingDir") ?? "");
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [_skills, setSkills] = useState<SkillInfo[]>([]);
  const [apiKeySet, setApiKeySet] = useState(false);
  const [loadingModels, setLoadingModels] = useState(false);

  const { messages, isLoading, sendMessage, clearMessages } = useChat();

  const loadModels = async () => {
    setLoadingModels(true);
    try {
      const [m, s] = await Promise.all([fetchModels(), fetchSkills()]);
      setModels(m);
      setSkills(s);
      const hasApi = m.some((x) => x.provider === "api");
      setApiKeySet(hasApi);
      const localModels = m.filter((x) => x.provider === "local");
      if (!selectedModel && localModels.length > 0) {
        setSelectedModel(localModels[0].id);
      }
    } catch {
      // backend may not be running yet
    } finally {
      setLoadingModels(false);
    }
  };

  useEffect(() => {
    loadModels();
  }, []);

  useEffect(() => {
    const filtered = models.filter((m) => m.provider === provider);
    if (filtered.length > 0 && !filtered.find((m) => m.id === selectedModel)) {
      setSelectedModel(filtered[0].id);
    }
  }, [provider, models]);

  const handleWorkingDirChange = (dir: string) => {
    setWorkingDir(dir);
    localStorage.setItem("workingDir", dir);
  };

  const handleSend = ({ skill, skillArgs, content }: { skill?: string; skillArgs?: string; content: string }) => {
    sendMessage({
      content,
      provider,
      model: selectedModel,
      workingDir,
      skill,
      skillArgs,
    });
  };

  return (
    <div className="flex flex-col h-screen bg-gray-950 text-gray-100">
      {/* Header */}
      <header className="flex items-center justify-between px-4 py-2.5 border-b border-gray-800 bg-gray-900">
        <div className="flex items-center gap-3">
          <span className="font-semibold text-sm tracking-wide text-white">AI Local Engine</span>
          <ProviderToggle provider={provider} onChange={setProvider} apiKeySet={apiKeySet} />
          <ModelSelector
            models={models}
            provider={provider}
            selectedModel={selectedModel}
            onChange={setSelectedModel}
          />
          <button
            onClick={loadModels}
            disabled={loadingModels}
            title="Refresh model list"
            className="p-1.5 rounded hover:bg-gray-800 text-gray-500 hover:text-gray-300 transition-colors"
          >
            <RefreshCw size={14} className={loadingModels ? "animate-spin" : ""} />
          </button>
        </div>
        <button
          onClick={clearMessages}
          title="Clear conversation"
          className="p-1.5 rounded hover:bg-gray-800 text-gray-500 hover:text-gray-300 transition-colors"
        >
          <Trash2 size={14} />
        </button>
      </header>

      {/* Workspace bar */}
      <WorkspaceBar workingDir={workingDir} onChange={handleWorkingDirChange} />

      {/* Chat area */}
      <ChatWindow messages={messages} />

      {/* Input */}
      <InputBar onSend={handleSend} disabled={isLoading || !selectedModel} />
    </div>
  );
}
