"""Extractor de PDF (BE-ING-002, ING-006, ING-007).

Usa pypdf. El fallback a pdfplumber (DT-04) queda pendiente.
"""
from io import BytesIO

from pypdf import PdfReader

from src.core.exceptions import InvalidFileError, ScannedPdfError
from src.ingestion.models import PageText


def extract_pdf_text(data: bytes) -> tuple[str, list[PageText]]:
    """Extrae texto de un PDF, página por página.

    Retorna:
        Tupla (raw_text, pages). `pages` incluye TODAS las páginas (con
        `text` vacío si no tienen texto extraíble); `raw_text` concatena solo
        las que sí tienen texto.

    Lanza:
        InvalidFileError: PDF corrupto o protegido con contraseña.
        ScannedPdfError: ninguna página contiene texto extraíble (ING-007).
    """
    try:
        reader = PdfReader(BytesIO(data))

        if reader.is_encrypted:
            try:
                unlocked = reader.decrypt("")  # PDFs cifrados sin clave de apertura
            except Exception:
                unlocked = 0
            if not unlocked:
                raise InvalidFileError(
                    "El PDF está protegido con contraseña. "
                    "Quite la protección y vuelva a subirlo."
                )

        pages: list[PageText] = []
        for number, page in enumerate(reader.pages, start=1):
            try:
                text = page.extract_text() or ""
            except Exception:
                text = ""
            pages.append(PageText(page=number, text=text))
    except InvalidFileError:
        raise
    except Exception as exc:
        raise InvalidFileError(
            "No fue posible leer el PDF: el archivo puede estar corrupto."
        ) from exc

    with_text = [p.text for p in pages if p.text.strip()]
    if not with_text:
        raise ScannedPdfError(
            "El PDF no contiene texto extraíble (posible documento escaneado). "
            "Suba una versión con texto seleccionable."
        )

    return "\n\n".join(with_text), pages
