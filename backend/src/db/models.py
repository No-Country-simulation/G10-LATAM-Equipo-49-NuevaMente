"""Modelo de Job (DT-08) — persistencia de estado de sesión en SQLite.

No reemplaza a OCI (que persiste originales y resultados); complementa
guardando metadatos de documentos/jobs consultables sin ir a OCI. El JSON
de resultado se retiene en `result_json` para que `GET /adapt/{job_id}`
no necesite re-ejecutar el pipeline.
"""
from typing import Literal

from pydantic import BaseModel

JobStatus = Literal["QUEUED", "PROCESSING", "SUCCESS", "PARTIAL", "NO_CONTEXT", "ERROR"]


class Job(BaseModel):
    """Registro de una solicitud `POST /adapt` en curso o finalizada."""

    job_id: str
    document_id: str
    status: JobStatus
    result_object_name: str | None = None
    result_json: str | None = None
    error: str | None = None