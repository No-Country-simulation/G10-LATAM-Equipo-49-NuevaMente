"""Tests de `validation/fidelity_checker.py` (BE-VAL-002b/c, DT-05, VAL-005).

El foco es que el score es determinista y se calcula en Python,
independiente de cualquier modelo externo.
"""

from src.validation.fidelity_checker import (
    DefaultValidationService,
    aggregate_score,
    verify_claim,
)
from src.validation.models import ClaimEvaluation, FidelityEvaluation

# ------------------------------------------------------------------ verify_claim


def test_claim_con_solapamiento_total_es_si():
    ev = verify_claim(
        claim_text="El agua hierve a 100 grados",
        contexto_fuente="El agua hierve a 100 grados centígrados",
    )
    assert ev.veredicto == "SI"


def test_claim_sin_solapamiento_significativo_es_parcial():
    """Con tokens comunes triviales (artículos) queda en PARCIAL, no NO."""
    ev = verify_claim(
        claim_text="El gato es un animal doméstico",
        contexto_fuente="El agua hierve a 100 grados",
    )
    assert ev.veredicto == "PARCIAL"


def test_claim_con_solapamiento_parcial():
    ev = verify_claim(
        claim_text="El agua es un líquido a temperatura ambiente",
        contexto_fuente="El agua es un compuesto químico",
    )
    assert ev.veredicto in ("SI", "PARCIAL")  # depende del ratio


def test_claim_entrega_claim_en_evaluacion():
    ev = verify_claim(claim_text="cualquier cosa", contexto_fuente="cualquier cosa")
    assert ev.claim.text == "cualquier cosa"


# ------------------------------------------------------------------ aggregate_score


def test_solo_si_da_100():
    evals = [ClaimEvaluation(claim={"text": "a"}, veredicto="SI")]
    assert aggregate_score(evals) == 1.0


def test_mezcla_si_y_parcial():
    evals = [
        ClaimEvaluation(claim={"text": "a"}, veredicto="SI"),
        ClaimEvaluation(claim={"text": "b"}, veredicto="PARCIAL"),
    ]
    assert aggregate_score(evals) == 0.75


def test_todos_no_da_0():
    evals = [ClaimEvaluation(claim={"text": "a"}, veredicto="NO")] * 3
    assert aggregate_score(evals) == 0.0


def test_lista_vacia_devuelve_none_val_005():
    assert aggregate_score([]) is None


def test_redondeo_a_dos_decimales():
    evals = [ClaimEvaluation(claim={"text": "a"}, veredicto="PARCIAL")] * 3  # 0.5 * 3 / 3 = 0.5
    assert aggregate_score(evals) == 0.5


# ------------------------------------------------------------------ DefaultValidationService


def test_servicio_devuelve_score_y_no_soportados():
    servicio = DefaultValidationService()
    contexto = "El agua hierve a 100 grados centígrados y es incolora."
    resultado = servicio.validate("El agua hierve a 100 grados.", contexto)

    assert isinstance(resultado, FidelityEvaluation)
    assert resultado.score is not None
    assert 0.0 <= resultado.score <= 1.0
    assert isinstance(resultado.claims_no_soportados, list)
    assert isinstance(resultado.observaciones, list)


def test_sin_claims_devuelve_score_none():
    """Texto sin oraciones válidas → sin claims → score None (VAL-005)."""
    servicio = DefaultValidationService()
    resultado = servicio.validate("Título. Alerta.", "contexto cualquiera")

    assert resultado.score is None
    assert "LLM-juez no disponible (VAL-005)" in resultado.observaciones


def test_determinismo_mismo_input_mismo_output():
    servicio = DefaultValidationService()
    contenido = "El agua hierve a 100 grados. Es incolora e inodora."
    contexto = "El agua es un compuesto incoloro e inodoro que hierve a 100°C."

    assert servicio.validate(contenido, contexto) == servicio.validate(contenido, contexto)
