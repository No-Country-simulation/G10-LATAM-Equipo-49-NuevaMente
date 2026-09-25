from src.core.exceptions import InvalidFileError


def extract_txt_text(data: bytes) -> str:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidFileError("El archivo de texto no es UTF-8 válido") from exc
    if not text.strip():
        raise InvalidFileError("El archivo de texto está vacío")
    return text
