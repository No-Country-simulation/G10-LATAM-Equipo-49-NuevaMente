"""Tests del Vector Store con ChromaDB (DT-02).

Valida persistencia, query por similitud, filtrado por doc_id y
segregación de colecciones por proveedor+dimensión.
"""
import pytest

from src.core.config import get_settings
from src.processing.models import DocumentChunk
from src.vectorstore.client import get_chroma_client, get_chroma_collection
from src.vectorstore.factory import get_vectorstore
from src.vectorstore.store import persist_chunks


@pytest.fixture
def chroma_settings(monkeypatch, tmp_path):
    """Configura entorno para ChromaDB con directorio temporal."""
    monkeypatch.setenv("VECTORSTORE_PROVIDER", "chroma")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "768")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    get_settings.cache_clear()
    get_vectorstore.cache_clear()
    get_chroma_client.cache_clear()
    get_chroma_collection.cache_clear()

    yield
    get_settings.cache_clear()
    get_vectorstore.cache_clear()
    get_chroma_client.cache_clear()
    get_chroma_collection.cache_clear()
    get_chroma_collection.cache_clear()


def _chunks(doc_id: str, texts: list[str], pages: list[int | None] | None = None):
    """Helper para crear DocumentChunks de prueba."""
    if pages is None:
        pages = [None] * len(texts)
    return [
        DocumentChunk(
            id=f"{doc_id}_chunk_{i}",
            doc_id=doc_id,
            text=t,
            position=i,
            page=p,
            section=None,
            char_start=0,
            char_end=len(t),
        )
        for i, (t, p) in enumerate(zip(texts, pages))
    ]


def test_chroma_add_y_query(chroma_settings):
    """Agrega chunks y los recupera por similitud."""
    store = get_vectorstore()
    doc_id = "doc_test_1"

    chunks = _chunks(doc_id, ["texto uno", "texto dos", "texto tres"], [1, 2, 3])
    # Vectores simples: cada uno unitario en dimensión distinta
    vectors = [[0.0] * 768 for _ in chunks]
    for i, vec in enumerate(vectors):
        vec[i] = 1.0

    persist_chunks(chunks, vectors, store)

    # Query con vector similar al primer chunk
    query_vec = [0.0] * 768
    query_vec[0] = 1.0
    matches = store.query(query_vec, top_k=2, doc_id=doc_id)

    assert len(matches) == 2
    assert matches[0].chunk_id == f"{doc_id}_chunk_0"
    assert matches[0].score > 0.99  # coseno ~1
    assert matches[0].page == 1


def test_chroma_filtra_por_doc_id(chroma_settings):
    """Solo devuelve matches del doc_id solicitado."""
    store = get_vectorstore()

    chunks_a = _chunks("doc_a", ["aaa"])
    vectors_a = [[1.0] + [0.0] * 767]

    chunks_b = _chunks("doc_b", ["bbb"])
    vectors_b = [[1.0] + [0.0] * 767]

    persist_chunks(chunks_a, vectors_a, store)
    persist_chunks(chunks_b, vectors_b, store)

    query_vec = [1.0] + [0.0] * 767
    matches_a = store.query(query_vec, top_k=5, doc_id="doc_a")
    matches_b = store.query(query_vec, top_k=5, doc_id="doc_b")

    assert len(matches_a) == 1
    assert matches_a[0].chunk_id == "doc_a_chunk_0"
    assert len(matches_b) == 1
    assert matches_b[0].chunk_id == "doc_b_chunk_0"


def test_chroma_count(chroma_settings):
    """`count()` devuelve el número correcto de chunks."""
    store = get_vectorstore()

    assert store.count() == 0
    assert store.count("doc_x") == 0

    chunks = _chunks("doc_x", ["a", "b"])
    vectors = [[1.0] + [0.0] * 767, [0.0, 1.0] + [0.0] * 766]
    persist_chunks(chunks, vectors, store)

    assert store.count() == 2
    assert store.count("doc_x") == 2
    assert store.count("doc_y") == 0


def test_chroma_persistencia_entre_instancias(chroma_settings, tmp_path):
    """La colección sobrevive a cache_clear y nueva instancia."""
    store = get_vectorstore()
    chunks = _chunks("doc_persist", ["persistente"])
    vectors = [[1.0] + [0.0] * 767]
    persist_chunks(chunks, vectors, store)

    # Fuerza nueva instancia limpiando el cache
    get_vectorstore.cache_clear()
    get_chroma_collection.cache_clear()

    store2 = get_vectorstore()
    assert store2.count("doc_persist") == 1

    matches = store2.query([1.0] + [0.0] * 767, top_k=1, doc_id="doc_persist")
    assert len(matches) == 1
    assert matches[0].chunk_id == "doc_persist_chunk_0"


def test_chroma_coleccion_segregada_por_dimensiones(monkeypatch, tmp_path):
    """Cambiar EMBEDDING_DIMENSIONS crea colección distinta (no rompe)."""
    # Primera configuración: 768 dims
    monkeypatch.setenv("VECTORSTORE_PROVIDER", "chroma")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma2"))
    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "768")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")

    get_settings.cache_clear()
    get_vectorstore.cache_clear()
    get_chroma_collection.cache_clear()

    store_768 = get_vectorstore()
    chunks = _chunks("dim_test", ["test"])
    vectors = [[1.0] + [0.0] * 767]
    persist_chunks(chunks, vectors, store_768)

    # Segunda configuración: 256 dims (mock)
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "256")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "mock")
    get_settings.cache_clear()
    get_vectorstore.cache_clear()
    get_chroma_collection.cache_clear()

    store_256 = get_vectorstore()
    chunks2 = _chunks("dim_test2", ["test2"])
    vectors2 = [[1.0] + [0.0] * 255]
    persist_chunks(chunks2, vectors2, store_256)

    # Ambas colecciones existen y son independientes
    assert store_768.count("dim_test") == 1
    assert store_256.count("dim_test2") == 1
    # store_256 no ve los datos de 768
    assert store_256.count("dim_test") == 0


def test_chroma_upsert_reindexa_sin_error(chroma_settings):
    """Reindexar el mismo doc_id con upsert no lanza DuplicateIDError."""
    store = get_vectorstore()
    doc_id = "doc_upsert"

    chunks = _chunks(doc_id, ["v1"])
    vectors = [[1.0] + [0.0] * 767]
    persist_chunks(chunks, vectors, store)

    # Reindexar con contenido distinto
    chunks2 = _chunks(doc_id, ["v2"])
    vectors2 = [[0.0, 1.0] + [0.0] * 766]
    persist_chunks(chunks2, vectors2, store)  # no debe lanzar

    matches = store.query([0.0, 1.0] + [0.0] * 766, top_k=1, doc_id=doc_id)
    assert matches[0].text == "v2"