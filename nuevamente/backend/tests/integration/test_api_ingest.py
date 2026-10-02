"""RF-001 — POST /ingest vía TestClient (contrato de la Fase 6)."""
import re

from tests.helpers import encrypt_pdf, make_pdf

TEXT = "Los contenedores empaquetan aplicaciones con sus dependencias. " * 20


def _upload(client, name: str, data: bytes, content_type: str = "application/octet-stream"):
    return client.post("/ingest", files={"file": (name, data, content_type)})


def _error(response) -> dict:
    body = response.json()
    assert set(body) == {"error"}
    assert set(body["error"]) == {"code", "message"}
    return body["error"]


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ingest_txt_returns_201_and_stores_original(client, storage_dir):
    response = _upload(client, "notas.txt", TEXT.encode(), "text/plain")

    assert response.status_code == 201
    body = response.json()
    assert re.fullmatch(r"doc_[0-9a-f]{12}", body["document_id"])
    assert body["file_type"] == "txt"
    assert body["status"] == "INGESTED"
    assert body["filename"] == "notas.txt"
    assert body["chunk_count"] >= 1
    assert body["warnings"] == []

    stored = list((storage_dir / "originals" / body["document_id"]).glob("*_notas.txt"))
    assert len(stored) == 1
    assert stored[0].read_bytes() == TEXT.encode()
    assert body["storage_object_name"].startswith(f"originals/{body['document_id']}/")


def test_ingest_markdown(client):
    response = _upload(client, "guia.md", f"# Guía\n\n{TEXT}".encode(), "text/markdown")
    assert response.status_code == 201
    assert response.json()["file_type"] == "md"


def test_ingest_pdf_reports_pages(client):
    pdf = make_pdf([TEXT, "Segunda página con otro contenido"])
    response = _upload(client, "informe.pdf", pdf, "application/pdf")
    assert response.status_code == 201
    body = response.json()
    assert body["file_type"] == "pdf"
    assert body["page_count"] == 2
    assert body["warnings"] == []


def test_ingest_pdf_with_blank_page_returns_warning(client):
    response = _upload(client, "mixto.pdf", make_pdf([TEXT, ""]), "application/pdf")
    assert response.status_code == 201
    assert "1 de 2" in response.json()["warnings"][0]


def test_ingest_text_in_windows_1252(client):
    response = _upload(client, "ansi.txt", "Canción, acción y pasión. ".encode("cp1252") * 10)
    assert response.status_code == 201


def test_unsupported_extension_is_400_invalid_file(client):
    response = _upload(client, "datos.docx", b"contenido")
    assert response.status_code == 400
    assert _error(response)["code"] == "INVALID_FILE"


def test_empty_file_is_400(client):
    response = _upload(client, "vacio.txt", b"")
    assert response.status_code == 400
    assert _error(response)["code"] == "INVALID_FILE"


def test_file_over_limit_is_400_with_explicit_message(client, monkeypatch):
    from src.core.config import get_settings

    monkeypatch.setenv("MAX_FILE_SIZE_MB", "1")
    get_settings.cache_clear()

    response = _upload(client, "grande.txt", b"a" * (2 * 1024 * 1024))
    assert response.status_code == 400
    error = _error(response)
    assert error["code"] == "INVALID_FILE"
    assert "tamaño máximo" in error["message"]
    assert "1 MB" in error["message"]


def test_scanned_pdf_is_400_scanned_pdf(client):
    response = _upload(client, "escaneado.pdf", make_pdf(["", ""]), "application/pdf")
    assert response.status_code == 400
    assert _error(response)["code"] == "SCANNED_PDF"


def test_corrupt_and_fake_pdfs_are_400(client):
    corrupt = _upload(client, "roto.pdf", b"%PDF-1.4\nesto esta roto", "application/pdf")
    fake = _upload(client, "falso.pdf", b"esto no es un pdf", "application/pdf")
    for response in (corrupt, fake):
        assert response.status_code == 400
        assert _error(response)["code"] == "INVALID_FILE"


def test_password_protected_pdf_is_400_with_clear_message(client):
    pdf = encrypt_pdf(make_pdf([TEXT]))
    response = _upload(client, "protegido.pdf", pdf, "application/pdf")
    assert response.status_code == 400
    error = _error(response)
    assert error["code"] == "INVALID_FILE"
    assert "contraseña" in error["message"]


def test_missing_file_field_is_422_invalid_request(client):
    response = client.post("/ingest")
    assert response.status_code == 422
    assert _error(response)["code"] == "INVALID_REQUEST"


def test_failed_ingest_leaves_nothing_stored(client, storage_dir):
    _upload(client, "datos.docx", b"contenido")
    _upload(client, "escaneado.pdf", make_pdf([""]), "application/pdf")
    assert not storage_dir.exists() or not list(storage_dir.rglob("*.*"))
