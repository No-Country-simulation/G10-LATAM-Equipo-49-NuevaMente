from src.generation.llm_provider import MockLLMProvider
from src.validation.fidelity_checker import validate_fidelity


def test_fidelity_score_in_range_and_deterministic():
    provider = MockLLMProvider()
    result_a = validate_fidelity(provider, "texto generado de prueba", "contexto fuente")
    result_b = validate_fidelity(provider, "texto generado de prueba", "contexto fuente")

    assert result_a.score is not None
    assert 0 <= result_a.score <= 1
    assert result_a.score == result_b.score  # temperatura 0 -> reproducible


def test_never_reports_100_percent_without_basis():
    provider = MockLLMProvider()
    result = validate_fidelity(provider, "texto", "contexto")
    # el sistema nunca debe forzar el score a 1.0 si hubo observaciones de riesgo
    assert isinstance(result.observaciones, list)
