"""Validaciones de ingesta (ING-005, ING-006).

Fuente: RF-001 (flujos alternativos), DT-12 (tamaño máximo configurable vía
`settings.MAX_FILE_SIZE_MB`).
"""
from src.core.config import get_settings
from src.core.exceptions import InvalidFileError
from src.ingestion.models import FileType

ALLOWED_EXTENSIONS: set[str] = {".pdf", ".md", ".markdown", ".txt"}


def validate_size(content: bytes) -> None:
    """Valida que `content` no esté vacío ni exceda `MAX_FILE_SIZE_MB`."""
    settings = get_settings()
    if not content:
        raise InvalidFileError("El archivo está vacío")
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) > max_bytes:
        raise InvalidFileError(
            f"El archivo excede el tamaño máximo de {settings.MAX_FILE_SIZE_MB} MB "
            f"({len(content) / (1024 * 1024):.1f} MB)"
        )


def detect_type(filename: str) -> FileType:
    """Determina el tipo de archivo (pdf/md/txt) a partir de su extensión."""
    import os

    ext = os.path.splitext(filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileError(f"Extensión no soportada: '{ext or '(sin extensión)'}'")
    if ext == ".pdf":
        return "pdf"
    if ext in {".md", ".markdown"}:
        return "md"
    return "txt"