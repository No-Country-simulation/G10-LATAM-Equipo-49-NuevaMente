"""Schemas HTTP de la API (Fase 6 del Plan Técnico).

Estos modelos son el contrato de entrada/salida de cada endpoint. No
contienen lógica; son composición de los schemas de dominio ya definidos
en `output/schema.py`, `db/models.py`, etc.
"""
from typing import Literal

from pydantic import BaseModel

FileType = Literal["pdf", "md", "txt"]


class IngestResponse(BaseModel):
    """201 — `POST /ingest`.

    Los tres primeros campos son el contrato de la Fase 6; el resto son
    extensiones opcionales (retrocompatibles) para mostrar el resumen en la UI.
    """

    document_id: str
    file_type: FileType
    status: Literal["INGESTED"] = "INGESTED"
    filename: str | None = None
    size_bytes: int | None = None
    page_count: int | None = None
    char_count: int | None = None
    chunk_count: int | None = None
    storage_object_name: str | None = None
    warnings: list[str] = []


class AdaptRequest(BaseModel):
    """`POST /adapt` — body JSON."""

    document_id: str
    perfil: str
    formato: str
    nicho: str | None = None
    nivel_detalle: str = "estandar"


class AdaptAcceptedResponse(BaseModel):
    """202 — `POST /adapt` (procesamiento asíncrono)."""

    job_id: str
    status: Literal["PROCESSING"] = "PROCESSING"


class JobPendingResponse(BaseModel):
    """202 — `GET /adapt/{job_id}` mientras el job no ha terminado."""

    job_id: str
    status: Literal["QUEUED", "PROCESSING"]


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Forma común de toda respuesta de error (400/404/500)."""

    error: ErrorDetail


class HealthResponse(BaseModel):
    """200 — `GET /health`."""

    status: Literal["ok"] = "ok"
