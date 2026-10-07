"""Validación de fidelidad — LLM como juez + score determinista
(BE-VAL-002b/c, DT-05, VAL-005).

Reglas (Plan Técnico, Fase 14):
    - EL LLM-juez SOLO devuelve SI/NO/PARCIAL (PROMPT-002, temperatura 0).
    - Cualquier respuesta fuera de esas 3 opciones se trata como PARCIAL.
    - El score final se calcula en Python (determinista), no lo decide el LLM.
    - Si el LLM-juez falla para un claim, ese claim se excluye (anotado en
      `observaciones`).
    - Si el LLM-juez falla por completo, `score=None` (VAL-005) — nunca se
      "inventa" un score ni se afirma "0% de alucinaciones".

Implementación actual: verificación mock por solapamiento de tokens con la
fuente (portada de la demo de Fase 1). `aggregate_score` es el mismo
cómputo determinista que usará el pipeline real.
"""
import re

from src.validation.claims_extractor import extract_claims
from src.validation.models import ClaimEvaluation, FidelityEvaluation


def _tokens(texto: str) -> set[str]:
    return set(re.findall(r"\w+", texto.lower()))


def verify_claim(*, claim_text: str, contexto_fuente: str) -> ClaimEvaluation:
    """Verdicto mock determinista por solapamiento de tokens."""
    compartidos = _tokens(claim_text) & _tokens(contexto_fuente)
    if not compartidos:
        return ClaimEvaluation(claim={"text": claim_text}, veredicto="NO")
    ratio = len(compartidos) / max(1, len(_tokens(claim_text)))
    return ClaimEvaluation(
        claim={"text": claim_text},
        veredicto="SI" if ratio >= 0.5 else "PARCIAL",
    )


def aggregate_score(evaluations: list[ClaimEvaluation]) -> float | None:
    """Calcula `fidelidad_score` en [0,1]. `None` si `evaluations` está vacía
    (caso VAL-005: el LLM-juez falló en todos los claims)."""
    if not evaluations:
        return None
    pesos = {"SI": 1.0, "PARCIAL": 0.5, "NO": 0.0}
    return round(sum(pesos[e.veredicto] for e in evaluations) / len(evaluations), 2)


class DefaultValidationService:
    """Implementación de `ValidationService` compone `extract_claims` +
    verificación (mock por overlap) + `aggregate_score`."""

    def validate(self, contenido_generado: str, contexto_fuente: str) -> FidelityEvaluation:
        claims = extract_claims(contenido_generado)
        evaluations = [
            verify_claim(claim_text=c.text, contexto_fuente=contexto_fuente) for c in claims
        ]
        score = aggregate_score(evaluations)
        no_soportados = [
            e.claim.text for e in evaluations if e.veredicto == "NO"
        ]
        return FidelityEvaluation(
            score=score if score is not None else None,
            claims_no_soportados=no_soportados,
            observaciones=[] if score is not None else ["LLM-juez no disponible (VAL-005)"],
        )
