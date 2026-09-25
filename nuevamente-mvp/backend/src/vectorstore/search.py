from dataclasses import dataclass
from src.vectorstore.client import get_collection


@dataclass
class RetrievedChunk:
    chunk_id: str
    text: str
    page: int | None
    section: str | None
    distance: float


def search(document_id: str, query_embedding: list[float], top_k: int) -> list[RetrievedChunk]:
    collection = get_collection()
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
        where={"doc_id": document_id},  # nunca cruzar documentos distintos
    )

    if not results["ids"] or not results["ids"][0]:
        return []

    retrieved = []
    for i, chunk_id in enumerate(results["ids"][0]):
        meta = results["metadatas"][0][i]
        retrieved.append(
            RetrievedChunk(
                chunk_id=chunk_id,
                text=results["documents"][0][i],
                page=meta.get("page") or None,
                section=meta.get("section") or None,
                distance=results["distances"][0][i],
            )
        )
    return retrieved
