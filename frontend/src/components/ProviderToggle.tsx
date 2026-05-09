interface Props {
  provider: "local" | "api";
  onChange: (p: "local" | "api") => void;
  apiKeySet: boolean;
}

export function ProviderToggle({ provider, onChange, apiKeySet }: Props) {
  return (
    <div className="flex items-center gap-1 bg-gray-800 rounded-lg p-1">
      <button
        onClick={() => onChange("local")}
        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
          provider === "local"
            ? "bg-green-600 text-white"
            : "text-gray-400 hover:text-gray-200"
        }`}
      >
        Local
      </button>
      <button
        onClick={() => onChange("api")}
        title={!apiKeySet ? "Set ANTHROPIC_API_KEY in .env to use Claude API" : ""}
        className={`px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
          provider === "api"
            ? "bg-blue-600 text-white"
            : "text-gray-400 hover:text-gray-200"
        } ${!apiKeySet ? "opacity-50 cursor-not-allowed" : ""}`}
      >
        API {!apiKeySet && "🔒"}
      </button>
    </div>
  );
}
