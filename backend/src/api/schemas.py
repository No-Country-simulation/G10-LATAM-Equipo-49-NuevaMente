"""Schemas HTTP de la API (Fase 6 del Plan Técnico).

Estos modelos son el contrato de entrada/salida de cada endpoint. No
contienen lógica; son composición de los schemas de dominio ya definidos
en `output/schema.py`, `db/models.py`, etc.
"""
from typing import Literal
from pydantic import BaseModel

FileType = Literal["pdf", "md", "txt"]


class IngestResponse(BaseModel):
    """201 — `POST /ingest`."""

    document_id: str
    file_type: FileType
    status: Literal["INGESTED"] = "INGESTED"


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


class ErrorDetail(BaseModel):
    code: str
    message: str


class ErrorResponse(BaseModel):
    """Forma común de toda respuesta de error (400/404/500)."""

    error: ErrorDetail


class HealthResponse(BaseModel):
    """200 — `GET /health`."""

    status: Literal["ok"] = "ok"
