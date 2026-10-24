"""Selector de proveedor de LLM según configuración (DT-09).

Permite intercambiar Cohere, Gemini o Mock vía `settings.LLM_PROVIDER` sin
tocar el resto del pipeline (RNF-005).

Si `LLM_PROVIDER=cohere` y hay `GEMINI_API_KEY` configurada, se devuelve una
cadena de failover `FailoverLLMProvider(CohereLLMProvider, GeminiLLMProvider)`:
primero Cohere, si falla tras reintentos → Gemini, si ambos fallan → error
que se propaga como error del job. El modo mock solo se activa cuando se
configura explícitamente `LLM_PROVIDER=mock`.

CAMBIO H-02 INICIO — 2026-10-24
El fallo de los proveedores se propaga como error del job, no como contenido mock.
CAMBIO H-02 FIN — 2026-10-24
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
    if provider == "cohere":
        from src.generation.providers.cohere import CohereLLMProvider

        cohere_provider = CohereLLMProvider()
        # Cadena de failover: Cohere → Gemini (si hay GEMINI_API_KEY)
        if settings.GEMINI_API_KEY:
            from src.generation.failover import FailoverLLMProvider
            from src.generation.providers.gemini import GeminiLLMProvider

            return FailoverLLMProvider(
                primary=cohere_provider,
                backup=GeminiLLMProvider(),
            )
        return cohere_provider
    raise NuevaMenteError(
        f"LLM_PROVIDER inválido: {settings.LLM_PROVIDER!r}. "
        "Valores válidos: 'mock', 'gemini' o 'cohere'."
    )