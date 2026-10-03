"""Modelos de dominio de Generation (COMP-06).

Fuente: RF-009..RF-013 (adaptación por perfil/formato/nicho) y
Fase 6 (`ContenidoAdaptado`, reutilizado también por `output/schema.py`).
"""
from pydantic import BaseModel

from src.generation.profiles import FormatoSalida, NichoSector, PerfilDestinatario


class AdaptationRequest(BaseModel):
    """Parámetros de una solicitud de generación adaptada."""

    document_id: str
    perfil: PerfilDestinatario
    formato: FormatoSalida
    nicho: NichoSector = "General"


class ContenidoAdaptado(BaseModel):
    """Salida de la generación — ver también `output/schema.py`, donde se
    reutiliza como submodelo de `NuevaMenteOutput` (Fase 6).
    """

    cuerpo: str
    conceptos_clave: list[str] = []
    prerrequisitos: list[str] = []
    tiempo_estimado_min: int | None = None
