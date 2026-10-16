"""Persistencia de embeddings en el Vector Store (BE-RAG-007)."""
from dataclasses import dataclass

from src.core.exceptions import VectorStoreError
from src.processing.models import DocumentChunk
from src.vectorstore.base import VectorStore, VectorStoreMatch
from src.vectorstore.client import get_chroma_collection


@dataclass
class ChromaMatch:
    """Forma concreta de `VectorStoreMatch` para ChromaDB."""

    chunk_id: str
    text: str
    score: float
    page: int | None = None


class ChromaVectorStore:
    """Implementación de `VectorStore` sobre ChromaDB embebido."""

    def __init__(self) -> None:
        self._collection = get_chroma_collection()

    def add(
        self,
        doc_id: str,
        chunk_ids: list[str],
        vectors: list[list[float]],
        metadatas: list[dict],
        documents: list[str],
    ) -> None:
        """Agrega o actualiza los vectores de un documento en la colección.

        Usa `upsert` para permitir reindexar sin `DuplicateIDError`.
        """
        # ChromaDB espera metadatas con valores simples (str, int, float, bool, None)
        clean_metadatas = []
        for meta in metadatas:
            clean = {}
            for k, v in meta.items():
                if v is None:
                    continue
                if isinstance(v, (str, int, float, bool)):
                    clean[k] = v
                else:
                    clean[k] = str(v)
            clean["doc_id"] = doc_id
            clean_metadatas.append(clean)

        self._collection.upsert(
            ids=chunk_ids,
            embeddings=vectors,
            metadatas=clean_metadatas,
            documents=documents,
        )

    def query(
        self,
        query_vector: list[float],
        top_k: int,
        doc_id: str | None = None,
    ) -> list[VectorStoreMatch]:
        """Devuelve hasta `top_k` chunks más similares a `query_vector`.

        ChromaDB devuelve distancia coseno (0 = idéntico, 2 = opuesto).
        Convertimos a score = 1 - distance para que 1.0 sea coincidencia perfecta.
        """
        where = {"doc_id": doc_id} if doc_id else None
        results = self._collection.query(
            query_embeddings=[query_vector],
            n_results=top_k,
            where=where,
            include=["metadatas", "documents", "distances"],
        )

        matches: list[ChromaMatch] = []
        if results["ids"] and results["ids"][0]:
            for chunk_id, text, distance, meta in zip(
                results["ids"][0],
                results["documents"][0],
                results["distances"][0],
                results["metadatas"][0],
            ):
                score = 1.0 - distance
                matches.append(
                    ChromaMatch(
                        chunk_id=chunk_id,
                        text=text,
                        score=score,
                        page=meta.get("page"),
                    )
                )
        return matches

    def count(self, doc_id: str | None = None) -> int:
        """Cantidad de chunks indexados, opcionalmente filtrados por `doc_id`."""
        if doc_id is None:
            return self._collection.count()
        results = self._collection.get(where={"doc_id": doc_id}, include=[])
        return len(results["ids"]) if results["ids"] else 0

    # *********************************************************************
    #  MEJORA AUD-013 / AUD-004 — 2026-10-15
    #  `delete` permite compensar una ingesta fallida y limpiar los vectores
    #  de un documento (el Protocol ya lo declara).
    # *********************************************************************
    def delete(self, doc_id: str) -> None:
        """Elimina todos los vectores de `doc_id` (idempotente)."""
        try:
            self._collection.delete(where={"doc_id": doc_id})
        except Exception as exc:
            raise VectorStoreError(
                f"No fue posible eliminar los vectores del documento: {exc}"
            ) from exc


def persist_chunks(
    chunks: list[DocumentChunk],
    vectors: list[list[float]],
    store: VectorStore,
) -> None:
    """Empaqueta `chunks` + `vectors` y los persiste vía `store.add(...)`.

    *********************************************************************
    MEJORA AUD-013 — 2026-10-15
    Antes solo se guardaba `{"page": ...}`; ahora se persisten también
    `position`, `section`, `char_start` y `char_end`, de modo que el índice
    permite reconstruir orden y sección y no solo la página.

    MEJORA AUD-022b — 2026-10-15
    Un fallo de persistencia en el índice vectorial se reporta como
    `VectorStoreError`, no como `NuevaMenteError` genérico.

    Lanza:
        VectorStoreError: si la persistencia falla.
    *********************************************************************
    """
    if not chunks:
        return
    try:
        doc_id = chunks[0].doc_id
        chunk_ids = [chunk.id for chunk in chunks]
        metadatas = [
            {
                "page": chunk.page,
                "position": chunk.position,
                "section": chunk.section,
                "char_start": chunk.char_start,
                "char_end": chunk.char_end,
            }
            for chunk in chunks
        ]
        documents = [chunk.text for chunk in chunks]
        store.add(doc_id, chunk_ids, vectors, metadatas, documents)
    except Exception as exc:
        raise VectorStoreError(f"Fallo al persistir chunks en el vectorstore: {exc}") from exc