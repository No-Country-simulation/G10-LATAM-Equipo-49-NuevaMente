"""VectorStore en memoria — implementación del `Protocol VectorStore`
para desarrollo/tests sin ChromaDB (DT-02). Persistencia en RAM del
proceso; misma interfaz que la implementación real futura.
"""
import math
from dataclasses import dataclass

from src.vectorstore.base import VectorStoreMatch


@dataclass
class InMemoryMatch:
    """Forma concreta de `vectorstore.base.VectorStoreMatch` para la
    implementación en memoria (los `Protocol` no son instanciables)."""

    chunk_id: str
    text: str
    score: float
    page: int | None = None


class InMemoryVectorStore:
    """Cumple `Protocol VectorStore` guardando vectores en listas. La
    query devuelve los `top_k` más cercanos por similaridad coseno,
    opcionalmente filtrados por `doc_id`."""

    def __init__(self):
        self._chunks: dict[str, dict] = {}

    def add(
        self,
        doc_id: str,
        chunk_ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
        documents: list[str],
    ) -> None:
        for cid, vec, meta, doc in zip(chunk_ids, vectors, metadatas, documents):
            self._chunks[cid] = {
                "doc_id": doc_id,
                "vector": vec,
                "text": doc,
                "page": meta.get("page"),
            }

    def query(
        self,
        query_vector: list[float],
        top_k: int,
        doc_id: str | None = None,
    ) -> list[VectorStoreMatch]:
        scored: list[tuple[float, dict]] = []
        for cid, meta in self._chunks.items():
            if doc_id and meta["doc_id"] != doc_id:
                continue
            scored.append((_cosine(query_vector, meta["vector"]), {**meta, "chunk_id": cid}))
        scored.sort(key=lambda t: t[0], reverse=True)
        return [
            InMemoryMatch(
                chunk_id=m["chunk_id"],
                text=m["text"],
                score=s,
                page=m["page"],
            )
            for s, m in scored[:top_k]
        ]

    def count(self, doc_id: str | None = None) -> int:
        """Cantidad de chunks indexados, opcionalmente de un `doc_id`.

        Permite distinguir un índice vacío (fallo técnico) de un índice con
        chunks que no superan el umbral de similitud (regla de negocio).
        """
        if doc_id is None:
            return len(self._chunks)
        return sum(1 for meta in self._chunks.values() if meta["doc_id"] == doc_id)


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)
