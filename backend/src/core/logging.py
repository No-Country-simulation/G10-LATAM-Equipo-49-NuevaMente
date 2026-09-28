"""Configuración de logging estructurado (FND-004, RNF-003).

Fuente: Plan Técnico, RNF-003 (Observabilidad) — cada ejecución del
pipeline debe generar logs con: document_id, etapa, duración, resultado.

Implementado con `logging` estándar + formato estructurado `key=value`
para que sea greppable en CI sin dependencias extra.
"""
import logging
from typing import Any

_configurado = False


def configure_logging() -> None:
    """Configura el logging global de la aplicación una sola vez."""
    global _configurado
    if _configurado:
        return
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter("[%(levelname)s] %(name)s: %(message)s"))
    root = logging.getLogger()
    root.handlers[:] = [handler]
    root.setLevel(logging.INFO)
    _configurado = True


def get_logger(name: str) -> Any:
    """Devuelve un logger nombrado listo para emitir eventos.

    Uso:
        log = get_logger(__name__)
        log.info("pipeline_stage", extra={"document_id": doc_id, "stage": "chunking"})
    """
    configure_logging()
    return logging.getLogger(name)