"""Flujo completo /ingest → /adapt → /adapt/{job_id} (QA-003, TEST-INT-001).

Hermético y determinista: el conftest fuerza mock embeddings/LLM y
`MockStorageClient`, por lo que no hay red ni credenciales OCI.
"""
from src.api.schemas import AdaptRequest


def _adapt(doc_id: str, perfil: str = "python") -> dict:
    return AdaptRequest(document_id=doc_id, perfil=perfil, formato="tutorial").model_dump()


def test_ingest_adapt_result(client):
    # 1. /ingest
    resp = client.post(
        "/ingest",
        files={
            "file": (
                "python.txt",
                b"python es un lenguaje de programacion popular",
                "text/plain",
            )
        },
    )
    assert resp.status_code == 201, resp.text
    doc_id = resp.json()["document_id"]
    assert resp.json()["status"] == "INGESTED"

    # 2. /adapt → 202 con job_id
    resp = client.post("/adapt", json=_adapt(doc_id))
    assert resp.status_code == 202, resp.text
    job_id = resp.json()["job_id"]

    # 3. /adapt/{job_id} → resultado
    resp = client.get(f"/adapt/{job_id}")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    # SUCCESS o PARTIAL: el score de fidelidad mock no es determinista al 100%
    assert body["status"] in {"SUCCESS", "PARTIAL"}
    assert body["metadatos"]["doc_id"] == doc_id
    assert body["contenido_adaptado"]["cuerpo"]


def test_adapt_documento_inexistente(client):
    resp = client.post("/adapt", json=_adapt("no-existe", perfil="x"))
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_job_inexistente(client):
    resp = client.get("/adapt/abcdef")
    assert resp.status_code == 404
    assert resp.json()["error"]["code"] == "DOCUMENT_NOT_FOUND"


def test_ingest_extension_invalida(client):
    resp = client.post(
        "/ingest",
        files={"file": ("malo.exe", b"contenido", "application/octet-stream")},
    )
    assert resp.status_code == 400
    assert resp.json()["error"]["code"] == "INVALID_FILE"


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}