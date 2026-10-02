"""Modelos de persistencia de sesión (DT-08) — SQLite.

No reemplaza al almacenamiento de objetos (que guarda originales y
resultados); complementa guardando metadatos de documentos y jobs
consultables sin ir al bucket.
"""
from typing import Literal

from pydantic import BaseModel

JobStatus = Literal["QUEUED", "PROCESSING", "SUCCESS", "PARTIAL", "NO_CONTEXT", "ERROR"]

FINAL_STATUSES: tuple[str, ...] = ("SUCCESS", "PARTIAL", "NO_CONTEXT", "ERROR")


class Job(BaseModel):
    """Registro de una solicitud `POST /adapt` en curso o finalizada."""

    job_id: str
    document_id: str
    status: JobStatus
    result_object_name: str | None = None
    result_json: str | None = None
    error: str | None = None


class DocumentRecord(BaseModel):
    """Metadatos de un documento ingerido (RF-001)."""

    document_id: str
    filename: str
    file_type: str
    size_bytes: int
    page_count: int = 0
    char_count: int = 0
    chunk_count: int = 0
    storage_object_name: str | None = None
    warnings: list[str] = []
    created_at: str