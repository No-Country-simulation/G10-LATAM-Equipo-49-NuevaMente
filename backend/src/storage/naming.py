"""Convención de nombres de objeto (DT-07): `{tipo}/{doc_id}/{timestamp}_{nombre}`."""
import re
from datetime import UTC, datetime

_MAX_NAME_LEN = 120


def sanitize_filename(name: str) -> str:
    """Deja solo el nombre base y caracteres seguros (evita rutas y `..`)."""
    base = name.replace("\\", "/").rsplit("/", 1)[-1]
    base = re.sub(r"[^A-Za-z0-9._-]+", "_", base).lstrip(".")
    return base[-_MAX_NAME_LEN:] or "archivo"


def build_object_name(
    tipo: str, doc_id: str, nombre: str, now: datetime | None = None
) -> str:
    """Construye `{tipo}/{doc_id}/{timestamp}_{nombre}` (timestamp UTC sin ':')."""
    stamp = (now or datetime.now(UTC)).strftime("%Y%m%dT%H%M%SZ")
    return f"{tipo}/{doc_id}/{stamp}_{sanitize_filename(nombre)}"