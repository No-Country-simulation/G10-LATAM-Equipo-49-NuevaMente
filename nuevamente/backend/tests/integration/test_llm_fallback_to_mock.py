"""Test de integración: fallback a mock cuando todos los proveedores LLM fallan."""
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.core.config import get_settings
from src.generation.factory import get_llm_provider


@pytest.fixture(autouse=True)
def mock_env(monkeypatch: pytest.MonkeyPatch):
    """Configura mock providers para tests deterministas, pero permite LLM_PROVIDER=cohere."""
    monkeypatch.setenv("LLM_PROVIDER", "cohere")
    monkeypatch.setenv("COHERE_API_KEY", "test-cohere")
    monkeypatch.setenv("GEMINI_API_KEY", "test-gemini")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "mock")
    monkeypatch.setenv("VECTORSTORE_PROVIDER", "memory")
    monkeypatch.setenv("STORAGE_PROVIDER", "mock")
    get_settings.cache_clear()
    get_llm_provider.cache_clear()
    yield
    get_settings.cache_clear()
    get_llm_provider.cache_clear()


def test_full_flow_fallback_to_mock_when_llm_fails():
    """Pipeline completo con LLM fallando → status=PARTIAL y MOCK_NOTICE."""
    client = TestClient(app)

    # 1. Ingestar un documento
    content = b"Texto del documento de prueba para ingestar."
    response = client.post("/ingest", files={"file": ("test.txt", content, "text/plain")})
    assert response.status_code == 201
    doc_id = response.json()["document_id"]

    # 2. Pedir adaptación (el LLM fallará porque no hay API real, caerá a mock)
    response = client.post(
        "/adapt",
        json={
            "document_id": doc_id,
            "perfil": "Principiante / Transición de Carrera",
            "formato": "Guía Práctica Paso a Paso (Tutorial)",
            "nicho": "Fintech",
            "nivel_detalle": "estandar",
        },
    )
    assert response.status_code == 202
    job_id = response.json()["job_id"]

    # 3. Polling hasta que termine
    import time
    for _ in range(20):
        time.sleep(0.1)
        status_resp = client.get(f"/adapt/{job_id}")
        if status_resp.status_code != 202:
            break
    else:
        pytest.fail("Job no terminó a tiempo")

    # 4. Verificar que terminó con PARTIAL y MOCK_NOTICE
    assert status_resp.status_code == 200
    data = status_resp.json()
    assert data["status"] == "PARTIAL"
    assert any("mock" in obs.lower() for obs in data["evaluacion_calidad"]["observaciones"])
    assert data["contenido_adaptado"]["cuerpo"] != ""