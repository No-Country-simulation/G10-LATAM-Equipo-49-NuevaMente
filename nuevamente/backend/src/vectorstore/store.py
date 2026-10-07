"""Persistencia de embeddings en el Vector Store (BE-RAG-007)."""
from src.core.exceptions import NuevaMenteError
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

    Lanza:
        NuevaMenteError: si la persistencia falla.
    """
    if not chunks:
        return
    try:
        doc_id = chunks[0].doc_id
        chunk_ids = [chunk.id for chunk in chunks]
        metadatas = [{"page": chunk.page} for chunk in chunks]
        documents = [chunk.text for chunk in chunks]
        store.add(doc_id, chunk_ids, vectors, metadatas, documents)
    except Exception as exc:
        raise NuevaMenteError(f"Fallo al persistir chunks en el vectorstore: {exc}") from exc