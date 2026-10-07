"""Tests del Vector Store en memoria y de su factory.

Cubre la mecánica que el RAG (paso 3) va a consumir: similitud coseno,
`top_k`, filtro por `doc_id`, y el `count()` que permite distinguir un
índice vacío de uno sin coincidencias relevantes.
"""
import pytest

from src.core.exceptions import NuevaMenteError
from src.vectorstore.factory import get_vectorstore
from src.vectorstore.memory import InMemoryMatch, InMemoryVectorStore


@pytest.fixture
def store():
    return InMemoryVectorStore()


def _add(store, doc_id, chunk_ids, vectors, pages=None):
    store.add(
        doc_id=doc_id,
        chunk_ids=chunk_ids,
        vectors=vectors,
        metadatas=[{"page": p} for p in (pages or [None] * len(chunk_ids))],
        documents=[f"texto de {cid}" for cid in chunk_ids],
    )


# ------------------------------------------------------------------ add/query


def test_query_devuelve_los_top_k_mas_similares(store):
    """Ordena por similitud coseno descendente y respeta `top_k`."""
    _add(
        store,
        "doc_1",
        ["c1", "c2", "c3"],
        [[1.0, 0.0], [0.9, 0.1], [0.0, 1.0]],
    )
    result = store.query([1.0, 0.0], top_k=2)

    assert [m.chunk_id for m in result] == ["c1", "c2"]
    assert result[0].score > result[1].score


def test_vector_identico_da_score_uno(store):
    _add(store, "doc_1", ["c1"], [[3.0, 4.0]])
    result = store.query([3.0, 4.0], top_k=1)

    assert isinstance(result[0], InMemoryMatch)
    assert result[0].score == pytest.approx(1.0)


def test_filtro_por_doc_id_excluye_otros_documentos(store):
    _add(store, "doc_1", ["c1"], [[1.0, 0.0]])
    _add(store, "doc_2", ["c2"], [[1.0, 0.0]])

    result = store.query([1.0, 0.0], top_k=10, doc_id="doc_2")

    assert [m.chunk_id for m in result] == ["c2"]


def test_query_sin_filtro_mezcla_documentos(store):
    _add(store, "doc_1", ["c1"], [[1.0, 0.0]])
    _add(store, "doc_2", ["c2"], [[0.0, 1.0]])

    result = store.query([1.0, 0.0], top_k=10)

    assert {m.chunk_id for m in result} == {"c1", "c2"}


def test_query_en_store_vacio_devuelve_lista_vacia(store):
    assert store.query([1.0, 0.0], top_k=5) == []


def test_query_con_doc_id_inexistente_devuelve_lista_vacia(store):
    _add(store, "doc_1", ["c1"], [[1.0, 0.0]])
    assert store.query([1.0, 0.0], top_k=5, doc_id="doc_999") == []


def test_la_page_se_propaga_desde_la_metadata(store):
    _add(store, "doc_1", ["c1"], [[1.0, 0.0]], pages=[7])
    assert store.query([1.0, 0.0], top_k=1)[0].page == 7


def test_add_sobrescribe_el_mismo_chunk_id(store):
    _add(store, "doc_1", ["c1"], [[1.0, 0.0]])
    _add(store, "doc_1", ["c1"], [[0.0, 1.0]])

    assert store.count() == 1
    assert store.query([0.0, 1.0], top_k=1)[0].score == pytest.approx(1.0)


# --------------------------------------------------------------------- count


def test_count_total_y_por_documento(store):
    _add(store, "doc_1", ["c1", "c2"], [[1.0, 0.0], [0.0, 1.0]])
    _add(store, "doc_2", ["c3"], [[1.0, 0.0]])

    assert store.count() == 3
    assert store.count(doc_id="doc_1") == 2
    assert store.count(doc_id="doc_2") == 1


def test_count_de_documento_no_indexado_es_cero(store):
    assert store.count(doc_id="doc_inexistente") == 0


# ------------------------------------------------------------------- factory


def test_factory_devuelve_memory_por_defecto():
    assert isinstance(get_vectorstore(), InMemoryVectorStore)


def test_factory_acepta_mayusculas(monkeypatch):
    monkeypatch.setenv("VECTORSTORE_PROVIDER", "MEMORY")
    get_vectorstore.cache_clear()
    assert isinstance(get_vectorstore(), InMemoryVectorStore)


def test_factory_es_singleton(monkeypatch):
    """Ingesta y retrieval deben compartir la MISMA instancia."""
    get_vectorstore.cache_clear()
    assert get_vectorstore() is get_vectorstore()


def test_factory_rechaza_proveedor_desconocido(monkeypatch):
    monkeypatch.setenv("VECTORSTORE_PROVIDER", "pinecone")
    get_vectorstore.cache_clear()
    with pytest.raises(NuevaMenteError, match="VECTORSTORE_PROVIDER"):
        get_vectorstore()


def test_factory_chroma_implementado(monkeypatch, tmp_path):
    """`chroma` ahora está implementado (DT-02) y devuelve ChromaVectorStore."""
    monkeypatch.setenv("VECTORSTORE_PROVIDER", "chroma")
    monkeypatch.setenv("CHROMA_PERSIST_DIR", str(tmp_path / "chroma"))
    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setenv("EMBEDDING_DIMENSIONS", "768")
    monkeypatch.setenv("GEMINI_API_KEY", "fake-key")
    get_vectorstore.cache_clear()

    from src.vectorstore.store import ChromaVectorStore
    store = get_vectorstore()
    assert isinstance(store, ChromaVectorStore)
