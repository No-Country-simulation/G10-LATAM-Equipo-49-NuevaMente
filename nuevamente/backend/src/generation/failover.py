"""Provider con cadena de failover automático para LLM (Cohere → Gemini → mock).

Cumple el Protocol `LLMProvider` encadenando un proveedor primario y uno de
respaldado. Si el primario falla tras sus reintentos, el error se loguea y
se intenta el de respaldo. Si ambos fallan, se propaga el error del último.
"""
import logging
from typing import Any

from src.core.exceptions import LLMProviderError

log = logging.getLogger(__name__)


class FailoverLLMProvider:
    """`LLMProvider` con cadena de dos proveedores: primario + respaldo.

    Comportamiento:
      1. Intenta el proveedor primario.
      2. Si falla (cualquier excepción), loguea warning y prueba el respaldo.
      3. Si el respaldo también falla, propaga la excepción del segundo.
      4. No reintenta más allá de los reintentos internos de cada proveedor.
    """

    def __init__(
        self,
        primary: Any,
        backup: Any | None = None,
    ) -> None:
        self._primary = primary
        self._backup = backup

    def generate(self, prompt: str, temperature: float = 0.3) -> str:
        """Genera texto intentando primario y, si falla, respaldo."""
        last_exc: Exception | None = None

        # 1. Proveedor primario
        try:
            return self._primary.generate(prompt, temperature)
        except Exception as exc:
            last_exc = exc
            log.warning(
                "llm_primary_failed_fallback_to_backup: primary=%s, backup=%s, error=%s",
                self._primary.__class__.__name__,
                self._backup.__class__.__name__ if self._backup else "none",
                str(exc),
            )

        # 2. Proveedor de respaldo (si existe)
        if self._backup is not None:
            try:
                return self._backup.generate(prompt, temperature)
            except Exception as exc:
                last_exc = exc
        else:
            log.warning(
                "llm_no_backup_configured: error=%s",
                str(last_exc),
            )

        # 3. Ambos fallaron
        msg = f"Todos los proveedores LLM fallaron. Último error: {last_exc}"
        raise LLMProviderError(msg) from last_exc


# Nota: cumple el Protocol `LLMProvider` por forma estructural (duck typing).
# No se usa issubclass() en importación: el Protocol no es @runtime_checkable.