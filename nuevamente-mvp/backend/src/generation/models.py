from typing import Literal
from pydantic import BaseModel


class GenerationRequest(BaseModel):
    context: str
    profile: Literal["principiante", "developer", "lider_tecnico", "ejecutivo"]
    format: Literal["tutorial", "flashcards", "resumen", "quiz"]
    niche: str | None = None
    detail_level: Literal["breve", "estandar", "profundo"]


class GeneratedContent(BaseModel):
    titulo: str
    cuerpo: str
    conceptos_clave: list[str]
    prerrequisitos: list[str]
    tiempo_estimado_min: int
    dificultad: Literal["baja", "media", "alta"]
