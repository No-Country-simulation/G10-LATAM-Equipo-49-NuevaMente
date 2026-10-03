"""Validación de fidelidad — LLM como juez + score determinista
(BE-VAL-002b/c, DT-05, VAL-005).

Reglas de diseño (Plan Técnico, Fase 14):
    - El LLM-juez SOLO devuelve SI/NO/PARCIAL (PROMPT-002, temperatura 0).
    - Cualquier respuesta fuera de esas 3 opciones se trata como PARCIAL.
    - El score final se calcula en Python (determinista), no lo decide el LLM.
    - Si el LLM-juez falla para un claim, ese claim se excluye del cálculo
      y se anota en `observaciones` (nunca cuenta como soportado ni no
      soportado).
    - Si el LLM-juez falla por completo, `score=None` (VAL-005) — nunca se
      "inventa" un score ni se afirma "0% de alucinaciones".
"""
from src.generation.llm_provider import LLMProvider
from src.validation.models import Claim, ClaimEvaluation, FidelityEvaluation


def verify_claim(provider: LLMProvider, claim: Claim, contexto_fuente: str) -> ClaimEvaluation:
    """Invoca PROMPT-002 sobre un único `claim` y normaliza el veredicto.

    Implementación futura.
    """
    ...


def aggregate_score(evaluations: list[ClaimEvaluation]) -> float | None:
    """Calcula `fidelidad_score` en [0,1] a partir de los veredictos
    (determinista — DT-05). `None` si `evaluations` está vacía por fallos
    del LLM-juez en todos los claims (VAL-005).

    Implementación futura.
    """
    ...


class DefaultValidationService:
    """Implementación futura de `ValidationService`, compone
    `claims_extractor.extract_claims` + `verify_claim` + `aggregate_score`.
    """

    def validate(self, contenido_generado: str, contexto_fuente: str) -> FidelityEvaluation:
        ...
# Nota: cumple el Protocol correspondiente por forma estructural (duck typing).
# No se usa issubclass() en importación: el Protocol no es @runtime_checkable.
