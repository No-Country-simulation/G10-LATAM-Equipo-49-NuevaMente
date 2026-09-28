"""Construcción de contexto para el LLM (BE-RAG-010) y regla NO_CONTEXT
(BE-RAG-011).

Regla de negocio crítica (Plan Técnico, RF-009 flujo alternativo): si el
score de los resultados de retrieval es insuficiente
(`settings.RETRIEVAL_MIN_SCORE`), el sistema NUNCA debe invocar al LLM de
generación libremente — debe cortar el flujo con `NoContextError` /
`status=NO_CONTEXT` antes de llegar a `generation/`.
"""
from src.vectorstore.base import VectorStoreMatch


def build_context(matches: list[VectorStoreMatch]) -> str:
    """Ensambla el texto de contexto que verá el LLM, referenciando
    `chunk_id` (y `page`, si existe) de cada match usado — necesario para
    `sources` en el contrato de salida (RNF-006).

    Lanza:
        NoContextError: si `matches` está vacío o ningún match supera
            `settings.RETRIEVAL_MIN_SCORE` (BE-RAG-011).

    Implementación futura.
    """
    ...
