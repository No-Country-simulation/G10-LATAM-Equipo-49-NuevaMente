"""Extracción de claims del contenido generado (VAL-001, BE-VAL-002a).

Extracción determinista por oraciones: cada oración con contenido sustantivo
se trata como un `Claim` potencialmente verificable.
"""
import re

from src.validation.models import Claim

_SENT = re.compile(r"(?<=[.!?])\s+")
_LINE = re.compile(r"\n+")


def extract_claims(contenido_generado: str) -> list[Claim]:
    """Extrae afirmaciones verificables de `contenido_generado`."""
    claims: list[Claim] = []
    # Primero dividimos por saltos de línea, luego por oraciones
    for linea in _LINE.split(contenido_generado or ""):
        for sent in _SENT.split(linea):
            limpiada = sent.strip()
            # al menos dos palabras y una minúscula (descarta títulos/plantillas)
            if len(limpiada.split()) >= 3 and any(c.islower() for c in limpiada):
                claims.append(Claim(text=limpiada[:400]))
    return claims
