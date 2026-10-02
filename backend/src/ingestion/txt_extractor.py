"""Extractor de texto plano (BE-ING-004, ING-009)."""
from src.core.exceptions import InvalidFileError


def extract_txt_text(data: bytes) -> str:
    """Decodifica y valida un archivo de texto plano.

    Lanza `InvalidFileError` si el contenido no es UTF-8 válido o si el
    texto resultante está vacío (ING-009).
    """
    try:
        texto = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidFileError(f"El texto no es UTF-8 válido: {exc}") from exc
    if not texto.strip():
        raise InvalidFileError("El archivo de texto está vacío")
    return texto