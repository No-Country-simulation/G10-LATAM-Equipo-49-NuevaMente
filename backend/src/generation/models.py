"""Modelos de dominio de Generation (COMP-06).

Fuente: RF-009..RF-013 (adaptación por perfil/formato/nicho/detalle) y
Fase 6 (`ContenidoAdaptado`, reutilizado también por `output/schema.py`).
"""
from typing import Literal

from pydantic import BaseModel

# Los 4 perfiles y ≥2 formatos MVP están definidos en `profiles.py` — aquí
# se usan como str libres para no acoplar el contrato al catálogo exacto,
# que puede crecer (GEN-006, GEN-007) sin romper este schema.

NivelDetalle = Literal["breve", "estandar", "profundo"]


class AdaptationRequest(BaseModel):
    """Parámetros de una solicitud de generación adaptada."""

    document_id: str
    perfil: str
    formato: str
    nicho: str | None = None
    nivel_detalle: NivelDetalle = "estandar"


class ContenidoAdaptado(BaseModel):
    """Salida de la generación — ver también `output/schema.py`, donde se
    reutiliza como submodelo de `NuevaMenteOutput` (Fase 6).
    """

    cuerpo: str
    conceptos_clave: list[str] = []
    prerrequisitos: list[str] = []
    tiempo_estimado_min: int | None = None
