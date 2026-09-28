"""Contrato de logging estructurado (FND-004, RNF-003).

Fuente: Plan Técnico, RNF-003 (Observabilidad) — cada ejecución del
pipeline debe generar logs con: document_id, etapa, duración, resultado.

Implementación futura: usar `structlog` o `logging` estándar, según decida
el equipo. Ninguna configuración de logging real ocurre en este módulo.
"""
from typing import Any


def configure_logging() -> None:
    """Configura el logging global de la aplicación.

    Debe llamarse una única vez al arrancar el proceso (API o UI).
    Implementación futura.
    """
    ...


def get_logger(name: str) -> Any:
    """Devuelve un logger nombrado, listo para emitir eventos estructurados.

    Uso previsto (una vez implementado):
        log = get_logger(__name__)
        log.info("pipeline_stage", document_id=doc_id, stage="chunking")

    Parámetros:
        name: nombre del módulo que solicita el logger (típicamente `__name__`).

    Implementación futura.
    """
    ...
