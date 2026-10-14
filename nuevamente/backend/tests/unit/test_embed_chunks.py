"""Tests para `embeddings.embed_chunks` (BE-RAG-005)."""
import pytest

from src.core.exceptions import NuevaMenteError
from src.embeddings.base import EmbeddingProvider
from src.embeddings.embed_chunks import embed_chunks
from src.processing.models import DocumentChunk


class _MockProvider(EmbeddingProvider):
    """Proveedor mock que devuelve vectores fijos por longitud de texto."""

    def __init__(self, dim: int = 4) -> None:
        self.dim = dim

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[float(len(t))] * self.dim for t in texts]

    def embed_query(self, text: str) -> list[float]:
        return [float(len(text))] * self.dim


class _FailingProvider(EmbeddingProvider):
    """Proveedor que siempre falla."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        raise RuntimeError("proveedor caído")

    def embed_query(self, text: str) -> list[float]:
        raise RuntimeError("proveedor caído")


def _chunk(
    chunk_id: str,
    doc_id: str,
    text: str,
    position: int,
    page: int = 1,
    section: str | None = None,
    char_start: int = 0,
) -> DocumentChunk:
    """Helper para crear chunks válidos con campos obligatorios."""
    return DocumentChunk(
        id=chunk_id,
        doc_id=doc_id,
        text=text,
        position=position,
        section=section,
        page=page,
        char_start=char_start,
        char_end=char_start + len(text),
    )


def test_embed_chunks_returns_one_vector_per_chunk():
    chunks = [
        _chunk("c1", "d1", "hola mundo", 0, page=1, section="intro"),
        _chunk("c2", "d1", "segundo fragmento", 1, page=1, section="body"),
        _chunk("c3", "d1", "tercero", 2, page=2, section="body"),
    ]
    provider = _MockProvider(dim=4)

    vectors = embed_chunks(chunks, provider)

    assert len(vectors) == 3
    assert all(len(v) == 4 for v in vectors)
    assert vectors[0] == [10.0, 10.0, 10.0, 10.0]
    assert vectors[1] == [17.0, 17.0, 17.0, 17.0]  # "segundo fragmento" = 17
    assert vectors[2] == [7.0, 7.0, 7.0, 7.0]


def test_embed_chunks_preserves_order():
    """Los vectores salen en el mismo orden que los chunks de entrada."""
    chunks = [
        _chunk("c1", "d1", "a", 0, page=1),
        _chunk("c2", "d1", "bb", 1, page=1),
        _chunk("c3", "d1", "ccc", 2, page=1),
    ]
    provider = _MockProvider(dim=2)

    vectors = embed_chunks(chunks, provider)

    assert vectors[0] == [1.0, 1.0]
    assert vectors[1] == [2.0, 2.0]
    assert vectors[2] == [3.0, 3.0]


def test_embed_chunks_empty_list():
    provider = _MockProvider(dim=3)
    vectors = embed_chunks([], provider)
    assert vectors == []


def test_embed_chunks_propagates_provider_error():
    chunks = [
        _chunk("c1", "d1", "hola", 0, page=1),
    ]
    provider = _FailingProvider()

    with pytest.raises(NuevaMenteError, match="Fallo al generar embeddings"):
        embed_chunks(chunks, provider)


def test_embed_chunks_single_chunk():
    chunks = [
        _chunk("c1", "d1", "un solo chunk", 0, page=1, section="intro"),
    ]
    provider = _MockProvider(dim=5)

    vectors = embed_chunks(chunks, provider)

    assert len(vectors) == 1
    assert len(vectors[0]) == 5
    assert vectors[0] == [13.0] * 5