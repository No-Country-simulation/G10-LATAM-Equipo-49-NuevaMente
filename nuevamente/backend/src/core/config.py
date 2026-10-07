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

    # RAG — BE-RAG-009/010 (pendiente: Semana 2)
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MIN_SCORE: float = 0.25

    # Validación de fidelidad — DT-11 (pendiente: Semana 3)
    FIDELITY_THRESHOLD: float = 0.90

    # Proveedores de IA — DT-09 (🔴 bloqueante, no confirmado formalmente)
    LLM_PROVIDER: str = "mock"          # "gemini" | "mock"
    EMBEDDING_PROVIDER: str = "mock"    # "gemini" | "mock"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    GEMINI_EMBEDDING_MODEL: str = "text-embedding-004"
    EMBEDDING_DIMENSIONS: int = 768     # dimensiones del modelo de embeddings activo
    LLM_TIMEOUT_SECONDS: int = 30       # Fase 14
    LLM_MAX_RETRIES: int = 1            # Fase 14

    # Vector Store — DT-02 (pendiente: Semana 2)
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
        """Si el proveedor es gemini, exige GEMINI_API_KEY."""
        if self.LLM_PROVIDER.lower() == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError(
                "LLM_PROVIDER='gemini' requiere GEMINI_API_KEY en .env o variables de entorno"
            )
        if self.EMBEDDING_PROVIDER.lower() == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError(
                "EMBEDDING_PROVIDER='gemini' requiere GEMINI_API_KEY en .env o variables de entorno"
            )
        return self

    def resolve_path(self, value: str) -> Path:
        """Convierte una ruta de configuración en absoluta.

        Las rutas relativas se interpretan desde la raíz del proyecto (no
        desde el directorio de trabajo), para que `data/` sea siempre el mismo.
        """
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