"""Contrato del Vector Store (COMP-04).

Tecnología prevista: ChromaDB embebido (DT-02) — pero el resto del
pipeline (COMP-05) solo debe conocer este `Protocol`, no ChromaDB
directamente (RNF-005).
"""
from typing import Protocol


class VectorStoreMatch(Protocol):
    """Resultado de una búsqueda por similitud (forma mínima esperada)."""

    chunk_id: str
    text: str
    score: float
    page: int | None


class VectorStore(Protocol):
    """Persiste embeddings + metadata y responde búsquedas por similitud."""

    def add(
        self,
        doc_id: str,
        chunk_ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
        documents: list[str],
    ) -> None:
        """Agrega o actualiza los vectores de un documento en la colección.

        Implementación futura.
        """
        ...

    def query(
        self,
        query_vector: list[float],
        top_k: int,
        doc_id: str | None = None,
    ) -> list[VectorStoreMatch]:
        """Devuelve hasta `top_k` chunks más similares a `query_vector`,
        opcionalmente filtrados por `doc_id`.

        Implementación futura.
        """
        ...
