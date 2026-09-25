import uuid
from dataclasses import dataclass, field

from src.ingestion.validators import validate_size, detect_type
from src.ingestion.pdf_extractor import extract_pdf_text
from src.ingestion.md_extractor import extract_markdown_text
from src.ingestion.txt_extractor import extract_txt_text
from src.core.logging import get_logger

log = get_logger(__name__)


@dataclass
class IngestResult:
    document_id: str
    file_type: str
    raw_text: str
    pages: list[dict] = field(default_factory=list)
    filename: str = ""


class IngestionService:
    def ingest(self, filename: str, content: bytes) -> IngestResult:
        validate_size(content)
        file_type = detect_type(filename)

        if file_type == "pdf":
            raw_text, pages = extract_pdf_text(content)
        elif file_type == "md":
            raw_text, pages = extract_markdown_text(content), []
        else:
            raw_text, pages = extract_txt_text(content), []

        document_id = f"doc_{uuid.uuid4().hex[:10]}"
        log.info("document_ingested", document_id=document_id, file_type=file_type,
                  chars=len(raw_text))

        return IngestResult(
            document_id=document_id,
            file_type=file_type,
            raw_text=raw_text,
            pages=pages,
            filename=filename,
        )
