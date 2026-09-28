"""Contrato del servicio de validación de fidelidad (COMP-07)."""
from typing import Protocol
from src.validation.models import FidelityEvaluation


class ValidationService(Protocol):
    """Evalúa si el contenido generado está sustentado en el contexto fuente."""

    def validate(self, contenido_generado: str, contexto_fuente: str) -> FidelityEvaluation:
        """Extrae claims de `contenido_generado`, los contrasta contra
        `contexto_fuente` y agrega el resultado en un score determinista.

        Implementación futura.
        """
        ...
