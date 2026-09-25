from src.core.config import settings
from src.core.exceptions import InvalidFileError

ALLOWED_EXTENSIONS = {".pdf", ".md", ".markdown", ".txt"}


def validate_size(content: bytes) -> None:
    max_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024
    if len(content) == 0:
        raise InvalidFileError("El archivo está vacío")
    if len(content) > max_bytes:
        raise InvalidFileError(
            f"El archivo excede el tamaño máximo permitido "
            f"({settings.MAX_FILE_SIZE_MB} MB)"
        )


def detect_type(filename: str) -> str:
    import os

    ext = os.path.splitext(filename.lower())[1]
    if ext not in ALLOWED_EXTENSIONS:
        raise InvalidFileError(f"Formato no soportado: {ext or 'sin extensión'}")
    if ext == ".pdf":
        return "pdf"
    if ext in (".md", ".markdown"):
        return "md"
    return "txt"
