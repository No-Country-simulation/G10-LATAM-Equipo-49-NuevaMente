"""Construcción de contexto para el LLM (BE-RAG-010) y regla NO_CONTEXT
(BE-RAG-011).

Regla de negocio crítica (Plan Técnico, RF-009 flujo alternativo): si el
score de los resultados de retrieval es insuficiente
(`settings.RETRIEVAL_MIN_SCORE`), el sistema NUNCA debe invocar al LLM de
generación libremente — debe cortar el flujo con `NoContextError` /
`status=NO_CONTEXT` antes de llegar a `generation/`.
"""
from src.core.config import get_settings
from src.core.exceptions import NoContextError
from src.vectorstore.base import VectorStoreMatch


def _reference(match: VectorStoreMatch) -> str:
    """Etiqueta de trazabilidad de un chunk: `[chunk_id]` o `[chunk_id (p.N)]`."""
    if match.page is not None:
        return f"[{match.chunk_id} (p.{match.page})]"
    return f"[{match.chunk_id}]"


def build_context(matches: list[VectorStoreMatch]) -> str:
    """Ensambla el texto de contexto que verá el LLM, referenciando
    `chunk_id` (y `page`, si existe) de cada match usado — necesario para
    `sources` en el contrato de salida (RNF-006).

    Lanza:
        NoContextError: si `matches` está vacío o ningún match supera
            `settings.RETRIEVAL_MIN_SCORE` (BE-RAG-011).
    """
    settings = get_settings()
    relevantes = [m for m in matches if m.score >= settings.RETRIEVAL_MIN_SCORE]
    if not relevantes:
        raise NoContextError(
            "No se encontró contexto suficiente para la solicitud (regla NO_CONTEXT)"
        )
    return "\n\n".join(f"{_reference(m)} {m.text}" for m in relevantes)
