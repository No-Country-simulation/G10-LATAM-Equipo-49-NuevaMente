"""Selector de proveedor de LLM según configuración (DT-09).

Permite intercambiar Gemini ↔ Mock vía `settings.LLM_PROVIDER` sin
tocar el resto del pipeline (RNF-005).
"""
from functools import lru_cache

from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError
from src.generation.llm_provider import LLMProvider


@lru_cache
def get_llm_provider() -> LLMProvider:
    """Devuelve el `LLMProvider` según `settings.LLM_PROVIDER`.

    La instancia está cacheada a propósito: la ingesta y la generación
    deben operar sobre el MISMO proveedor durante la vida del proceso.
    Los tests que necesiten aislar el estado deben llamar a
    `get_llm_provider.cache_clear()`.

    Lanza:
        NuevaMenteError: si el valor no es un proveedor conocido.
    """
    settings = get_settings()
    provider = settings.LLM_PROVIDER.lower()
    if provider == "mock":
        from src.generation.providers.mock import MockLLMProvider

        return MockLLMProvider()
    if provider == "gemini":
        from src.generation.providers.gemini import GeminiLLMProvider

        return GeminiLLMProvider()
    raise NuevaMenteError(
        f"LLM_PROVIDER inválido: {settings.LLM_PROVIDER!r}. "
        "Valores válidos: 'mock' o 'gemini'."
    )