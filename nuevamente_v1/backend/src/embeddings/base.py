"""Contrato del proveedor de embeddings (COMP-03).

Fuente: instrucciones de arquitectura + DT-09 (Gemini propuesto, 🔴
bloqueante — proveedor no confirmado formalmente por el equipo, ver Plan
Técnico Fase 10/20). Cualquier proveedor concreto (Gemini, mock, u otro)
debe implementar este `Protocol` para que el resto del pipeline (COMP-04,
COMP-05) sea independiente del proveedor (RNF-005).
"""
from typing import Protocol


class EmbeddingProvider(Protocol):
    """Genera vectores de embedding para texto."""

    def embed_documents(self, texts: list[str]) -> list[list[float]]:
        """Genera un vector por cada texto de `texts`, en el mismo orden.

        Implementación futura.
        """
        ...

    def embed_query(self, text: str) -> list[float]:
        """Genera el vector de una consulta individual (para retrieval).

        Implementación futura.
        """
        ...
