"""Tests para `CohereEmbeddingProvider` (BE-RAG-004).

Usa un cliente Cohere inyectado (fake) para validar el comportamiento sin
necesidad de credenciales reales ni red.
"""
import pytest

from src.core.exceptions import LLMProviderError


class _FakeCohereClient:
    """Cliente Cohere v2 falso que devuelve embeddings predecibles."""

    def __init__(self, dim: int = 1024, batch_size: int = 96):
        self.dim = dim
        self.batch_size = batch_size
        self.calls = []

    def embed(self, texts: list[str], model: str, input_type: str, embedding_types: list[str]):
        """Simula `co.embed()` devolviendo embeddings predecibles."""
        self.calls.append({
            "texts": texts,
            "model": model,
            "input_type": input_type,
            "embedding_types": embedding_types,
        })
        # Vector = [len(texto)] * dim (para que sea distinguible por texto)
        Embeddings = type(
            "Embeddings",
            (),
            {"float_": [[float(len(t))] * self.dim for t in texts]},
        )
        return type(
            "EmbedResponse",
            (),
            {"embeddings": Embeddings()},
        )()


class _FailingCohereClient:
    """Cliente que siempre falla."""

    def embed(self, *args, **kwargs):
        raise RuntimeError("Cohere API caído")


def _make_provider(client, dim: int = 1024):
    """Crea un CohereEmbeddingProvider inyectando un cliente fake."""
    from src.embeddings.providers.cohere import CohereEmbeddingProvider

    provider = CohereEmbeddingProvider.__new__(CohereEmbeddingProvider)
    provider._client = client
    provider._model = "embed-multilingual-v3.0"
    provider._max_retries = 1
    return provider


def test_embed_documents_returns_one_vector_per_text():
    """Un vector por cada texto de entrada, en el mismo orden."""
    client = _FakeCohereClient(dim=1024)
    provider = _make_provider(client)

    texts = ["hola", "segundo fragmento", "tercero"]
    vectors = provider.embed_documents(texts)

    assert len(vectors) == 3
    assert all(len(v) == 1024 for v in vectors)
    # El vector es [len(texto)] * dim
    assert vectors[0] == [4.0] * 1024
    assert vectors[1] == [17.0] * 1024
    assert vectors[2] == [7.0] * 1024


def test_embed_documents_batching_respects_limit():
    """Lotes de 96 textos (límite de `/v2/embed`)."""
    client = _FakeCohereClient(dim=1024, batch_size=96)
    provider = _make_provider(client)

    texts = [f"texto {i}" for i in range(200)]  # 3 lotes: 96, 96, 8
    vectors = provider.embed_documents(texts)

    assert len(vectors) == 200
    assert all(len(v) == 1024 for v in vectors)
    # Verificar que se hizo la llamada correcta (3 lotes)
    assert len(client.calls) == 3
    assert len(client.calls[0]["texts"]) == 96
    assert len(client.calls[1]["texts"]) == 96
    assert len(client.calls[2]["texts"]) == 8


def test_embed_documents_empty_list():
    """Lista vacía devuelve lista vacía."""
    client = _FakeCohereClient(dim=1024)
    provider = _make_provider(client)

    vectors = provider.embed_documents([])

    assert vectors == []


def test_embed_documents_uses_search_document():
    """`embed_documents` usa `input_type='search_document'`."""
    client = _FakeCohereClient()
    provider = _make_provider(client)

    provider.embed_documents(["hola"])

    assert client.calls[0]["input_type"] == "search_document"


def test_embed_query_uses_search_query():
    """`embed_query` usa `input_type='search_query'`."""
    client = _FakeCohereClient()
    provider = _make_provider(client)

    provider.embed_query("consulta de prueba")

    assert client.calls[0]["input_type"] == "search_query"


def test_embed_documents_propagates_error_after_retries():
    """Tras agotar reintentos, propaga LLMProviderError."""
    client = _FailingCohereClient()
    provider = _make_provider(client)

    with pytest.raises(LLMProviderError, match="Fallo al generar embeddings"):
        provider.embed_documents(["hola"])


def test_embed_documents_respects_model_and_params():
    """Pasa el modelo y parámetros correctos a la API."""
    client = _FakeCohereClient()
    provider = _make_provider(client)

    provider.embed_documents(["test"])

    call = client.calls[0]
    assert call["model"] == "embed-multilingual-v3.0"
    assert call["embedding_types"] == ["float"]