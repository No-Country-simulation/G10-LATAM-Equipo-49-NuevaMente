"""Extractor de PDF (BE-ING-002, ING-007).

Tecnología: PyPDF (DT-04). Lanza `ScannedPdfError` si no hay texto extraíble.
"""
from io import BytesIO

from pypdf import PdfReader

from src.core.exceptions import InvalidFileError, ScannedPdfError
from src.ingestion.models import PageText


def extract_pdf_text(data: bytes) -> tuple[str, list[PageText]]:
    """Extrae texto de un PDF, página por página.

    Retorna (raw_text, pages) — `raw_text` es la concatenación del texto de
    todas las páginas; `pages` conserva el texto por página (RNF-006).
    """
    try:
        reader = PdfReader(BytesIO(data))
    except Exception as exc:
        raise InvalidFileError(f"No se pudo leer el PDF: {exc}") from exc

    pages: list[PageText] = []
    for i, page in enumerate(reader.pages, start=1):
        try:
            text = (page.extract_text() or "").strip()
        except Exception:
            text = ""
        if text:
            pages.append(PageText(page=i, text=text))

    if not pages:
        raise ScannedPdfError("No se pudo extraer texto del PDF (¿documento escaneado?)")

    raw = "\n\n".join(p.text for p in pages)
    return raw, pages