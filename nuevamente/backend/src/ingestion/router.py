"""Orquestador de ingesta (BE-ING-001, COMP-01).

Recibe el archivo, valida tamaño y tipo, delega en el extractor
correspondiente y devuelve un `IngestResult` con un `document_id` nuevo.
NO sube a almacenamiento (eso es `storage/upload.py`, invocado por
`api/orchestrator.py`): COMP-01 y COMP-09 permanecen desacoplados (RNF-005).
"""
import uuid

from src.ingestion.md_extractor import extract_markdown_text
from src.ingestion.models import FileType, IngestResult, PageText
from src.ingestion.pdf_extractor import extract_pdf_text
from src.ingestion.txt_extractor import extract_txt_text
from src.ingestion.validators import (
    detect_type,
    display_name,
    validate_signature,
    validate_size,
)


def new_document_id() -> str:
    """Genera un identificador de documento único (`doc_` + 12 hex)."""
    return f"doc_{uuid.uuid4().hex[:12]}"


def _extract(file_type: FileType, content: bytes) -> tuple[str, list[PageText]]:
    if file_type == "pdf":
        return extract_pdf_text(content)
    if file_type == "md":
        return extract_markdown_text(content), []
    return extract_txt_text(content), []


def _pdf_warnings(pages: list[PageText]) -> list[str]:
    empty = [p.page for p in pages if not p.text.strip()]
    if not empty:
        return []
    shown = ", ".join(str(n) for n in empty[:10])
    suffix = "…" if len(empty) > 10 else ""
    return [
        f"{len(empty)} de {len(pages)} páginas no tienen texto extraíble "
        f"(p. ej. imágenes escaneadas): {shown}{suffix}. Ese contenido no se procesará."
    ]


class IngestionRouter:
    """Punto de entrada único de la capa de ingesta."""

    def ingest(self, filename: str, content: bytes) -> IngestResult:
        """Valida, detecta el tipo y extrae el texto de `content`.

        Lanza:
            InvalidFileError, ScannedPdfError — ver cada extractor/validador.
        """
        name = display_name(filename)
        validate_size(content)
        file_type = detect_type(name)
        validate_signature(file_type, content)

        raw_text, pages = _extract(file_type, content)
        warnings = _pdf_warnings(pages) if file_type == "pdf" else []

        return IngestResult(
            document_id=new_document_id(),
            file_type=file_type,
            raw_text=raw_text,
            pages=pages,
            filename=name,
            warnings=warnings,
        )
