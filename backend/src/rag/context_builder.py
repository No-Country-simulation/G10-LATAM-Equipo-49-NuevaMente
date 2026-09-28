"""Construcción de contexto para el LLM (BE-RAG-010) y regla NO_CONTEXT
(BE-RAG-011).

Regla de negocio crítica (Plan Técnico, RF-009 flujo alternativo): si el
score de los resultados de retrieval es insuficiente
(`settings.RETRIEVAL_MIN_SCORE`), el sistema NUNCA invoca al LLM de
generación libremente — corta con `NoContextError`.

En el modo mock determinista (sin embeddings reales) los scores de
similaridad coseno son siempre positivos, por lo que la regla NO_CONTEXT
solo se dispara si `matches` está vacío.
"""
from src.core.config import get_settings
from src.core.exceptions import NoContextError
from src.vectorstore.base import VectorStoreMatch


def build_context(matches: list[VectorStoreMatch]) -> str:
    """Ensambla el texto de contexto que verá el LLM, referenciando
    `chunk_id` (y `page`, si existe) de cada match usado (RNF-006).

    Lanza `NoContextError` si `matches` está vacío o ningún match supera
    `settings.RETRIEVAL_MIN_SCORE`."""
    settings = get_settings()
    relevantes = [m for m in matches if m.score >= settings.RETRIEVAL_MIN_SCORE]
    if not relevantes:
        raise NoContextError(
            "No se encontró contexto suficiente para la solicitud (regla NO_CONTEXT)"
        )
    return "\n\n".join(
        f"[{m.chunk_id}{f' (p.{m.page})' if m.page else ''}] {m.text}" for m in relevantes
    )