"""Schema formal de salida — NuevaMenteOutput (BE-OUT-002, TASK-003, DT-06).

Contrato tomado literalmente de la Fase 6 del Plan Técnico. Es EL contrato
más importante del sistema: una vez implementado (TASK-003 en DONE), "no
se congela a mitad de proyecto en silencio" — cualquier cambio debe
revisarse contra todos los consumidores (`api/main.py`,
`ui/components/result_view.py`, tests de integración).

`ContenidoAdaptado` se reutiliza desde `generation.models` (única definición).
"""
from typing import Literal

from pydantic import BaseModel, field_validator

from src.generation.models import ContenidoAdaptado

Status = Literal["SUCCESS", "PARTIAL", "NO_CONTEXT", "ERROR"]


class Source(BaseModel):
    """Referencia a un chunk fuente usado en la generación (RNF-006)."""

    chunk_id: str
    page: int | None = None


class Metadatos(BaseModel):
    doc_id: str
    perfil: str
    formato: str
    nicho: str | None = None
    nivel_detalle: str
    sources: list[Source] = []


class EvaluacionCalidad(BaseModel):
    """`fidelidad_score` es `None` si el LLM-juez falló (VAL-005) — nunca
    se fuerza a 1.0 ni se afirma "0% de alucinaciones" (RF-014).
    """

    fidelidad_score: float | None = None
    claims_no_soportados: list[str] = []
    dificultad: str | None = None
    observaciones: list[str] = []

    @field_validator("fidelidad_score")
    @classmethod
    def score_en_rango(cls, value: float | None) -> float | None:
        """Exige `0 <= value <= 1` cuando no es `None`."""
        if value is not None and not 0.0 <= value <= 1.0:
            raise ValueError("fidelidad_score debe estar entre 0 y 1")
        return value


class AlmacenamientoOCI(BaseModel):
    bucket: str
    object_name_original: str | None = None
    object_name_json: str | None = None
    uploaded_at: str | None = None


class NuevaMenteOutput(BaseModel):
    """Contrato completo de `GET /adapt/{job_id}` (Fase 6).

    `contenido_adaptado` y `almacenamiento_oci` son opcionales porque
    `status="NO_CONTEXT"` o `status="ERROR"` pueden no llegar a producirlos.
    """

    status: Status
    metadatos: Metadatos
    contenido_adaptado: ContenidoAdaptado | None = None
    evaluacion_calidad: EvaluacionCalidad
    almacenamiento_oci: AlmacenamientoOCI | None = None
