from functools import lru_cache
from pathlib import Path
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CLINICAL_RAG_", env_file=".env", extra="ignore")

    app_name: str = "Clinical RAG Agent"
    model_id: str = "clinical-rag-agent"
    api_key: str = "local-dev-key"
    data_dir: Path = Field(default=Path("data"))
    llm_provider: str = "stub"
    llm_base_url: str = ""
    llm_api_key: str = ""
    llm_model: str = ""
    request_timeout_seconds: float = 45.0
    max_retrieval_chunks: int = 4

    @property
    def sessions_dir(self) -> Path:
        return self.data_dir / "sessions"

    @property
    def therapy_states_dir(self) -> Path:
        return self.data_dir / "therapy_states"

    @property
    def session_notes_dir(self) -> Path:
        return self.data_dir / "session_notes"

    @property
    def rag_dir(self) -> Path:
        return self.data_dir / "rag"


@lru_cache
def get_settings() -> Settings:
    return Settings()
