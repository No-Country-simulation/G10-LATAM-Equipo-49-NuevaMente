"""Modelos de datos de Ingestion (COMP-01).

Contratos de entrada/salida usados por `router.py` y los extractores.
Fuente: Plan Técnico, COMP-01 (Fase 5) y RF-001..RF-004.
"""
from typing import Literal

from pydantic import BaseModel

FileType = Literal["pdf", "md", "txt"]


class PageText(BaseModel):
    """Texto extraído de una página física del documento (solo aplica a PDF).

    Necesario para construir `sources: [{chunk_id, page}]` (Fase 6, RNF-006).
    Puede tener `text` vacío si la página no contiene texto extraíble.
    """

    page: int
    text: str


class IngestResult(BaseModel):
    """Resultado de una ingesta exitosa (COMP-01 → salida).

    Corresponde a `{raw_text, file_type, source_metadata}` de la Fase 5, con
    `document_id` agregado (se asigna en `router.py`) y `warnings` para las
    advertencias no fatales (p. ej. páginas de un PDF sin texto, RF-001).
    """

    document_id: str
    file_type: FileType
    raw_text: str
    pages: list[PageText] = []
    filename: str
    warnings: list[str] = []
