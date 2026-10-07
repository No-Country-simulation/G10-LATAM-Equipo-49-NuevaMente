"""Selector de proveedor de embeddings según configuración (DT-09).

Permite intercambiar Gemini ↔ Mock vía `settings.EMBEDDING_PROVIDER` sin
tocar el resto del pipeline (RNF-005).
"""
from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError
from src.embeddings.base import EmbeddingProvider


def get_embedding_provider() -> EmbeddingProvider:
    """Devuelve el `EmbeddingProvider` según `settings.EMBEDDING_PROVIDER`.

    Lanza:
        NuevaMenteError: si el valor no es un proveedor conocido.
    """
    settings = get_settings()
    provider = settings.EMBEDDING_PROVIDER.lower()
    if provider == "mock":
        from src.embeddings.providers.mock import MockEmbeddingProvider

        return MockEmbeddingProvider()
    if provider == "gemini":
        from src.embeddings.providers.gemini import GeminiEmbeddingProvider

        return GeminiEmbeddingProvider()
    raise NuevaMenteError(
        f"EMBEDDING_PROVIDER inválido: {settings.EMBEDDING_PROVIDER!r}. "
        "Valores válidos: 'mock' o 'gemini'."
    )
