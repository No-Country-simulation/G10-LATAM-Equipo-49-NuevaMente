from src.embeddings.provider_mock import MockEmbeddingProvider
from src.embeddings.embed_chunks import embed_chunks
from src.processing.models import DocumentChunk


def test_mock_embeddings_are_deterministic():
    provider = MockEmbeddingProvider()
    v1 = provider.embed_query("texto de prueba")
    v2 = provider.embed_query("texto de prueba")
    assert v1 == v2


def test_embed_chunks_matches_chunk_count():
    chunks = [
        DocumentChunk(id="1", doc_id="d1", text="a" * 10, position=0, char_start=0, char_end=10),
        DocumentChunk(id="2", doc_id="d1", text="b" * 10, position=1, char_start=10, char_end=20),
    ]
    vectors = embed_chunks(chunks, MockEmbeddingProvider())
    assert len(vectors) == len(chunks)


def test_embed_chunks_empty_list_returns_empty():
    assert embed_chunks([], MockEmbeddingProvider()) == []
