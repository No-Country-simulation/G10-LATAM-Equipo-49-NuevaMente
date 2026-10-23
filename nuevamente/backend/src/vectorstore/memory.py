"""VectorStore en memoria — implementación del `Protocol VectorStore`
para desarrollo/tests sin ChromaDB (DT-02). Persistencia en RAM del
proceso; misma interfaz que la implementación real futura.
"""
import math
import threading
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
    """Cumple `Protocol VectorStore` guardando vectores en un diccionario. La
    query devuelve los `top_k` más cercanos por similaridad coseno,
    opcionalmente filtrados por `doc_id`."""

    def __init__(self):
        self._chunks: dict[str, dict] = {}
        # *********************************************************************
        #  MEJORA AUD-008 — 2026-10-15
        #  Los endpoints síncronos y las BackgroundTasks de FastAPI corren en un
        #  pool de hilos; `add` mutaba el dict mientras `query` lo recorría y
        #  producía `RuntimeError: dictionary changed size during iteration`
        #  (196 errores / 4 s en la reproducción). Un `RLock` serializa el acceso.
        # *********************************************************************
        self._lock = threading.RLock()

    def add(
        self,
        doc_id: str,
        chunk_ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
        documents: list[str],
    ) -> None:
        # *********************************************************************
        #  MEJORA AUD-014a — 2026-10-15
        #  Antes `zip` truncaba al mínimo sin error: se podían indexar 2 vectores
        #  para 3 chunks y perder chunks en silencio. Ahora se validan las
        #  longitudes y `zip(..., strict=True)` garantiza la correspondencia.
        # *********************************************************************
        lengths = {len(chunk_ids), len(vectors), len(metadatas), len(documents)}
        if len(lengths) != 1:
            raise ValueError(
                "chunk_ids, vectors, metadatas y documents deben tener la misma longitud."
            )
        with self._lock:
            for cid, vec, meta, doc in zip(
                chunk_ids, vectors, metadatas, documents, strict=True
            ):
                # MEJORA AUD-013 — se conserva la metadata completa (no solo page).
                self._chunks[cid] = {
                    "doc_id": doc_id,
                    "vector": vec,
                    "text": doc,
                    "meta": dict(meta or {}),
                }

    def query(
        self,
        query_vector: list[float],
        top_k: int,
        doc_id: str | None = None,
    ) -> list[VectorStoreMatch]:
        # Se itera sobre una copia tomada bajo lock: así una escritura
        # concurrente no modifica el diccionario durante el recorrido.
        with self._lock:
            items = list(self._chunks.items())
        scored: list[tuple[float, dict]] = []
        for cid, entry in items:
            if doc_id and entry["doc_id"] != doc_id:
                continue
            scored.append(
                (_cosine(query_vector, entry["vector"]), {**entry, "chunk_id": cid})
            )
        scored.sort(key=lambda t: t[0], reverse=True)
        return [
            InMemoryMatch(
                chunk_id=m["chunk_id"],
                text=m["text"],
                score=s,
                page=(m["meta"] or {}).get("page"),
            )
            for s, m in scored[:top_k]
        ]

    def count(self, doc_id: str | None = None) -> int:
        """Cantidad de chunks indexados, opcionalmente de un `doc_id`.

        Permite distinguir un índice vacío (fallo técnico) de un índice con
        chunks que no superan el umbral de similitud (regla de negocio).
        """
        with self._lock:
            if doc_id is None:
                return len(self._chunks)
            return sum(1 for meta in self._chunks.values() if meta["doc_id"] == doc_id)

    def delete(self, doc_id: str) -> None:
        """Elimina todos los vectores de `doc_id` (idempotente) — AUD-013/004."""
        with self._lock:
            for cid in [c for c, meta in self._chunks.items() if meta["doc_id"] == doc_id]:
                del self._chunks[cid]


def _cosine(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = math.sqrt(sum(x * x for x in a)) or 1.0
    nb = math.sqrt(sum(y * y for y in b)) or 1.0
    return dot / (na * nb)
