"""Validaciones de ingesta (ING-005, ING-006).

Fuente: RF-001 (flujos alternativos), DT-12 (tamaño máximo asumido en 10 MB,
configurable vía `settings.MAX_FILE_SIZE_MB`).
"""
from src.core.config import get_settings
from src.core.exceptions import InvalidFileError
from src.ingestion.models import FileType

ALLOWED_EXTENSIONS: set[str] = {".pdf", ".md", ".markdown", ".txt"}

_EXTENSION_TO_TYPE: dict[str, FileType] = {
    ".pdf": "pdf",
    ".md": "md",
    ".markdown": "md",
    ".txt": "txt",
}


def display_name(filename: str) -> str:
    """Devuelve solo el nombre del archivo (sin rutas de Windows ni de Unix)."""
    return filename.replace("\\", "/").rsplit("/", 1)[-1].strip()


def validate_size(content: bytes) -> None:
    """Valida que `content` no esté vacío ni exceda `MAX_FILE_SIZE_MB`.

    Lanza:
        InvalidFileError: si el archivo está vacío o excede el tamaño máximo.
    """
    if not content:
        raise InvalidFileError("El archivo está vacío.")

    max_mb = get_settings().MAX_FILE_SIZE_MB
    if len(content) > max_mb * 1024 * 1024:
        raise InvalidFileError(
            f"El archivo excede el tamaño máximo permitido ({max_mb} MB)"
        )


def detect_type(filename: str) -> FileType:
    """Determina el tipo de archivo (pdf/md/txt) a partir de su extensión.

    Lanza:
        InvalidFileError: si no hay nombre o la extensión no está permitida.
    """
    name = display_name(filename)
    if not name:
        raise InvalidFileError("El archivo no tiene nombre.")

    dot = name.rfind(".")
    extension = name[dot:].lower() if dot != -1 else ""
    if extension not in ALLOWED_EXTENSIONS:
        raise InvalidFileError(
            "Tipo de archivo no soportado. Formatos permitidos: PDF, MD y TXT."
        )
    return _EXTENSION_TO_TYPE[extension]


def validate_signature(file_type: FileType, content: bytes) -> None:
    """Comprueba la firma del archivo (un `.pdf` debe empezar con `%PDF-`).

    Lanza:
        InvalidFileError: si el contenido no corresponde al tipo declarado.
    """
    if file_type == "pdf" and b"%PDF-" not in content[:1024]:
        raise InvalidFileError("El archivo no es un PDF válido.")

