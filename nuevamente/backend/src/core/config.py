"""Configuración del sistema (FND-003).

Define las variables de entorno del Plan Técnico (Fase 6) con valores por
defecto seguros (proveedores en modo mock). `get_settings()` devuelve una
instancia cacheada; el `.env` se busca en la raíz del proyecto, sin importar
desde qué directorio se lance la API.
"""
from functools import lru_cache
from pathlib import Path
from typing import Self

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

PROJECT_ROOT = Path(__file__).resolve().parents[3]

_SQLITE_PREFIX = "sqlite:///"


class Settings(BaseSettings):
    """Esquema de configuración de la aplicación.

    Cada campo corresponde a una variable de `.env.example`.
    """

    APP_NAME: str = "NuevaMente"
    APP_VERSION: str = "0.1.0"
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"

    # Orígenes que pueden llamar a la API desde un navegador.
    CORS_ORIGINS: list[str] = ["http://localhost:8501", "http://127.0.0.1:8501"]

    # Ingesta — DT-12 (RF-001, ING-005)
    MAX_FILE_SIZE_MB: int = 10

    # Processing — TASK-002 (RF-005), PROC-005
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150
    MAX_DOCUMENT_CHARS: int = 2_000_000

    # RAG — BE-RAG-009/010
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MIN_SCORE: float = 0.25

    # Validación de fidelidad — DT-11
    FIDELITY_THRESHOLD: float = 0.90

    # Proveedores de IA — DT-09 ("gemini" | "cohere" | "mock")
    LLM_PROVIDER: str = "mock"          # "gemini" | "cohere" | "mock"
    EMBEDDING_PROVIDER: str = "mock"    # "gemini" | "cohere" | "mock"

    # Configuración de Gemini
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"

    # Configuración de Cohere
    COHERE_API_KEY: str | None = None
    COHERE_MODEL: str = "command-r-plus"
    COHERE_EMBEDDING_MODEL: str = "embed-multilingual-v3.0"

    # Dimensiones de los embeddings activos (768 para Gemini, 1024 para Cohere v3)
    EMBEDDING_DIMENSIONS: int = 768
    COHERE_EMBEDDING_DIMENSIONS: int = 1024
    LLM_TIMEOUT_SECONDS: int = 30
    LLM_MAX_RETRIES: int = 1

    # Vector Store — DT-02
    VECTORSTORE_PROVIDER: str = "memory"    # "memory" | "chroma"
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # Almacenamiento de objetos — DT-07, REQ-18
    STORAGE_PROVIDER: str = "mock"      # "mock" (disco local) | "oci"
    MOCK_STORAGE_DIR: str = "./data/mock_oci"
    OCI_CONFIG_FILE: str = "~/.oci/config"
    OCI_PROFILE: str = "DEFAULT"
    OCI_BUCKET_NAME: str = "nuevamente-g10"
    OCI_NAMESPACE: str | None = None

    # Persistencia de sesión — DT-08
    DATABASE_URL: str = "sqlite:///./data/sqlite/nuevamente.db"

    model_config = SettingsConfigDict(
        env_file=PROJECT_ROOT / ".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @model_validator(mode="after")
    def validate_chunking(self) -> Self:
        """El overlap debe ser menor que el tamaño del chunk."""
        if self.CHUNK_OVERLAP >= self.CHUNK_SIZE:
            raise ValueError("CHUNK_OVERLAP debe ser menor que CHUNK_SIZE")
        if self.MAX_FILE_SIZE_MB <= 0:
            raise ValueError("MAX_FILE_SIZE_MB debe ser positivo")
        return self

    @model_validator(mode="after")
    def validate_ai_providers(self) -> Self:
        """Verifica que existan las API Keys según los proveedores activos."""
        provider_llm = self.LLM_PROVIDER.lower()
        provider_emb = self.EMBEDDING_PROVIDER.lower()

        # Validación para Gemini
        if provider_llm == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError("LLM_PROVIDER='gemini' requiere GEMINI_API_KEY en .env o variables de entorno")
        if provider_emb == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError("EMBEDDING_PROVIDER='gemini' requiere GEMINI_API_KEY en .env o variables de entorno")

        # Validación para Cohere
        if provider_llm == "cohere" and not self.COHERE_API_KEY:
            raise ValueError("LLM_PROVIDER='cohere' requiere COHERE_API_KEY en .env o variables de entorno")
        if provider_emb == "cohere" and not self.COHERE_API_KEY:
            raise ValueError("EMBEDDING_PROVIDER='cohere' requiere COHERE_API_KEY en .env o variables de entorno")
        if provider_emb == "cohere":
            if self.COHERE_EMBEDDING_DIMENSIONS <= 0:
                raise ValueError("COHERE_EMBEDDING_DIMENSIONS debe ser positivo")
            if (
                self.COHERE_EMBEDDING_MODEL == "embed-multilingual-v3.0"
                and self.COHERE_EMBEDDING_DIMENSIONS not in {256, 512, 1024}
            ):
                raise ValueError(
                    "COHERE_EMBEDDING_DIMENSIONS debe ser 256, 512 o 1024 "
                    "para embed-multilingual-v3.0"
                )

        return self

    @property
    def active_embedding_dimensions(self) -> int:
        """Dimensión efectiva del proveedor usado para indexar y consultar."""
        if self.EMBEDDING_PROVIDER.lower() == "cohere":
            return self.COHERE_EMBEDDING_DIMENSIONS
        return self.EMBEDDING_DIMENSIONS

    def resolve_path(self, value: str) -> Path:
        """Convierte una ruta de configuración en absoluta."""
        path = Path(value).expanduser()
        return path if path.is_absolute() else PROJECT_ROOT / path

    @property
    def sqlite_path(self) -> Path:
        """Ruta del archivo SQLite extraída de `DATABASE_URL`."""
        if not self.DATABASE_URL.startswith(_SQLITE_PREFIX):
            raise ValueError("DATABASE_URL debe tener la forma sqlite:///ruta/archivo.db")
        return self.resolve_path(self.DATABASE_URL[len(_SQLITE_PREFIX):])


@lru_cache
def get_settings() -> Settings:
    """Devuelve la configuración cacheada (se lee el `.env` una sola vez)."""
    return Settings()