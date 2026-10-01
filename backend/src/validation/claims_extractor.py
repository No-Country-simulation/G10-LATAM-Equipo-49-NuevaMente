"""Extracción de claims del contenido generado (VAL-001, BE-VAL-002a)."""
from src.validation.models import Claim


def extract_claims(contenido_generado: str) -> list[Claim]:
    """Extrae afirmaciones verificables de `contenido_generado`, en
    formato JSON según especifica VAL-001.

    Implementación futura.
    """
    ...
