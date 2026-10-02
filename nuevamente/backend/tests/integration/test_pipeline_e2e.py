"""CU-001/CU-002 — flujo POST /ingest → POST /adapt → GET /adapt/{job_id} (mock)."""
from src.db.session import create_job, update_job_status
from src.output.schema import NuevaMenteOutput

DOC = "# Contenedores\n\n" + " ".join(f"concepto{i}" for i in range(900))


def _ingest(client, name: str = "guia.md", text: str = DOC) -> dict:
    response = client.post("/ingest", files={"file": (name, text.encode(), "text/markdown")})
    assert response.status_code == 201
    return response.json()


def _adapt(client, document_id: str, **overrides):
    payload = {"document_id": document_id, "perfil": "principiante", "formato": "tutorial"}
    payload.update(overrides)
    return client.post("/adapt", json=payload)


def test_full_flow_returns_valid_partial_output(client, storage_dir):
    document = _ingest(client)

    accepted = _adapt(client, document["document_id"], nicho="cloud computing")
    assert accepted.status_code == 202
    assert accepted.json()["status"] == "PROCESSING"
    job_id = accepted.json()["job_id"]

    result = client.get(f"/adapt/{job_id}")
    assert result.status_code == 200
    body = result.json()
    output = NuevaMenteOutput.model_validate(body)

    assert output.status == "PARTIAL"
    assert output.metadatos.doc_id == document["document_id"]
    assert output.metadatos.nicho == "cloud computing"
    assert output.evaluacion_calidad.fidelidad_score is None
    assert output.evaluacion_calidad.observaciones
    assert "concepto0" in output.contenido_adaptado.cuerpo
    assert output.metadatos.sources
    assert all(s.chunk_id.startswith(document["document_id"]) for s in output.metadatos.sources)

    storage = output.almacenamiento_oci
    assert storage.object_name_json.startswith(f"generated/{document['document_id']}/")
    assert storage.object_name_original == document["storage_object_name"]
    assert (storage_dir / storage.object_name_json).exists()


def test_detail_level_controls_number_of_sources(client):
    document_id = _ingest(client)["document_id"]
    counts = {}
    for level in ("breve", "estandar", "profundo"):
        job_id = _adapt(client, document_id, nivel_detalle=level).json()["job_id"]
        counts[level] = len(client.get(f"/adapt/{job_id}").json()["metadatos"]["sources"])
    assert counts == {"breve": 1, "estandar": 3, "profundo": 5}


def test_same_document_can_be_adapted_with_other_profile(client):
    document_id = _ingest(client)["document_id"]
    first = _adapt(client, document_id, perfil="principiante").json()["job_id"]
    second = _adapt(client, document_id, perfil="ejecutivo", formato="resumen_ejecutivo")
    second_id = second.json()["job_id"]

    assert first != second_id
    assert client.get(f"/adapt/{second_id}").json()["metadatos"]["perfil"] == "ejecutivo"
    assert client.get(f"/adapt/{first}").json()["metadatos"]["perfil"] == "principiante"


def test_unknown_document_is_404(client):
    response = _adapt(client, "doc_inexistente")
    assert response.status_code == 404
    assert response.json() == {
        "error": {
            "code": "DOCUMENT_NOT_FOUND",
            "message": "No existe un documento indexado con ese document_id",
        }
    }


def test_invalid_parameters_are_400(client):
    document_id = _ingest(client)["document_id"]
    for overrides in ({"perfil": "pirata"}, {"formato": "poema"}, {"nivel_detalle": "extremo"}):
        response = _adapt(client, document_id, **overrides)
        assert response.status_code == 400
        assert response.json()["error"]["code"] == "INVALID_REQUEST"


def test_missing_fields_are_422(client):
    response = client.post("/adapt", json={"document_id": "doc_x"})
    assert response.status_code == 422
    assert response.json()["error"]["code"] == "INVALID_REQUEST"


def test_unknown_job_is_404(client):
    response = client.get("/adapt/job_inexistente")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "JOB_NOT_FOUND"


def test_pending_job_returns_202(client):
    job = create_job("doc_x")
    response = client.get(f"/adapt/{job.job_id}")
    assert response.status_code == 202
    assert response.json() == {"job_id": job.job_id, "status": "QUEUED"}


def test_failed_job_returns_500_with_error_payload(client):
    job = create_job("doc_x")
    update_job_status(job.job_id, "ERROR", "falló la generación")
    response = client.get(f"/adapt/{job.job_id}")
    assert response.status_code == 500
    assert response.json() == {
        "error": {"code": "INTERNAL_ERROR", "message": "falló la generación"}
    }
