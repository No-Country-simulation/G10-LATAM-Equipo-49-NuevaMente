"""Modelos de dominio de Generation (COMP-06).

Fuente: RF-009..RF-013 (adaptación por perfil/formato/nicho) y
Fase 6 (`ContenidoAdaptado`, reutilizado también por `output/schema.py`).
"""
from pydantic import BaseModel, Field, field_validator

from src.generation.profiles import FormatoSalida, NichoSector, PerfilDestinatario


class AdaptationRequest(BaseModel):
    """Parámetros de una solicitud de generación adaptada."""

    document_id: str
    perfil: PerfilDestinatario
    formato: FormatoSalida
    nicho: NichoSector = "General"


# CAMBIO H-05 INICIO — 2026-10-24
class PasoGuia(BaseModel):
    """Schema de pasos para tutoriales (H-05)."""

    numero: int
    titulo: str
    descripcion: str


class Flashcard(BaseModel):
    """Schema frente/dorso para flashcards (H-05)."""

    frente: str
    dorso: str


class PreguntaQuiz(BaseModel):
    """Schema de pregunta, opciones y justificación para quiz (H-05)."""

    pregunta: str
    opciones: list[str]
    respuesta_correcta: str
    justificacion: str


class EscenaGuion(BaseModel):
    """Schema de escena para guiones de clase o video (H-05)."""

    numero: int
    titulo: str
    contenido: str
    minuto: str | None = None


class ContenidoAdaptado(BaseModel):
    """Salida de generación con campos específicos para los cinco formatos (H-05).

    Ver también `output/schema.py`, donde se reutiliza como submodelo de
    `NuevaMenteOutput` (Fase 6).
    """

    cuerpo: str
    conceptos_clave: list[str] = Field(default_factory=list)
    prerrequisitos: list[str] = Field(default_factory=list)
    tiempo_estimado_min: int | None = None
    pasos: list[PasoGuia] = Field(default_factory=list)
    tarjetas: list[Flashcard] = Field(default_factory=list)
    preguntas: list[PreguntaQuiz] = Field(default_factory=list)
    resumen_ejecutivo: str | None = None
    escenas: list[EscenaGuion] = Field(default_factory=list)

    @field_validator("cuerpo")
    @classmethod
    def cuerpo_no_vacio(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("cuerpo no puede estar vacío")
        return value
# CAMBIO H-05 FIN — 2026-10-24



