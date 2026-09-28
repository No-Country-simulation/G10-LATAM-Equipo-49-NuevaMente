"""Contrato del extractor de documentos (Protocol).

Cualquier extractor concreto (PDF, Markdown, TXT) debe cumplir esta
interfaz para que `router.py` pueda invocarlo de forma intercambiable
(RNF-005 — mantenibilidad por capas).
"""
from typing import Protocol


class DocumentExtractor(Protocol):
    """Extrae texto crudo (y, si aplica, texto por página) de un archivo."""

    def extract(self, data: bytes) -> tuple[str, list]:
        """Extrae el texto de `data`.

        Parámetros:
            data: contenido binario del archivo ya leído en memoria.

        Retorna:
            Tupla (raw_text, pages) donde `pages` es una lista de
            `ingestion.models.PageText` (vacía si el formato no tiene
            noción de página, p. ej. TXT o MD).

        Lanza:
            InvalidFileError: si el contenido no puede interpretarse en
                el formato esperado.
            ScannedPdfError: (solo PDF) si no hay texto extraíble.

        Implementación futura.
        """
        ...
