from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "EvidenceGraph"
    app_env: str = "development"
    app_debug: bool = True
    log_level: str = "INFO"

    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_prefix: str = "/api/v1"
    secret_key: str = "change-this-in-production"
    cors_origins: str = "http://localhost:5173"

    database_url: str = (
        "postgresql+psycopg://evidencegraph:"
        "evidencegraph_dev_password@db:5432/evidencegraph"
    )

    openalex_base_url: str = "https://api.openalex.org"
    openalex_email: str = "your_email@example.com"
    crossref_base_url: str = "https://api.crossref.org"
    semantic_scholar_base_url: str = (
        "https://api.semanticscholar.org/graph/v1"
    )
    semantic_scholar_api_key: str = ""

    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    agent_max_papers: int = 10
    request_timeout_seconds: int = 30

    llm_provider: str = "none"
    llm_model: str = ""
    llm_api_key: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()