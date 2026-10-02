"""Cliente HTTP de la UI: mapeo de errores de la API (sin servidor real)."""
import sys
from pathlib import Path

import httpx
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "ui"))

import api_client  # noqa: E402


def _fake(monkeypatch, response=None, error=None):
    def fake_request(method, url, **kwargs):
        if error is not None:
            raise error
        return response

    monkeypatch.setattr(api_client.httpx, "request", fake_request)


def test_ingest_returns_json_on_success(monkeypatch):
    _fake(monkeypatch, httpx.Response(201, json={"document_id": "doc_a", "file_type": "txt"}))
    assert api_client.ingest(b"hola", "a.txt")["document_id"] == "doc_a"


def test_api_error_payload_is_mapped(monkeypatch):
    payload = {"error": {"code": "INVALID_FILE", "message": "Archivo vacío"}}
    _fake(monkeypatch, httpx.Response(400, json=payload))
    with pytest.raises(api_client.ApiError) as info:
        api_client.ingest(b"", "a.txt")
    assert info.value.code == "INVALID_FILE"
    assert info.value.message == "Archivo vacío"
    assert info.value.status_code == 400


def test_non_json_error_becomes_internal_error(monkeypatch):
    _fake(monkeypatch, httpx.Response(502, text="Bad Gateway"))
    with pytest.raises(api_client.ApiError) as info:
        api_client.poll_adapt_result("job_x")
    assert info.value.code == "INTERNAL_ERROR"


def test_unreachable_api(monkeypatch):
    _fake(monkeypatch, error=httpx.ConnectError("boom"))
    with pytest.raises(api_client.ApiError) as info:
        api_client.request_adapt("doc_a", "principiante", "tutorial", None, "estandar")
    assert info.value.code == "API_UNREACHABLE"
    assert api_client.health() is False


def test_health_true_when_ok(monkeypatch):
    _fake(monkeypatch, httpx.Response(200, json={"status": "ok"}))
    assert api_client.health() is True


def test_pending_poll_returns_status(monkeypatch):
    _fake(monkeypatch, httpx.Response(202, json={"job_id": "job_x", "status": "PROCESSING"}))
    assert api_client.poll_adapt_result("job_x")["status"] in api_client.PENDING_STATUSES
