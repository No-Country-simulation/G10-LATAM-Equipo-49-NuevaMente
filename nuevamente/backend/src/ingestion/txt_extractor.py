"""Extractor de texto plano (BE-ING-004, ING-009)."""
from src.core.exceptions import InvalidFileError
from src.ingestion.text_decoding import decode_text


def extract_txt_text(data: bytes) -> str:
    """Decodifica y valida un archivo de texto plano.

    Lanza:
        InvalidFileError: si el contenido no se puede decodificar o el texto
            resultante está vacío (ING-009).
    """
    text = decode_text(data, "de texto")
    if not text.strip():
        raise InvalidFileError("El archivo de texto está vacío.")
    return text
