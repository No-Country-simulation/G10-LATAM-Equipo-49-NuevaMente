"""Retrieval service (BE-RAG-009, COMP-05).

Combina `EmbeddingProvider.embed_query` + `VectorStore.query` para obtener
el contexto relevante a una solicitud de adaptación.
"""
from src.vectorstore.base import VectorStoreMatch


class DefaultRetrievalService:
    """Implementación futura de `RetrievalService`."""

    def retrieve(
        self,
        doc_id: str,
        perfil: str,
        nicho: str | None = None,
        tema: str | None = None,
    ) -> list[VectorStoreMatch]:
        ...
