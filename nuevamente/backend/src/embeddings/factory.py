"""Selector de proveedor de embeddings según configuración (DT-09).

Permite intercambiar Gemini ↔ Mock vía `settings.EMBEDDING_PROVIDER` sin
tocar el resto del pipeline (RNF-005).
"""
from src.embeddings.base import EmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    """Devuelve la instancia de `EmbeddingProvider` según
    `settings.EMBEDDING_PROVIDER` ("gemini" | "mock").

    Implementación futura.
    """
    ...

