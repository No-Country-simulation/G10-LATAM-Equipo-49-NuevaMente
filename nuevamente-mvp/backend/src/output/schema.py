from typing import Literal
from pydantic import BaseModel, Field


class Source(BaseModel):
    chunk_id: str
    page: int | None = None


class Metadata(BaseModel):
    doc_id: str
    profile: str
    format: str
    niche: str | None = None
    detail_level: str
    sources: list[Source]


class GeneratedContentOut(BaseModel):
    titulo: str
    cuerpo: str
    conceptos_clave: list[str]
    prerrequisitos: list[str]
    tiempo_estimado_min: int
    dificultad: Literal["baja", "media", "alta"]


class QualityEvaluation(BaseModel):
    fidelity_score: float | None = Field(default=None, ge=0, le=1)
    claims_no_soportados: list[str] = []
    observaciones: list[str] = []


class OCIStorage(BaseModel):
    bucket: str | None = None
    object_name_json: str | None = None
    uploaded_at: str | None = None


class NuevaMenteOutput(BaseModel):
    status: Literal["SUCCESS", "PARTIAL", "NO_CONTEXT", "ERROR"]
    metadatos: Metadata
    contenido_adaptado: GeneratedContentOut | None = None
    evaluacion_calidad: QualityEvaluation
    almacenamiento_oci: OCIStorage | None = None
