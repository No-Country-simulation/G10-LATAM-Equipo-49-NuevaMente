"""Extractor de Markdown (BE-ING-003, ING-008)."""
from src.core.exceptions import InvalidFileError


def extract_markdown_text(data: bytes) -> str:
    """Decodifica y valida un archivo Markdown.

    Lanza `InvalidFileError` si el contenido no es UTF-8 válido o si el
    texto resultante está vacío (ING-008).
    """
    try:
        texto = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidFileError(f"El Markdown no es UTF-8 válido: {exc}") from exc
    if not texto.strip():
        raise InvalidFileError("El contenido Markdown está vacío")
    return texto