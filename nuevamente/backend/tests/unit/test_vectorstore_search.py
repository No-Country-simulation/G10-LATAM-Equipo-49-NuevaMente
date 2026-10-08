"""Tests de `vectorstore/search.py::similarity_search` (BE-RAG-008, OUT-005).

El helper delega en `store.query`, aplica el umbral `RETRIEVAL_MIN_SCORE`
y convierte fallos del store en `StorageError`.
"""
import pytest

from src.core.config import get_settings
from src.core.exceptions import NoContextError, NuevaMenteError, StorageError
from src.vectorstore.memory import InMemoryMatch, InMemoryVectorStore
from src.vectorstore.search import similarity_search


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


class _FallaStore:
    """Simula un vectorstore que rompe la consulta."""

    def __init__(self, exc: Exception):
        self.exc = exc

    def add(self, *args, **kwargs) -> None:
        pass

    def query(self, *args, **kwargs):
        raise self.exc


# ------------------------------------------------------------------ delegación


def test_delega_a_store_query_con_los_argumentos():
    store = _SpyStore([InMemoryMatch(chunk_id="c1", text="t", score=0.9)])

    similarity_search([1.0, 0.0], store, top_k=3, doc_id="doc_1")

    assert store.calls == [{"vector": [1.0, 0.0], "top_k": 3, "doc_id": "doc_1"}]


def test_devuelve_match_que_supera_el_umbral():
    store = _SpyStore([InMemoryMatch(chunk_id="c1", text="t", score=0.9)])

    assert len(similarity_search([1.0, 0.0], store, top_k=5)) == 1


# ------------------------------------------------------------------- umbral


def test_filtra_los_scores_bajo_el_umbral():
    """Los chunks que no alcanzan RETRIEVAL_MIN_SCORE no vuelven."""
    store = _SpyStore(
        [
            InMemoryMatch(chunk_id="alto", text="a", score=0.9),
            InMemoryMatch(chunk_id="bajo", text="b", score=0.01),
        ]
    )

    resultados = similarity_search([1.0, 0.0], store, top_k=5)

    assert [m.chunk_id for m in resultados] == ["alto"]


def test_un_score_justo_en_el_umbral_se_mantiene():
    store = _SpyStore(
        [InMemoryMatch(chunk_id="limite", text="t", score=get_settings().RETRIEVAL_MIN_SCORE)]
    )

    assert len(similarity_search([1.0, 0.0], store, top_k=5)) == 1


def test_si_todo_queda_bajo_el_umbral_devuelve_vacio():
    store = _SpyStore([InMemoryMatch(chunk_id="x", text="t", score=0.0)])

    assert similarity_search([1.0, 0.0], store, top_k=5) == []


# ------------------------------------------------------------------ normalización


def test_store_que_devuelve_none_se_normaliza_a_lista_vacia():
    """El stub `ChromaVectorStore.query` devuelve None: se convierte en []."""
    store = _SpyStore(None)

    assert similarity_search([1.0, 0.0], store, top_k=5) == []


def test_store_vacio_devuelve_lista_vacia():
    store = _SpyStore([])

    assert similarity_search([1.0, 0.0], store, top_k=5) == []


# -------------------------------------------------------------------- OUT-005


def test_fallo_del_store_se_convierte_en_storage_error():
    store = _FallaStore(RuntimeError("colección corrrupta"))

    with pytest.raises(StorageError, match="búsqueda por similitud"):
        similarity_search([1.0, 0.0], store, top_k=5)


def test_fallo_del_store_conserva_la_causa():
    cause = ValueError("vector dimensión inválida")
    store = _FallaStore(cause)

    with pytest.raises(StorageError) as exc_info:
        similarity_search([1.0, 0.0], store, top_k=5)

    assert exc_info.value.__cause__ is cause


def test_error_de_dominio_del_store_no_se_re_envelopa():
    """Un error ya tipado (NuevaMenteError) debe propagarse sin perder su code."""
    store = _FallaStore(NoContextError("sin contexto"))

    with pytest.raises(NoContextError):
        similarity_search([1.0, 0.0], store, top_k=5)


def test_otro_nueva_mente_error_se_propaga_tal_cual():
    class _CustomError(NuevaMenteError):
        pass

    store = _FallaStore(_CustomError("config inválida"))

    with pytest.raises(_CustomError):
        similarity_search([1.0, 0.0], store, top_k=5)


# ---------------------------------------------------------- integración simple


def test_end_to_end_con_store_en_memoria():
    """Store real + umbral: solo sobreviven los chunks sobre RETRIEVAL_MIN_SCORE."""
    store = InMemoryVectorStore()
    store.add(
        doc_id="doc_1",
        chunk_ids=["c1", "c2"],
        vectors=[[1.0, 0.0], [0.0, 1.0]],
        metadatas=[{"page": 1}, {"page": 2}],
        documents=["idéntico", "opuesto"],
    )

    resultados = similarity_search([1.0, 0.0], store, top_k=5, doc_id="doc_1")

    assert [m.chunk_id for m in resultados] == ["c1"]