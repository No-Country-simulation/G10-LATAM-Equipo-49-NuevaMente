"""Validaciones de ingesta (ING-005, ING-006).

Fuente: RF-001 (flujos alternativos), DT-12 (tamaño máximo asumido en 10 MB,
configurable vía `settings.MAX_FILE_SIZE_MB`).
"""
from src.ingestion.models import FileType

ALLOWED_EXTENSIONS: set[str] = {".pdf", ".md", ".markdown", ".txt"}


def validate_size(content: bytes) -> None:
    """Valida que `content` no esté vacío ni exceda `MAX_FILE_SIZE_MB`.

    Lanza:
        InvalidFileError: si el archivo está vacío o excede el tamaño máximo.

    Implementación futura.
    """
    ...


def detect_type(filename: str) -> FileType:
    """Determina el tipo de archivo (pdf/md/txt) a partir de su extensión.

    Lanza:
        InvalidFileError: si la extensión no está en `ALLOWED_EXTENSIONS`.

    Implementación futura.
    """
    ...
