from typing import Literal
from pydantic import BaseModel


class IngestResponse(BaseModel):
    document_id: str
    file_type: str
    status: Literal["INGESTED"]


class AdaptRequest(BaseModel):
    document_id: str
    perfil: Literal["principiante", "developer", "lider_tecnico", "ejecutivo"]
    formato: Literal["tutorial", "flashcards", "resumen", "quiz"]
    nicho: str | None = None
    nivel_detalle: Literal["breve", "estandar", "profundo"] = "estandar"


class AdaptAcceptedResponse(BaseModel):
    job_id: str
    status: Literal["PROCESSING"]


class ErrorResponse(BaseModel):
    error: dict
