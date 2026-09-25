from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "NuevaMente"
    ENVIRONMENT: str = "development"

    MAX_FILE_SIZE_MB: int = 10

    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MIN_SCORE: float = 0.25

    FIDELITY_THRESHOLD: float = 0.90

    LLM_PROVIDER: str = "mock"
    EMBEDDING_PROVIDER: str = "mock"

    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-3.1-flash-lite"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-2"

    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_RETRIES: int = 1

    CHROMA_PERSIST_DIR: str = "./data/chroma"

    OCI_CONFIG_FILE: str = "~/.oci/config"
    OCI_PROFILE: str = "DEFAULT"
    OCI_BUCKET_NAME: str = "nuevamente-g10"
    OCI_NAMESPACE: str | None = None

    DATABASE_URL: str = "sqlite:///./data/sqlite/nuevamente.db"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
