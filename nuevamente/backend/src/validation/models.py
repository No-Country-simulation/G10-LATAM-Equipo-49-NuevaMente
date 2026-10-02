"""Modelos de dominio de Validation (COMP-07). Fuente: RF-014, DT-05."""
from typing import Literal

from pydantic import BaseModel

Veredicto = Literal["SI", "NO", "PARCIAL"]


class Claim(BaseModel):
    """Afirmación individual extraída del contenido generado (VAL-001)."""

    text: str


class ClaimEvaluation(BaseModel):
    """Resultado de contrastar un `Claim` contra el contexto fuente
    (PROMPT-002) — el LLM-juez solo devuelve el veredicto; el peso
    numérico de cada veredicto se define en la implementación (DT-05:
    "el score se calcula en Python, no lo decide el modelo").
    """

    claim: Claim
    veredicto: Veredicto


class FidelityEvaluation(BaseModel):
    """Resultado agregado de la validación de fidelidad (RF-014).

    `score` es `None` si el LLM-juez falló (VAL-005) — nunca se inventa un
    valor en ese caso.
    """

    score: float | None = None
    claims_no_soportados: list[str] = []
    observaciones: list[str] = []

