"""Chunking con overlap configurable (BE-PROC-002, PROC-004, PROC-005).

Tecnología prevista: `RecursiveCharacterTextSplitter` (LangChain), DT-03.
Tamaños por defecto: `settings.CHUNK_SIZE=800`, `settings.CHUNK_OVERLAP=150`
(TASK-002).
"""
from src.processing.models import DocumentChunk
from src.ingestion.models import PageText

MAX_DOCUMENT_CHARS = 2_000_000  # PROC-005 — umbral de "documento demasiado grande"


def chunk_text(
    raw_text: str,
    doc_id: str,
    pages: list[PageText] | None = None,
) -> list[DocumentChunk]:
    """Divide `raw_text` (ya limpio) en una lista de `DocumentChunk`.

    Parámetros:
        raw_text: texto normalizado (ver `cleaning.clean_text`).
        doc_id: identificador del documento al que pertenecen los chunks.
        pages: texto por página, si el origen es un PDF — permite asignar
            `DocumentChunk.page` a cada fragmento (ver nota en `models.py`).

    Retorna:
        Lista de `DocumentChunk`, nunca con `text` vacío (criterio de
        aceptación de TASK-002). Lista vacía si `raw_text` está vacío.

    Lanza:
        NuevaMenteError: si `len(raw_text) > MAX_DOCUMENT_CHARS` (PROC-005).

    Implementación futura.
    """
    ...
