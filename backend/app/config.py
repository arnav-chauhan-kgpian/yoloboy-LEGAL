"""Application configuration loaded from environment."""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    groq_api_key: str = ""

    chroma_collection: str = "legal_clauses"

    cors_origins: str = "http://localhost:3000,https://*.railway.app,https://*.up.railway.app"
    log_level: str = "INFO"

    demo_cache_enabled: bool = True
    demo_cache_path: str = "../data/cache"

    data_path: str = "./data"

    groq_model: str = "llama-3.3-70b-versatile"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()

