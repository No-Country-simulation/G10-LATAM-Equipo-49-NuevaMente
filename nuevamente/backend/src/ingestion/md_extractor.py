"""Extractor de Markdown (BE-ING-003, ING-008)."""
from src.core.exceptions import InvalidFileError
from src.ingestion.text_decoding import decode_text


def extract_markdown_text(data: bytes) -> str:
    """Decodifica y valida un archivo Markdown.

    Lanza:
        InvalidFileError: si el contenido no se puede decodificar o, una vez
            decodificado, el texto está vacío (ING-008).
    """
    text = decode_text(data, "Markdown")
    if not text.strip():
        raise InvalidFileError("El archivo Markdown está vacío.")
    return text
