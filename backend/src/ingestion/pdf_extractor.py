"""Extractor de PDF (BE-ING-002, ING-007).

Tecnología prevista: PyPDF, con fallback a pdfplumber si PyPDF no
recupera texto (DT-04). Implementación futura — este módulo solo declara
el contrato de la función.
"""
from src.ingestion.models import PageText


def extract_pdf_text(data: bytes) -> tuple[str, list[PageText]]:
    """Extrae texto de un PDF, página por página.

    Retorna:
        Tupla (raw_text, pages) — `raw_text` es la concatenación del texto
        de todas las páginas; `pages` conserva el texto por página para
        trazabilidad (RNF-006).

    Lanza:
        ScannedPdfError: si ninguna página contiene texto extraíble
            (posible PDF escaneado, ING-007).

    Implementación futura.
    """
    ...
