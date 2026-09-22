from app.config import settings
from app.providers.interfaces import LLMProvider
from app.providers.gemini_provider import GeminiProvider
from app.providers.mock_provider import MockProvider


def create_llm_provider() -> LLMProvider:

    if settings.LLM_PROVIDER == "gemini":
        return GeminiProvider()

    if settings.LLM_PROVIDER == "mock":
        return MockProvider()

    raise ValueError(
        f"Proveedor LLM desconocido: "
        f"{settings.LLM_PROVIDER}"
    )