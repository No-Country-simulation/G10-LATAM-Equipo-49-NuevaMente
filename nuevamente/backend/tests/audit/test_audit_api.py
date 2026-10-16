"""Pruebas a nivel HTTP (requieren FastAPI + httpx: `pip install -r requirements-dev.txt`).

Cubren el mismo contrato que `test_audit_rag.py`, pero atravesando la capa HTTP real.
NO se pudieron ejecutar en el entorno de auditoría (sin acceso a internet).
"""
from tests.audit._support import DOC_CLOUD, FORMATO, PERFIL


def _ingest(client) -> str:
    r = client.post("/ingest", files={"file": ("arq.md", DOC_CLOUD.encode(), "text/markdown")})
    assert r.status_code == 201
    return r.json()["document_id"]


# REGRESIÓN PERMANENTE — AUD-002 (capa HTTP) corregido el 2026-10-15 (antes xfail(strict))
def test_aud_002_api_no_context_responde_200_con_status_no_context(client, monkeypatch):
    from src.core.config import get_settings

    monkeypatch.setenv("RETRIEVAL_MIN_SCORE", "0.999")
    get_settings.cache_clear()
    doc_id = _ingest(client)
    job = client.post("/adapt", json={"document_id": doc_id, "perfil": PERFIL, "formato": FORMATO})
    respuesta = client.get(f"/adapt/{job.json()['job_id']}")
    assert respuesta.status_code == 200
    assert respuesta.json()["status"] == "NO_CONTEXT"


def test_ok_api_rechaza_docx_con_400(client):
    r = client.post("/ingest", files={"file": ("a.docx", b"x", "application/octet-stream")})
    assert r.status_code == 400
    assert r.json()["error"]["code"] == "INVALID_FILE"
