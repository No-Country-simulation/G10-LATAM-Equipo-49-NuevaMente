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

# *****************************************************************************
#  MEJORA AUD-012 — 2026-10-15
#  Dimensión real del proveedor mock (debe coincidir con
#  `embeddings.providers.mock.DIM`). Se usa para nombrar la colección del
#  vector store con la dimensión efectiva, no con un valor configurado a mano.
# *****************************************************************************
MOCK_EMBEDDING_DIMENSIONS = 256


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
    # Dimensión del modelo de embeddings activo (gemini/cohere/mock).
    LLM_PROVIDER: str = "mock"          # "gemini" | "cohere" | "mock"
    EMBEDDING_PROVIDER: str = "mock"    # "gemini" | "cohere" | "mock"
    GEMINI_API_KEY: str | None = None
    # *********************************************************************
    #  MEJORA AUD-003 — 2026-10-15
    #  Los modelos por defecto anteriores (`gemini-2.5-flash`,
    #  `text-embedding-004`) fueron dados de baja según la documentación
    #  oficial de deprecaciones de Gemini. Se fijan IDs vigentes para que
    #  `EMBEDDING_PROVIDER=gemini` no falle "out of the box".
    # *********************************************************************
    GEMINI_MODEL: str = "gemini-3.8-flash"
    GEMINI_EMBEDDING_MODEL: str = "gemini-embedding-2"
    COHERE_API_KEY: str | None = None
    COHERE_MODEL: str = "command-r-plus"
    COHERE_EMBEDDING_MODEL: str = "embed-multilingual-v3.0"
    COHERE_EMBEDDING_DIMENSIONS: int = 1024
    COHERE_MAX_TOKENS: int = 4096

   
    # Dimensiones del modelo de embeddings activo (gemini/cohere).
    EMBEDDING_DIMENSIONS: int = 768 # dimensiones del modelo de embeddings activo (gemini/mock)
    LLM_TIMEOUT_SECONDS: int = 30       # Fase 14
    LLM_MAX_RETRIES: int = 1            # Fase 14

    # Vector Store — DT-02
    # *********************************************************************
    #  MEJORA AUD-007 — 2026-10-15
    #  El valor por defecto era `memory`: el índice vivía solo en RAM y se
    #  perdía en silencio al reiniciar (SQLite persistía, los vectores no).
    #  Ahora el defecto es un índice persistente (`chroma`); `memory` queda
    #  reservado para tests/desarrollo.
    # *********************************************************************
    VECTORSTORE_PROVIDER: str = "chroma"    # "memory" | "chroma"
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # Almacenamiento de objetos — DT-07, REQ-18
    STORAGE_PROVIDER: str = "mock"      # "mock" (disco local) | "oci"
    MOCK_STORAGE_DIR: str = "./data/mock_oci"
    OCI_CONFIG_FILE: str = "~/.oci/config"
    OCI_PROFILE: str = "DEFAULT"
    # *********************************************************************
    #  MEJORA AUD-021 — 2026-10-15
    #  El valor por defecto anterior (`nuevamente-g10`) era un bucket concreto
    #  y obsoleto; se usa un nombre genérico que el operador debe sobrescribir.
    # *********************************************************************
    OCI_BUCKET_NAME: str = "nuevamente-docs"
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
        """Si el proveedor es gemini o cohere, exige la API key correspondiente."""
        if self.LLM_PROVIDER.lower() == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError(
                "LLM_PROVIDER='gemini' requiere GEMINI_API_KEY en .env o variables de entorno"
            )
        if self.LLM_PROVIDER.lower() == "cohere" and not self.COHERE_API_KEY:
            raise ValueError(
                "LLM_PROVIDER='cohere' requiere COHERE_API_KEY en .env o variables de entorno"
            )
        if self.EMBEDDING_PROVIDER.lower() == "gemini" and not self.GEMINI_API_KEY:
            raise ValueError(
                "EMBEDDING_PROVIDER='gemini' requiere GEMINI_API_KEY en .env o variables de entorno"
            )
        if self.EMBEDDING_PROVIDER.lower() == "cohere" and not self.COHERE_API_KEY:
            raise ValueError(
                "EMBEDDING_PROVIDER='cohere' requiere COHERE_API_KEY en .env o variables de entorno"
            )
        if self.EMBEDDING_PROVIDER.lower() == "cohere":
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
        """Dimensión efectiva del proveedor usado para indexar y consultar.

        *********************************************************************
        MEJORA AUD-012 — 2026-10-15
        El proveedor mock tiene una dimensión fija real (256). Antes se
        devolvía `EMBEDDING_DIMENSIONS` (768), de modo que la colección se
        nombraba con una dimensión que no correspondía a los vectores
        almacenados y se mezclaban espacios vectoriales incompatibles.
        *********************************************************************
        """
        provider = self.EMBEDDING_PROVIDER.lower()
        if provider == "cohere":
            return self.COHERE_EMBEDDING_DIMENSIONS
        if provider == "mock":
            return MOCK_EMBEDDING_DIMENSIONS
        return self.EMBEDDING_DIMENSIONS

    @property
    def active_embedding_model(self) -> str:
        """Modelo de embeddings activo (para segregar la colección del índice).

        *********************************************************************
        MEJORA AUD-012 — 2026-10-15
        Cambiar de modelo de embeddings debe cambiar la colección del vector
        store; antes el nombre solo dependía del proveedor y la dimensión.
        *********************************************************************
        """
        provider = self.EMBEDDING_PROVIDER.lower()
        if provider == "gemini":
            return self.GEMINI_EMBEDDING_MODEL
        if provider == "cohere":
            return self.COHERE_EMBEDDING_MODEL
        return "hash-tf"

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