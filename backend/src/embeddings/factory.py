"""Selector de proveedor de embeddings según configuración (DT-09).

Permite intercambiar Gemini ↔ Mock vía `settings.EMBEDDING_PROVIDER` sin
tocar el resto del pipeline (RNF-005).
"""
from src.core.config import get_settings
from src.embeddings.base import EmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    """Devuelve la instancia de `EmbeddingProvider` según
    `settings.EMBEDDING_PROVIDER` ("gemini" | "mock")."""
    settings = get_settings()
    if settings.EMBEDDING_PROVIDER == "mock":
        from src.embeddings.providers.mock import MockEmbeddingProvider

        return MockEmbeddingProvider()
    if settings.EMBEDDING_PROVIDER == "gemini":
        from src.embeddings.providers.gemini import GeminiEmbeddingProvider

        return GeminiEmbeddingProvider()
    raise ValueError(f"EMBEDDING_PROVIDER desconocido: {settings.EMBEDDING_PROVIDER!r}")