"""Chunking con overlap configurable (BE-PROC-002, PROC-004, PROC-005).

Implementación determinista sobre el texto ya limpio: tokeniza el texto por
oraciones (consulta envuelta en `clean_text`) y las agrupa en fragmentos de
hasta `settings.CHUNK_SIZE` caracteres, con `settings.CHUNK_OVERLAP` de
solapamiento entre fragmentos consecutivos. No requiere LangChain ni red.
"""
import re

from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError
from src.ingestion.models import PageText
from src.processing.cleaning import clean_text
from src.processing.models import DocumentChunk

_SENT = re.compile(r"(?<=[.!?])\s+")


def chunk_text(
    raw_text: str,
    doc_id: str,
    pages: list[PageText] | None = None,
) -> list[DocumentChunk]:
    """Divide `raw_text` (ya limpio) en una lista de `DocumentChunk`.

    Nunca produce chunks con `text` vacío (criterio de aceptación TASK-002);
    devuelve lista vacía si `raw_text` está vacío. Lanza `NuevaMenteError`
    si `len(raw_text) > settings.MAX_DOCUMENT_CHARS` (PROC-005).
    """
    settings = get_settings()
    if len(raw_text) > settings.MAX_DOCUMENT_CHARS:
        raise NuevaMenteError(
            f"documento excede el tamaño máximo "
            f"({settings.MAX_DOCUMENT_CHARS} chars): {len(raw_text)}"
        )

    texto = clean_text(raw_text)
    if not texto:
        return []

    fragmentos = _SENT.split(texto)
    size = settings.CHUNK_SIZE
    overlap = settings.CHUNK_OVERLAP
    chunks: list[DocumentChunk] = []
    buffer, start = "", 0

    def _empezar(nuevo: str) -> None:
        nonlocal buffer, start
        buffer = nuevo
        start = len(chunks) * (size - overlap)

    for frag in fragmentos:
        if len(buffer) + len(frag) > size and buffer:
            chunks.append(
                DocumentChunk(
                    id=f"{doc_id}_{len(chunks):04d}",
                    doc_id=doc_id,
                    text=buffer.strip(),
                    position=len(chunks),
                    char_start=start,
                    char_end=start + len(buffer.strip()),
                )
            )
            solape = buffer if overlap else ""
            _empezar((solape + " " + frag).strip())
        else:
            buffer = (buffer + " " + frag).strip()

    if buffer.strip():
        chunks.append(
            DocumentChunk(
                id=f"{doc_id}_{len(chunks):04d}",
                doc_id=doc_id,
                text=buffer.strip(),
                position=len(chunks),
                char_start=start,
                char_end=start + len(buffer.strip()),
            )
        )

    return _asignar_paginas(chunks, pages or [])


def _asignar_paginas(chunks: list[DocumentChunk], pages: list[PageText]) -> list[DocumentChunk]:
    if not pages:
        return chunks
    # Asigna a cada chunk la página cuyo rango de texto lo contiene
    # (aproximación por orden de aparición, suficiente para trazabilidad).
    pagina, offset = 0, 0
    for chunk in chunks:
        while pagina < len(pages) - 1 and offset + len(pages[pagina].text) < chunk.char_start:
            offset += len(pages[pagina].text)
            pagina += 1
        chunk.page = pages[pagina].page if pagina < len(pages) else None
    return chunks