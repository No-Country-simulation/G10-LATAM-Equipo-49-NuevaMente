"""Chunking con overlap configurable (BE-PROC-002, PROC-004, PROC-005).

Usa `RecursiveCharacterTextSplitter` (LangChain), DT-03. Tamaños por defecto:
`CHUNK_SIZE=800`, `CHUNK_OVERLAP=150` (TASK-002). Cada chunk conserva su
posición en el texto (`char_start`/`char_end`), su página (PDF) y la sección
(último encabezado Markdown anterior) para trazabilidad (RNF-006).
"""
import re
from bisect import bisect_right

from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.core.config import get_settings
from src.core.exceptions import DocumentTooLargeError
from src.ingestion.models import PageText
from src.processing.models import DocumentChunk

_HEADING = re.compile(r"^#{1,6}[ \t]+(.+?)[ \t#]*$", re.MULTILINE)


def _heading_index(text: str) -> tuple[list[int], list[str]]:
    """Posiciones y títulos de los encabezados Markdown del texto."""
    positions: list[int] = []
    titles: list[str] = []
    for match in _HEADING.finditer(text):
        positions.append(match.start())
        titles.append(match.group(1).strip())
    return positions, titles


def _page_ranges(text: str, pages: list[PageText]) -> list[tuple[int, int, int]]:
    """Rangos (inicio, fin, página) de cada página dentro del texto."""
    ranges: list[tuple[int, int, int]] = []
    cursor = 0
    for page in pages:
        start = text.find(page.text, cursor)
        if start == -1:
            continue
        end = start + len(page.text)
        ranges.append((start, end, page.page))
        cursor = end
    return ranges


def _page_for(position: int, ranges: list[tuple[int, int, int]]) -> int | None:
    if not ranges:
        return None
    starts = [r[0] for r in ranges]
    index = bisect_right(starts, position) - 1
    if index < 0:
        return ranges[0][2]
    start, end, page = ranges[index]
    if position >= end and index + 1 < len(ranges):  # cae en el hueco entre páginas
        return ranges[index + 1][2]
    return page


def chunk_text(
    raw_text: str,
    doc_id: str,
    pages: list[PageText] | None = None,
) -> list[DocumentChunk]:
    """Divide `raw_text` (ya limpio) en una lista de `DocumentChunk`.

    Parámetros:
        raw_text: texto normalizado (ver `cleaning.prepare_document_text`).
        doc_id: identificador del documento al que pertenecen los chunks.
        pages: páginas limpias (solo PDF), para asignar `DocumentChunk.page`.

    Retorna:
        Lista de `DocumentChunk`, nunca con `text` vacío. Lista vacía si
        `raw_text` está vacío. Los ids son deterministas: `{doc_id}-chunk-{n}`.

    Lanza:
        DocumentTooLargeError: si `len(raw_text) > MAX_DOCUMENT_CHARS` (PROC-005).
    """
    if not raw_text.strip():
        return []

    settings = get_settings()
    if len(raw_text) > settings.MAX_DOCUMENT_CHARS:
        raise DocumentTooLargeError(
            f"El documento es demasiado grande ({len(raw_text):,} caracteres; "
            f"máximo {settings.MAX_DOCUMENT_CHARS:,})."
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    fragments = splitter.split_text(raw_text)

    ranges = _page_ranges(raw_text, pages or [])
    heading_pos, heading_titles = _heading_index(raw_text)

    chunks: list[DocumentChunk] = []
    prev_start = -1
    prev_end = 0
    for fragment in fragments:
        if not fragment.strip():
            continue

        # Con overlap, el siguiente chunk empieza como mucho `CHUNK_OVERLAP`
        # caracteres antes del fin del anterior. Buscar desde ahí (y nunca antes
        # del inicio previo + 1) evita confundirlo con texto repetido anterior.
        lower = max(prev_start + 1, prev_end - settings.CHUNK_OVERLAP)
        start = raw_text.find(fragment, lower)
        if start == -1:
            start = raw_text.find(fragment, prev_start + 1)
        if start == -1:  # no debería ocurrir; se conserva el chunk con posición aproximada
            start = min(max(lower, 0), len(raw_text) - 1)
        end = min(start + len(fragment), len(raw_text))

        index = bisect_right(heading_pos, start) - 1
        position = len(chunks)
        chunks.append(
            DocumentChunk(
                id=f"{doc_id}-chunk-{position}",
                doc_id=doc_id,
                text=fragment,
                position=position,
                section=heading_titles[index] if index >= 0 else None,
                page=_page_for(start, ranges),
                char_start=start,
                char_end=end,
            )
        )
        prev_start, prev_end = start, end

    return chunks