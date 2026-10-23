"""Test de integración: flujo completo chunks → embeddings → ChromaDB (BE-RAG-007)."""
import os

from src.embeddings.embed_chunks import embed_chunks
from src.embeddings.factory import get_embedding_provider
from src.ingestion.models import PageText
from src.processing.chunking import chunk_text
from src.vectorstore.factory import get_vectorstore
from src.vectorstore.search import similarity_search
from src.vectorstore.store import persist_chunks


def _make_chunks(doc_id: str, text: str) -> list:
    """Crea chunks a partir de texto usando el chunker real."""
    pages = [PageText(page=i + 1, text=text) for i in range(10)]
    chunks = chunk_text(text, doc_id, pages)
    return chunks


def test_chunks_to_embeddings_to_chroma_persists_and_searches(tmp_path):
    """Flujo e2e: chunk → embed → persist → search."""
    # 1. Texto de prueba con contenido distinguible
    text = (
        "La inteligencia artificial transforma la educación. "
        "Los modelos de lenguaje generan texto coherente. "
        "La búsqueda semántica encuentra documentos relevantes. "
        "El chunking divide el texto en fragmentos manejables. "
        "Los embeddings capturan significado semántico. "
    )

    doc_id = "test_doc_e2e"

    # 2. Chunking
    chunks = _make_chunks(doc_id, text)
    assert len(chunks) >= 1, "El chunker debe producir al menos un chunk"

    # 3. Embeddings (usar mock para test determinista y rápido)
    os.environ["EMBEDDING_PROVIDER"] = "mock"
    from src.core.config import get_settings
    from src.embeddings.factory import get_embedding_provider as gefp
    get_settings.cache_clear()
    gefp.cache_clear()

    provider = get_embedding_provider()
    vectors = embed_chunks(chunks, provider)

    assert len(vectors) == len(chunks)
    assert all(len(v) > 0 for v in vectors)

    # 4. Persistencia en ChromaDB
    os.environ["VECTORSTORE_PROVIDER"] = "chroma"
    os.environ["CHROMA_PERSIST_DIR"] = str(tmp_path / "chroma")
    from src.vectorstore.factory import get_vectorstore as gvs
    gvs.cache_clear()

    store = get_vectorstore()
    persist_chunks(chunks, vectors, store)

    # 5. Búsqueda semántica (similarity_search)
    query_vector = vectors[0]  # usar el primer vector como query
    matches = similarity_search(
        query_vector, store, top_k=3, doc_id=doc_id
    )

    assert len(matches) >= 1, "La búsqueda debe devolver al menos un match"
    # Los matches ya vienen filtrados por doc_id en el store
    # El primer match debe ser el más similar (el mismo chunk)
    assert matches[0].chunk_id == chunks[0].id
    # Verificar que los matches tienen los campos esperados
    for m in matches:
        assert hasattr(m, "chunk_id")
        assert hasattr(m, "score")
        assert hasattr(m, "text")


def test_chroma_collection_named_by_provider_and_dimensions(tmp_path):
    """La colección de Chroma se nombra según proveedor y dimensiones."""
    os.environ["VECTORSTORE_PROVIDER"] = "chroma"
    os.environ["CHROMA_PERSIST_DIR"] = str(tmp_path / "chroma")
    os.environ["EMBEDDING_PROVIDER"] = "mock"
    os.environ["EMBEDDING_DIMENSIONS"] = "256"

    from src.core.config import get_settings
    from src.vectorstore.client import _collection_name

    get_settings.cache_clear()

    settings = get_settings()

    # El nombre de la colección debe incluir provider y dimensiones
    collection_name = _collection_name(settings)
    assert "mock" in collection_name
    assert "256" in collection_name


def test_chunks_with_different_providers_use_separate_collections(tmp_path):
    """Chroma aísla colecciones por proveedor y dimensiones."""
    import os
    os.environ["VECTORSTORE_PROVIDER"] = "chroma"

    # Provider mock (256 dims)
    os.environ["EMBEDDING_PROVIDER"] = "mock"
    os.environ["EMBEDDING_DIMENSIONS"] = "256"
    os.environ["CHROMA_PERSIST_DIR"] = str(tmp_path / "chroma_mock")

    from src.core.config import get_settings
    from src.vectorstore.client import _collection_name

    get_settings.cache_clear()

    settings = get_settings()
    mock_name = _collection_name(settings)

    # Provider gemini (768 dims)
    os.environ["GEMINI_API_KEY"] = "test-key"
    os.environ["EMBEDDING_PROVIDER"] = "gemini"
    os.environ["EMBEDDING_DIMENSIONS"] = "768"
    os.environ["CHROMA_PERSIST_DIR"] = str(tmp_path / "chroma_gemini")

    get_settings.cache_clear()

    settings2 = get_settings()
    gemini_name = _collection_name(settings2)

    # Los nombres deben ser distintos
    assert mock_name != gemini_name
    assert "mock" in mock_name
    assert "256" in mock_name
    assert "gemini" in gemini_name
    assert "768" in gemini_name