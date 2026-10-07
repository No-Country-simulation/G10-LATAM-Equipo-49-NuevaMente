"""Selección del Vector Store según `VECTORSTORE_PROVIDER` (RNF-005, DT-02)."""
from functools import lru_cache

from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError
from src.vectorstore.base import VectorStore


@lru_cache
def get_vectorstore() -> VectorStore:
    """Devuelve el Vector Store según `settings.VECTORSTORE_PROVIDER`.

    La instancia está cacheada a propósito: la ingesta y el retrieval deben
    operar sobre el MISMO store durante la vida del proceso. Los tests que
    necesiten aislar el estado deben llamar a `get_vectorstore.cache_clear()`.

    Lanza:
        NuevaMenteError: si el proveedor no es conocido o no está implementado.
    """
    settings = get_settings()
    provider = settings.VECTORSTORE_PROVIDER.lower()
    if provider == "memory":
        from src.vectorstore.memory import InMemoryVectorStore

        return InMemoryVectorStore()
    if provider == "chroma":
        raise NuevaMenteError(
            "VECTORSTORE_PROVIDER='chroma' todavía no está implementado (DT-02). "
            "Usá 'memory' por ahora."
        )
    raise NuevaMenteError(
        f"VECTORSTORE_PROVIDER inválido: {settings.VECTORSTORE_PROVIDER!r}. "
        "Valores válidos: 'memory' o 'chroma'."
    )
