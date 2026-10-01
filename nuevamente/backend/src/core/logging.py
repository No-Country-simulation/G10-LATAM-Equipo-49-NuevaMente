"""Logging estructurado (FND-004, RNF-003).

Cada evento se emite como `evento clave=valor ...`, con `document_id`, `stage`,
`duration_ms` y `result` en las etapas del pipeline. Usa solo `logging` de la
biblioteca estándar (sin dependencias adicionales).
"""
import json
import logging
import sys
import time
from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from src.core.config import get_settings

_LOG_FORMAT = "%(asctime)s %(levelname)-7s %(name)s | %(message)s"


def _format_value(value: Any) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False) if (" " in value or not value) else value
    return str(value)


class StructuredLogger:
    """Envuelve un `logging.Logger` para emitir eventos con campos clave=valor."""

    def __init__(self, logger: logging.Logger) -> None:
        self._logger = logger

    def _emit(self, level: int, event: str, fields: dict[str, Any], exc_info: bool) -> None:
        if not self._logger.isEnabledFor(level):
            return
        details = " ".join(f"{key}={_format_value(val)}" for key, val in fields.items())
        self._logger.log(level, f"{event} {details}".rstrip(), exc_info=exc_info)

    def debug(self, event: str, **fields: Any) -> None:
        self._emit(logging.DEBUG, event, fields, False)

    def info(self, event: str, **fields: Any) -> None:
        self._emit(logging.INFO, event, fields, False)

    def warning(self, event: str, **fields: Any) -> None:
        self._emit(logging.WARNING, event, fields, False)

    def error(self, event: str, **fields: Any) -> None:
        self._emit(logging.ERROR, event, fields, False)

    def exception(self, event: str, **fields: Any) -> None:
        """Registra un error con su traza completa."""
        self._emit(logging.ERROR, event, fields, True)


def configure_logging() -> None:
    """Configura el logging global. Es idempotente (se puede llamar varias veces)."""
    root = logging.getLogger()
    if not any(getattr(h, "_nuevamente", False) for h in root.handlers):
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(_LOG_FORMAT))
        handler._nuevamente = True  # type: ignore[attr-defined]
        root.addHandler(handler)
    root.setLevel(get_settings().LOG_LEVEL.upper())


def get_logger(name: str) -> StructuredLogger:
    """Devuelve un logger nombrado que acepta campos estructurados.

    Uso: `log.info("pipeline_stage", document_id=doc_id, stage="chunking")`
    """
    return StructuredLogger(logging.getLogger(name))


@contextmanager
def log_stage(log: StructuredLogger, stage: str, **fields: Any) -> Iterator[None]:
    """Mide y registra una etapa del pipeline (RNF-003: etapa, duración, resultado)."""
    started = time.perf_counter()
    try:
        yield
    except Exception:
        duration_ms = round((time.perf_counter() - started) * 1000)
        log.error("pipeline_stage", stage=stage, result="error", duration_ms=duration_ms, **fields)
        raise
    duration_ms = round((time.perf_counter() - started) * 1000)
    log.info("pipeline_stage", stage=stage, result="ok", duration_ms=duration_ms, **fields)
