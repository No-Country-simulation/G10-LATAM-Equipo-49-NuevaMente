from fastapi.testclient import TestClient
import time

from src.api.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_full_vertical_slice_ingest_and_adapt():
    # 1) Ingesta
    files = {"file": ("doc.txt", b"NuevaMente transforma documentacion tecnica. " * 50)}
    ingest_response = client.post("/ingest", files=files)
    assert ingest_response.status_code == 201
    document_id = ingest_response.json()["document_id"]

    # 2) Adaptación
    payload = {"document_id": document_id, "perfil": "principiante",
               "formato": "tutorial", "nivel_detalle": "estandar"}
    adapt_response = client.post("/adapt", json=payload)
    assert adapt_response.status_code == 202
    job_id = adapt_response.json()["job_id"]

    # 3) Polling hasta status final
    final = None
    for _ in range(20):
        result = client.get(f"/adapt/{job_id}")
        status = result.json().get("status")
        if status not in ("QUEUED", "PROCESSING"):
            final = result.json()
            break
        time.sleep(0.5)

    assert final is not None
    assert final["status"] in ("SUCCESS", "PARTIAL", "NO_CONTEXT")
    if final["status"] in ("SUCCESS", "PARTIAL"):
        assert "sources" in final["metadatos"]
        assert "fidelity_score" in final["evaluacion_calidad"]


def test_adapt_with_nonexistent_document_returns_error_status():
    payload = {"document_id": "doc_no_existe", "perfil": "developer",
               "formato": "resumen", "nivel_detalle": "breve"}
    adapt_response = client.post("/adapt", json=payload)
    job_id = adapt_response.json()["job_id"]

    time.sleep(1)
    result = client.get(f"/adapt/{job_id}")
    assert result.json().get("status") in ("NO_CONTEXT", "ERROR")


def test_same_document_different_profile_produces_different_output():
    files = {"file": ("doc2.txt", b"Contenido tecnico sobre arquitectura de microservicios. " * 60)}
    document_id = client.post("/ingest", files=files).json()["document_id"]

    job_a = client.post("/adapt", json={"document_id": document_id, "perfil": "principiante",
                                         "formato": "tutorial", "nivel_detalle": "estandar"}).json()["job_id"]
    job_b = client.post("/adapt", json={"document_id": document_id, "perfil": "ejecutivo",
                                         "formato": "resumen", "nivel_detalle": "breve"}).json()["job_id"]

    time.sleep(1.5)
    result_a = client.get(f"/adapt/{job_a}").json()
    result_b = client.get(f"/adapt/{job_b}").json()

    assert result_a["metadatos"]["profile"] != result_b["metadatos"]["profile"]
