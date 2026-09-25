import uuid
from langchain_text_splitters import RecursiveCharacterTextSplitter

from src.processing.models import DocumentChunk
from src.processing.cleaning import clean_text
from src.core.config import settings
from src.core.exceptions import NuevaMenteError

MAX_DOCUMENT_CHARS = 2_000_000  # PROC-005


def _page_for_offset(pages: list[dict], global_offset: int) -> int | None:
    """Determina a qué página pertenece un offset del texto concatenado."""
    if not pages:
        return None
    cursor = 0
    for page in pages:
        length = len(page["text"])
        if cursor <= global_offset < cursor + length + 2:  # +2 por el "\n\n"
            return page["page"]
        cursor += length + 2
    return pages[-1]["page"]


def chunk_text(raw_text: str, doc_id: str, pages: list[dict] | None = None) -> list[DocumentChunk]:
    text = clean_text(raw_text)
    if not text:
        return []
    if len(text) > MAX_DOCUMENT_CHARS:
        raise NuevaMenteError(
            f"Documento demasiado grande ({len(text)} caracteres, "
            f"máximo {MAX_DOCUMENT_CHARS})"
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    fragments = splitter.split_text(text)

    chunks: list[DocumentChunk] = []
    cursor = 0
    for i, frag in enumerate(fragments):
        start = text.find(frag, cursor)
        if start == -1:  # fragmento repetido: buscar desde el inicio como fallback
            start = text.find(frag)
        end = start + len(frag)
        cursor = max(cursor, end - settings.CHUNK_OVERLAP)

        chunks.append(
            DocumentChunk(
                id=str(uuid.uuid4()),
                doc_id=doc_id,
                text=frag,
                position=i,
                page=_page_for_offset(pages, start) if pages else None,
                char_start=start,
                char_end=end,
            )
        )
    return chunks
