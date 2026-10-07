"""Tests de `rag/retrieval_service.py` (BE-RAG-009, COMP-05).

El servicio combina embedder + vectorstore. Se testea con espías para
verificar la query que se construye y los argumentos que se reenvían, más
un test de integración con las implementaciones reales (mock + memoria).
"""
from src.core.config import get_settings
from src.rag.retrieval_service import DefaultRetrievalService
from src.vectorstore.memory import InMemoryMatch, InMemoryVectorStore


class _SpyEmbedder:
    """Registra las queries y devuelve un vector trivial."""

    def __init__(self):
        self.queries: list[str] = []

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        return [[0.0] for _ in texts]

    def embed_query(self, text: str) -> list[float]:
        self.queries.append(text)
        return [1.0, 0.0]


class _SpyStore:
    """Registra los argumentos de `query` y devuelve un resultado fijo."""

    def __init__(self, result=None):
        self.result = result if result is not None else []
        self.calls: list[dict] = []

    def add(self, *args, **kwargs) -> None:
        pass

    def query(self, query_vector, top_k, doc_id=None):
        self.calls.append({"vector": query_vector, "top_k": top_k, "doc_id": doc_id})
        return self.result


# ------------------------------------------------------------------- contrato


def test_devuelve_lo_que_devuelve_el_store():
    esperado = [InMemoryMatch(chunk_id="c1", text="t", score=0.9)]
    service = DefaultRetrievalService(store=_SpyStore(esperado), embedder=_SpyEmbedder())

    assert service.retrieve(doc_id="doc_1", perfil="docente") == esperado


def test_reenvia_el_doc_id_al_store():
    store = _SpyStore()
    service = DefaultRetrievalService(store=store, embedder=_SpyEmbedder())

    service.retrieve(doc_id="doc_42", perfil="docente")

    assert store.calls[0]["doc_id"] == "doc_42"


def test_usa_retrieval_top_k_de_la_configuracion():
    store = _SpyStore()
    service = DefaultRetrievalService(store=store, embedder=_SpyEmbedder())

    service.retrieve(doc_id="doc_1", perfil="docente")

    assert store.calls[0]["top_k"] == get_settings().RETRIEVAL_TOP_K


# ---------------------------------------------------------------------- query


def test_query_combina_perfil_nicho_y_tema():
    embedder = _SpyEmbedder()
    service = DefaultRetrievalService(store=_SpyStore(), embedder=embedder)

    service.retrieve(doc_id="doc_1", perfil="docente", nicho="ansiedad", tema="sueño")

    assert embedder.queries == ["docente ansiedad sueño"]


def test_query_omite_las_partes_nulas():
    embedder = _SpyEmbedder()
    service = DefaultRetrievalService(store=_SpyStore(), embedder=embedder)

    service.retrieve(doc_id="doc_1", perfil="docente")

    assert embedder.queries == ["docente"]


def test_query_sin_datos_usa_general():
    embedder = _SpyEmbedder()
    service = DefaultRetrievalService(store=_SpyStore(), embedder=embedder)

    service.retrieve(doc_id="doc_1", perfil="")

    assert embedder.queries == ["general"]


def test_el_vector_del_embedder_llega_al_store():
    store = _SpyStore()
    service = DefaultRetrievalService(store=store, embedder=_SpyEmbedder())

    service.retrieve(doc_id="doc_1", perfil="docente")

    assert store.calls[0]["vector"] == [1.0, 0.0]


# ------------------------------------------------------------- integración


def test_retrieval_end_to_end_con_mock_y_memoria():
    """Embedder mock + store en memoria: el chunk que comparte token con la
    query debe quedar primero."""
    from src.embeddings.providers.mock import MockEmbeddingProvider

    store = InMemoryVectorStore()
    embedder = MockEmbeddingProvider()
    textos = [
        "contenido sobre ansiedad",
        "contenido sobre sueño",
        "receta de cocina",
    ]
    store.add(
        doc_id="doc_1",
        chunk_ids=["c1", "c2", "c3"],
        vectors=embedder.embed_documents(textos),
        metadatas=[{"page": 1}, {"page": 2}, {"page": 3}],
        documents=textos,
    )
    service = DefaultRetrievalService(store=store, embedder=embedder)

    matches = service.retrieve(doc_id="doc_1", perfil="", tema="ansiedad")

    assert matches[0].chunk_id == "c1"
    assert matches[0].page == 1


def test_fallo_del_store_se_convierte_en_storage_error():
    """El cableado hacia similarity_search hace que un fallo del store
    llegue como StorageError (OUT-005), no crudo."""
    from src.core.exceptions import StorageError

    class _BrokenStore:
        def add(self, *args, **kwargs) -> None:
            pass

        def query(self, *args, **kwargs):
            raise RuntimeError("colección no inicializada")

    service = DefaultRetrievalService(store=_BrokenStore(), embedder=_SpyEmbedder())

    import pytest

    with pytest.raises(StorageError):
        service.retrieve(doc_id="doc_1", perfil="docente")
