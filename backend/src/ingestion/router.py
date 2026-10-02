"""Orquestador de ingesta (BE-ING-001, COMP-01).

Recibe el archivo, detecta su tipo, delega en el extractor correspondiente,
valida tamaño y devuelve un `IngestResult` con un `document_id` nuevo. NO
sube a OCI (eso es `storage/upload.py`, invocado por `api/orchestrator.py`).
"""
import os

from src.ingestion.md_extractor import extract_markdown_text
from src.ingestion.models import IngestResult
from src.ingestion.pdf_extractor import extract_pdf_text
from src.ingestion.txt_extractor import extract_txt_text
from src.ingestion.validators import detect_type, validate_size


class IngestionRouter:
    """Punto de entrada único de la capa de ingesta."""

    def ingest(self, filename: str, content: bytes) -> IngestResult:
        """Valida, detecta el tipo y extrae el texto de `content`."""
        validate_size(content)
        file_type = detect_type(filename)

        if file_type == "pdf":
            raw, pages = extract_pdf_text(content)
        else:
            raw = (
                extract_markdown_text(content)
                if file_type == "md"
                else extract_txt_text(content)
            )
            pages = []

        document_id = os.urandom(12).hex()
        return IngestResult(
            document_id=document_id,
            file_type=file_type,
            raw_text=raw,
            pages=pages,
            filename=filename,
        )