"""Contrato del servicio de retrieval (COMP-05)."""
from typing import Protocol

from src.vectorstore.base import VectorStoreMatch


class RetrievalService(Protocol):
    """Recupera el contexto relevante para una solicitud de adaptación."""

    def retrieve(
        self,
        doc_id: str,
        perfil: str,
        nicho: str | None = None,
        tema: str | None = None,
    ) -> list[VectorStoreMatch]:
        """Construye la query desde `perfil`/`nicho`/`tema` y recupera el
        top-k de chunks relevantes (`settings.RETRIEVAL_TOP_K`).

        Implementación futura.
        """
        ...

