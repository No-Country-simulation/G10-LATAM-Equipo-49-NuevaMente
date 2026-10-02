"""Tests de fidelidad (QA-004, determinismo de `aggregate_score`)."""
from src.validation.fidelity_checker import DefaultValidationService, aggregate_score, verify_claim
from src.validation.models import ClaimEvaluation


def test_aggregate_score_todo_soportado():
    evals = [
        ClaimEvaluation(claim={"text": "x"}, veredicto="SI"),
        ClaimEvaluation(claim={"text": "y"}, veredicto="SI"),
    ]
    assert aggregate_score(evals) == 1.0


def test_aggregate_score_parcial():
    evals = [
        ClaimEvaluation(claim={"text": "x"}, veredicto="SI"),
        ClaimEvaluation(claim={"text": "y"}, veredicto="NO"),
    ]
    assert aggregate_score(evals) == 0.5


def test_aggregate_score_vacio_devuelve_none():
    assert aggregate_score([]) is None


def test_verify_claim_solapamiento():
    soportado = verify_claim(
        claim_text="El gato juega con la pelota",
        contexto_fuente="El gato juega con la pelota roja",
    )
    assert soportado.veredicto == "SI"
    no_soportado = verify_claim(
        claim_text="Elefantes vuelan siempre espacio",
        contexto_fuente="El gato juega",
    )
    assert no_soportado.veredicto == "NO"


def test_validation_service_score_en_rango():
    svc = DefaultValidationService()
    res = svc.validate(
        "El gato juega con la pelota.",
        "El gato juega con la pelota roja todos los días.",
    )
    assert res.score is None or 0.0 <= res.score <= 1.0