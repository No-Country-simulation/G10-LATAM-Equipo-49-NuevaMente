"""Búsqueda por similitud (BE-RAG-008, OUT-005)."""
from src.vectorstore.base import VectorStore, VectorStoreMatch


def similarity_search(
    query_vector: list[float],
    store: VectorStore,
    top_k: int,
    doc_id: str | None = None,
) -> list[VectorStoreMatch]:
    """Ejecuta `store.query(...)` y normaliza el resultado.

    Lanza:
        StorageError (o una excepción más específica a definir): si el
        Vector Store no está disponible o la colección no existe
        (OUT-005 — manejo de error).

    Implementación futura.
    """
    ...
