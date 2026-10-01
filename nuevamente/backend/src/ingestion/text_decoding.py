"""Decodificación de archivos de texto (BE-ING-003, BE-ING-004)."""
from src.core.exceptions import InvalidFileError


def decode_text(data: bytes, label: str) -> str:
    """Decodifica `data` como UTF-8 (con o sin BOM) o, si falla, Windows-1252.

    Lanza:
        InvalidFileError: si no se puede decodificar o el contenido parece binario.
    """
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            text = data.decode(encoding)
            break
        except UnicodeDecodeError:
            continue
    else:
        raise InvalidFileError(
            f"No fue posible leer el archivo {label}: guárdelo con codificación UTF-8."
        )

    if "\x00" in text:
        raise InvalidFileError(f"El archivo {label} parece binario, no es texto válido.")
    return text