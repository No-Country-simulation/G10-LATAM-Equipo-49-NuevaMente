"""Búsqueda por similitud (BE-RAG-008, OUT-005)."""
from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError, StorageError
from src.vectorstore.base import VectorStore, VectorStoreMatch


def similarity_search(
    query_vector: list[float],
    store: VectorStore,
    top_k: int,
    doc_id: str | None = None,
) -> list[VectorStoreMatch]:
    """Ejecuta `store.query(...)`, aplica el umbral de `RETRIEVAL_MIN_SCORE`
    y normaliza el resultado.

    Solo devuelve los chunks cuya score alcanza `settings.RETRIEVAL_MIN_SCORE`;
    así la regla NO_CONTEXT (RF-009) se decide por umbral, cualquiera sea el
    proveedor del vectorstore (`memory` o `chroma`).

    Lanza:
        StorageError: si el Vector Store no está disponible o la colección no
            existe (OUT-005 — manejo de error).
    """
    try:
        resultados = store.query(query_vector, top_k, doc_id=doc_id)
    except NuevaMenteError:
        raise
    except Exception as exc:
        raise StorageError(
            f"No fue posible ejecutar la búsqueda por similitud: {exc}"
        ) from exc

    settings = get_settings()
    return [m for m in (resultados or []) if m.score >= settings.RETRIEVAL_MIN_SCORE]

__all__ = ["similarity_search"]
