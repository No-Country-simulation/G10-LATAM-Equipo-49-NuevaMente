"""Tests del proveedor de embeddings real Gemini (DT-09).

Valida el contrato sin llamadas de red: usa un fake inyectado para
`google.genai.Client` y verifica lotes, orden, reintentos y traducción
de errores.
"""
import pytest

from src.core.config import get_settings
from src.core.exceptions import LLMProviderError
from src.embeddings.factory import get_embedding_provider
from src.embeddings.providers.gemini import GeminiEmbeddingProvider


class FakeGenAIClient:
    """Fake del cliente `google.genai.Client` para tests deterministas."""

    def __init__(self, *, fail_after: int = -1):
        self._call_count = 0
        self._fail_after = fail_after  # -1 = never fail, 0 = fail first call, etc.
        self.last_contents: list[str] = []

        # models es un atributo con embed_content method
        class Models:
            def __init__(self, outer):
                self._outer = outer

            def embed_content(self, model: str, contents: list[str]):
                self._outer._call_count += 1
                self._outer.last_contents = contents

                if self._outer._call_count > self._outer._fail_after >= 0:
                    from google.genai import errors
                    raise errors.APIError("Simulated API failure")

                class FakeEmbedding:
                    def __init__(self, values: list[float]):
                        self.values = values

                class FakeResponse:
                    def __init__(self, embeddings: list[FakeEmbedding]):
                        self.embeddings = embeddings

                # Genera embeddings deterministas: vector unitario en dimensiones 0..len-1
                embeddings = []
                for i, _ in enumerate(contents):
                    vec = [0.0] * 768
                    vec[i % 768] = 1.0
                    embeddings.append(FakeEmbedding(vec))
                return FakeResponse(embeddings)

        self.models = Models(self)


@pytest.fixture
def fake_client():
    return FakeGenAIClient()


@pytest.fixture
def provider(fake_client, monkeypatch):
    """Provider con cliente fake inyectado."""
    p = GeminiEmbeddingProvider(api_key="test-key")
    # Inyecta el fake evitando la importación real
    monkeypatch.setattr(p, "_get_client", lambda: fake_client)
    return p


# --------------------------------------------------------------------- contratos

def test_embed_documents_conserva_orden_y_longitud(provider):
    """Mismo número de vectores que textos, en el mismo orden."""
    texts = ["primero", "segundo", "tercero"]
    vectors = provider.embed_documents(texts)
    assert len(vectors) == 3
    # Cada vector es unitario en una dimensión distinta según su índice
    for i, vec in enumerate(vectors):
        assert vec[i % 768] == 1.0
        assert sum(v for v in vec if v != 1.0) == 0.0


def test_embed_query_delega_en_embed_documents(provider):
    """`embed_query` llama a `embed_documents([text])` y devuelve el primero."""
    vec = provider.embed_query("consulta")
    assert len(vec) == 768
    assert vec[0] == 1.0


def test_lotes_de_100_textos(provider, fake_client):
    """Lotes mayores a 100 se procesan en múltiples llamadas a la API."""
    texts = [f"texto {i}" for i in range(250)]
    vectors = provider.embed_documents(texts)
    assert len(vectors) == 250
    # 250 textos -> 3 llamadas (100, 100, 50)
    assert fake_client._call_count == 3


def test_reintento_con_backoff_exitoso(provider, monkeypatch):
    """Si falla una vez y luego tiene éxito, reintenta y devuelve resultado."""
    # Cliente simple que falla la primera vez y luego tiene éxito
    class FlakyClient:
        def __init__(self):
            self._call_count = 0
            self._fail_first = True
            self.last_contents: list[str] = []

            class Models:
                def __init__(self, outer):
                    self._outer = outer

                def embed_content(self, model: str, contents: list[str]):
                    self._outer._call_count += 1
                    self._outer.last_contents = contents

                    if self._outer._fail_first:
                        self._outer._fail_first = False
                        from google.genai import errors
                        raise errors.APIError("Simulated API failure")

                    class FakeEmbedding:
                        def __init__(self, values: list[float]):
                            self.values = values

                    class FakeResponse:
                        def __init__(self, embeddings: list[FakeEmbedding]):
                            self.embeddings = embeddings

                    embeddings = []
                    for i, _ in enumerate(contents):
                        vec = [0.0] * 768
                        vec[i % 768] = 1.0
                        embeddings.append(FakeEmbedding(vec))
                    return FakeResponse(embeddings)

            self.models = Models(self)

    client = FlakyClient()
    monkeypatch.setattr(provider, "_get_client", lambda: client)

    texts = ["a", "b"]
    vectors = provider.embed_documents(texts)
    assert len(vectors) == 2
    assert client._call_count == 2


def test_reintento_agotado_lanza_llmprovidererror(provider, monkeypatch):
    """Si todos los reintentos fallan, lanza LLMProviderError."""
    client = FakeGenAIClient(fail_after=0)  # falla siempre
    monkeypatch.setattr(provider, "_get_client", lambda: client)

    with pytest.raises(LLMProviderError, match="Fallo al generar embeddings"):
        provider.embed_documents(["test"])


def test_lista_vacia_devuelve_lista_vacia(provider):
    assert provider.embed_documents([]) == []

# ---------------------------------------------------------------------- factory


def test_factory_devuelve_gemini(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    # Limpia el cache del factory y settings
    get_embedding_provider.cache_clear()
    get_settings.cache_clear()

    prov = get_embedding_provider()
    assert type(prov).__name__ == "GeminiEmbeddingProvider"