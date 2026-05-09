from pathlib import Path
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ollama_base_url: str = "http://localhost:11434"
    default_model: str = "llama3.2"
    default_provider: str = "local"
    anthropic_api_key: str = ""

    model_config = {"env_file": str(Path(__file__).resolve().parent.parent / ".env")}


settings = Settings()
