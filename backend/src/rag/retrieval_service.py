"""Retrieval service (BE-RAG-009, COMP-05).

Combina `EmbeddingProvider.embed_query` + `VectorStore.query` para obtener
el contexto relevante a una solicitud de adaptación.
"""
from src.core.config import get_settings
from src.embeddings.factory import get_embedding_provider
from src.vectorstore.base import VectorStoreMatch
from src.vectorstore.memory import InMemoryVectorStore


class DefaultRetrievalService:
    """Implementación de `RetrievalService` sobre el vectorstore dado.

    Construye la query a partir de `perfil`/`nicho`/`tema` y recupera el
    top-k de chunks (`settings.RETRIEVAL_TOP_K`).
    """

    def __init__(self, store: InMemoryVectorStore | None = None, embedder=None):
        self._store = store or InMemoryVectorStore()
        self._embedder = embedder or get_embedding_provider()

    def retrieve(
        self,
        doc_id: str,
        perfil: str,
        nicho: str | None = None,
        tema: str | None = None,
    ) -> list[VectorStoreMatch]:
        settings = get_settings()
        query = " ".join(t for t in (perfil, nicho, tema) if t).strip()
        query = query or "general"
        vector = self._embedder.embed_query(query)
        return self._store.query(vector, settings.RETRIEVAL_TOP_K, doc_id=doc_id)