"""Limpieza de texto (PROC-003).

- `clean_text`: normaliza saltos de línea, caracteres de control y espacios,
  conservando la sangría (listas anidadas y bloques de código en Markdown).
- `clean_pdf_pages`: además elimina encabezados/pies de página repetidos y
  números de página sueltos, que ensucian los chunks.
- `prepare_document_text`: punto de entrada que deja texto y páginas
  consistentes entre sí (las páginas son subcadenas del texto final).
"""
import re
from collections import Counter

from src.core.exceptions import InvalidFileError
from src.ingestion.models import PageText

_EDGE_LINES = 3          # líneas de arriba/abajo de cada página que se inspeccionan
_MIN_PAGES_FOR_HEADERS = 3
_MAX_HEADER_LEN = 100
_PAGE_NUMBER = re.compile(
    r"^\s*(p[áa]g(ina|\.)?\s*)?\d{1,4}(\s*(de|of|/)\s*\d{1,4})?\s*$", re.IGNORECASE
)


def clean_text(raw_text: str) -> str:
    """Normaliza espacios, elimina caracteres de control y colapsa saltos repetidos."""
    if not raw_text:
        return ""

    text = raw_text.replace("\ufeff", "")
    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # Elimina caracteres de control excepto salto de línea y tabulación.
    text = "".join(ch for ch in text if ch in ("\n", "\t") or ord(ch) >= 32)

    # Colapsa espacios repetidos solo en medio de la línea (conserva la sangría).
    text = re.sub(r"(?<=\S)[ \t]{2,}", " ", text)
    # Quita espacios al final de cada línea.
    text = re.sub(r"[ \t]+\n", "\n", text)
    # Reduce saltos de línea excesivos.
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip("\n").rstrip()


def _signature(line: str) -> str:
    """Normaliza una línea para detectar repeticiones ('Página 3' == 'Página 4')."""
    return re.sub(r"\d+", "#", line.strip().lower())


def _edge_indexes(lines: list[str]) -> list[int]:
    """Índices de las primeras y últimas líneas no vacías de una página."""
    non_empty = [i for i, line in enumerate(lines) if line.strip()]
    return sorted(set(non_empty[:_EDGE_LINES] + non_empty[-_EDGE_LINES:]))


def clean_pdf_pages(pages: list[PageText]) -> list[PageText]:
    """Limpia cada página y quita encabezados, pies y números de página repetidos.

    Devuelve solo las páginas que conservan texto.
    """
    split = [clean_text(p.text).split("\n") for p in pages]

    counts: Counter[str] = Counter()
    if len(pages) >= _MIN_PAGES_FOR_HEADERS:
        for lines in split:
            signatures = {
                _signature(lines[i])
                for i in _edge_indexes(lines)
                if len(lines[i].strip()) <= _MAX_HEADER_LEN
            }
            counts.update(signatures)
    threshold = max(_MIN_PAGES_FOR_HEADERS, len(pages) // 2)
    repeated = {sig for sig, n in counts.items() if n >= threshold}

    result: list[PageText] = []
    for page, lines in zip(pages, split, strict=True):
        drop = set()
        for i in _edge_indexes(lines):
            line = lines[i]
            if _PAGE_NUMBER.match(line) or (
                len(line.strip()) <= _MAX_HEADER_LEN and _signature(line) in repeated
            ):
                drop.add(i)
        kept = [line for i, line in enumerate(lines) if i not in drop]
        text = clean_text("\n".join(kept))
        if text.strip():
            result.append(PageText(page=page.page, text=text))
    return result


def prepare_document_text(
    raw_text: str, pages: list[PageText]
) -> tuple[str, list[PageText]]:
    """Devuelve (texto_limpio, páginas_limpias) coherentes entre sí.

    Para PDF, el texto es la unión (`\\n\\n`) de las páginas limpias, de modo
    que cada página es una subcadena del texto y se puede asignar `page` a
    cada chunk. Para MD/TXT no hay páginas.

    Lanza:
        InvalidFileError: si tras la limpieza no queda texto utilizable.
    """
    if pages:
        clean_pages = clean_pdf_pages(pages)
        text = "\n\n".join(p.text for p in clean_pages)
    else:
        clean_pages = []
        text = clean_text(raw_text)

    if not text.strip():
        raise InvalidFileError("El documento no contiene texto utilizable tras la limpieza.")
    return text, clean_pages
