"""Limpieza de texto normalizado (PROC-003)."""
import re

_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_MULTISPACE = re.compile(r"[ \t]+")
_MULTILINE = re.compile(r"\n{3,}")


def clean_text(raw_text: str) -> str:
    """Normaliza espacios, elimina caracteres de control y colapsa saltos
    de línea repetidos y encabezados duplicados."""
    texto = _CONTROL.sub("", raw_text)
    texto = _MULTISPACE.sub(" ", texto)
    texto = _MULTILINE.sub("\n\n", texto)
    return texto.strip()