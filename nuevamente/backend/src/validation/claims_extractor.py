"""Extracción de claims del contenido generado (VAL-001, BE-VAL-002a).

Extracción determinista por oraciones: cada oración con contenido sustantivo
se trata como un `Claim` potencialmente verificable.
"""
import re

from src.validation.models import Claim

_SENT = re.compile(r"(?<=[.!?])\s+")
_LINE = re.compile(r"\n+")
# *****************************************************************************
#  MEJORA AUD-009 — 2026-10-15
#  Las líneas de plantilla/aviso del contenido mock (encabezados Markdown,
#  referencias `**[...]**`, el rótulo "Nicho / contexto" y el aviso ⚠️) se
#  contaban como afirmaciones verificables y aparecían como "no soportadas",
#  inflando el ruido del score de fidelidad. Se excluyen del extractor.
# *****************************************************************************
_TEMPLATE_PREFIXES = ("#", "**", "Nicho", "⚠️")


def extract_claims(contenido_generado: str) -> list[Claim]:
    """Extrae afirmaciones verificables de `contenido_generado`."""
    claims: list[Claim] = []
    # Primero dividimos por saltos de línea, luego por oraciones
    for linea in _LINE.split(contenido_generado or ""):
        raw = linea.strip()
        if not raw or raw.startswith(_TEMPLATE_PREFIXES):
            continue
        # Los fragmentos citados pueden venir como cita Markdown ("> ...").
        raw = raw.lstrip(">").lstrip("*").strip()
        if not raw or "⚠️" in raw:
            continue
        for sent in _SENT.split(raw):
            limpiada = sent.strip()
            # al menos dos palabras y una minúscula (descarta títulos/plantillas)
            if len(limpiada.split()) >= 3 and any(c.islower() for c in limpiada):
                claims.append(Claim(text=limpiada[:400]))
    return claims
