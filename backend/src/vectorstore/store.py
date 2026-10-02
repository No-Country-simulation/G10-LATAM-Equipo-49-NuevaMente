"""Persistencia de embeddings en el Vector Store (BE-RAG-007)."""
from src.processing.models import DocumentChunk
from src.vectorstore.base import VectorStore


class ChromaVectorStore:
    """Implementación futura de `VectorStore` sobre ChromaDB embebido."""

    def add(
        self,
        doc_id: str,
        chunk_ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
        documents: list[str],
    ) -> None:
        ...

    def query(self, query_vector: list[float], top_k: int, doc_id: str | None = None):
        ...


def persist_chunks(
    chunks: list[DocumentChunk],
    vectors: list[list[float]],
    store: VectorStore,
) -> None:
    """Empaqueta `chunks` + `vectors` y los persiste vía `store.add(...)`.

    Implementación futura.
    """
    ...
