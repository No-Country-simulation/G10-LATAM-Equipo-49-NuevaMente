"""Verifica que un fallo de generación no produzca un resultado mock exitoso."""
from src.core.exceptions import LLMProviderError

from .conftest import ATLAS, ingestar


# CAMBIO H-02 INICIO — 2026-10-24
def test_error_de_generacion_no_se_presenta_como_fallback_mock(
    client, monkeypatch
) -> None:
    monkeypatch.setenv("LLM_PROVIDER", "cohere")
    monkeypatch.setenv("COHERE_API_KEY", "test-cohere-key")

    def _falla(self, request, contexto, provider):  # noqa: ANN001, ARG001
        raise LLMProviderError("Proveedor no disponible")

    monkeypatch.setattr(
        "src.api.orchestrator.GenerationOrchestrator.generate_content", _falla
    )
    document_id = ingestar(client, ATLAS)
    accepted = client.post(
        "/adapt",
        json={
            "document_id": document_id,
            "perfil": "Principiante / Transición de Carrera",
            "formato": "Guía Práctica Paso a Paso (Tutorial)",
            "nicho": "Fintech",
        },
    )
    assert accepted.status_code == 202

    result = client.get(f"/adapt/{accepted.json()['job_id']}")

    assert result.status_code == 500
    assert result.json()["error"]["code"] == "INTERNAL_ERROR"
# CAMBIO H-02 FIN — 2026-10-24
