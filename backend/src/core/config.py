"""Configuración declarativa del sistema (FND-003).

Contrato: define QUÉ variables de entorno necesita el sistema y sus valores
por defecto. NO ejecuta la carga real del .env en tiempo de importación
(eso es implementación futura, a cargo de quien construya `get_settings()`).

Fuente: Plan Técnico, Fase 6 ("Variables de configuración") y Fase 7
(FND-003, EPIC-01).
"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Esquema de configuración de la aplicación.

    Cada campo corresponde a una variable declarada en `.env.example`.
    No se instancia ni se carga automáticamente en este archivo: la carga
    real (lectura de `.env`, cacheo) es responsabilidad de
    `get_settings()`, todavía sin implementar.
    """

    APP_NAME: str = "NuevaMente"
    ENVIRONMENT: str = "development"

    # Ingesta — DT-12 (RF-001, ING-005)
    MAX_FILE_SIZE_MB: int = 10

    # Processing — TASK-002 (RF-005)
    CHUNK_SIZE: int = 800
    CHUNK_OVERLAP: int = 150

    # RAG — BE-RAG-009/010
    RETRIEVAL_TOP_K: int = 5
    RETRIEVAL_MIN_SCORE: float = 0.25

    # Validación de fidelidad — DT-11
    FIDELITY_THRESHOLD: float = 0.90

    # Proveedores de IA — DT-09 (🔴 bloqueante, no confirmado formalmente)
    LLM_PROVIDER: str = "mock"          # "gemini" | "mock"
    EMBEDDING_PROVIDER: str = "mock"    # "gemini" | "mock"
    GEMINI_API_KEY: str | None = None
    GEMINI_MODEL: str | None = None
    GEMINI_EMBEDDING_MODEL: str | None = None
    LLM_TIMEOUT_SECONDS: int = 30       # Fase 14
    LLM_MAX_RETRIES: int = 1            # Fase 14

    # Vector Store — DT-02
    CHROMA_PERSIST_DIR: str = "./data/chroma"

    # OCI Object Storage — DT-07, REQ-18
    OCI_CONFIG_FILE: str = "~/.oci/config"
    OCI_PROFILE: str = "DEFAULT"
    OCI_BUCKET_NAME: str = "nuevamente-g10"
    OCI_NAMESPACE: str | None = None

    # Persistencia de sesión — DT-08
    DATABASE_URL: str = "sqlite:///./data/sqlite/nuevamente.db"

    model_config = SettingsConfigDict(
        env_file="../.env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


def get_settings() -> Settings:
    """Contrato de acceso a la configuración cacheada.

    Implementación futura: debe cachear la instancia (p. ej. `lru_cache`)
    para no releer el `.env` en cada llamada. No se implementa aquí — este
    archivo es CONTRACT-ONLY.
    """
    ...
