from src.core.exceptions import InvalidFileError


def extract_markdown_text(data: bytes) -> str:
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidFileError("El archivo Markdown no es UTF-8 válido") from exc
    if not text.strip():
        raise InvalidFileError("El archivo Markdown está vacío")
    return text
