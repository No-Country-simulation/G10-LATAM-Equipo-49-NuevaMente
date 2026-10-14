"""Tests para `get_llm_provider` factory (DT-09)."""
import os

import pytest

from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError
from src.generation.factory import get_llm_provider
from src.generation.llm_provider import LLMProvider
from src.generation.providers.mock import MockLLMProvider


def test_factory_returns_mock_by_default():
    """Por defecto devuelve MockLLMProvider."""
    os.environ["LLM_PROVIDER"] = "mock"
    get_settings.cache_clear()

    client = get_llm_provider()
    assert isinstance(client, MockLLMProvider)
    assert isinstance(client, LLMProvider)


def test_factory_returns_gemini_provider():
    """`LLM_PROVIDER=gemini` devuelve GeminiLLMProvider."""
    os.environ["LLM_PROVIDER"] = "gemini"
    os.environ["GEMINI_API_KEY"] = "test-key"
    get_settings.cache_clear()

    from src.generation.factory import get_llm_provider
    get_llm_provider.cache_clear()

    client = get_llm_provider()
    assert client.__class__.__name__ == "GeminiLLMProvider"
    assert isinstance(client, LLMProvider)


def test_factory_returns_cohere_chain_with_fallback():
    """`LLM_PROVIDER=cohere` devuelve FailoverLLMProvider(Cohere, Gemini)."""
    os.environ["LLM_PROVIDER"] = "cohere"
    os.environ["COHERE_API_KEY"] = "test-cohere"
    os.environ["GEMINI_API_KEY"] = "test-gemini"
    get_settings.cache_clear()

    from src.generation.factory import get_llm_provider
    get_llm_provider.cache_clear()

    client = get_llm_provider()
    assert client.__class__.__name__ == "FailoverLLMProvider"
    assert isinstance(client, LLMProvider)


def test_factory_cohere_without_gemini_key_returns_single():
    """`LLM_PROVIDER=cohere` SIN GEMINI_API_KEY devuelve solo Cohere."""
    os.environ["LLM_PROVIDER"] = "cohere"
    os.environ["COHERE_API_KEY"] = "test-cohere"
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    get_settings.cache_clear()

    from src.generation.factory import get_llm_provider
    get_llm_provider.cache_clear()

    client = get_llm_provider()
    assert client.__class__.__name__ == "CohereLLMProvider"
    assert isinstance(client, LLMProvider)


def test_factory_rejects_unknown_provider():
    """Proveedor desconocido lanza NuevaMenteError."""
    os.environ["LLM_PROVIDER"] = "proveedor-inexistente"
    get_settings.cache_clear()

    with pytest.raises(NuevaMenteError, match="LLM_PROVIDER inválido"):
        get_llm_provider()


def test_factory_cohere_requires_api_key():
    """`LLM_PROVIDER=cohere` sin COHERE_API_KEY lanza ValueError."""
    os.environ["LLM_PROVIDER"] = "cohere"
    if "COHERE_API_KEY" in os.environ:
        del os.environ["COHERE_API_KEY"]
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="COHERE_API_KEY"):
        get_llm_provider()


def test_factory_gemini_requires_api_key():
    """`LLM_PROVIDER=gemini` sin GEMINI_API_KEY lanza ValueError."""
    os.environ["LLM_PROVIDER"] = "gemini"
    if "GEMINI_API_KEY" in os.environ:
        del os.environ["GEMINI_API_KEY"]
    get_settings.cache_clear()

    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        get_llm_provider()