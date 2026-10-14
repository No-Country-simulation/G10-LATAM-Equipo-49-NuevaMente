"""COMP-09 — almacenamiento: nombres de objeto, cliente mock y subidas."""
from datetime import UTC, datetime

import pytest

from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError, StorageError
from src.storage.base import StorageResult
from src.storage.factory import get_storage_client
from src.storage.mock_client import MockStorageClient
from src.storage.naming import build_object_name, sanitize_filename
from src.storage.upload import upload_original, upload_result_json
from src.storage.verify import verify_upload


def test_build_object_name_follows_dt07():
    now = datetime(2026, 1, 2, 3, 4, 5, tzinfo=UTC)
    name = build_object_name("originals", "doc_1", "mi archivo.pdf", now=now)
    assert name == "originals/doc_1/20260102T030405Z_mi_archivo.pdf"


@pytest.mark.parametrize(
    "raw,expected",
    [
        ("../../etc/passwd", "passwd"),
        ("..\\..\\x.txt", "x.txt"),
        (".oculto", "oculto"),
        ("", "archivo"),
        ("informe final (v2).pdf", "informe_final_v2_.pdf"),
    ],
)
def test_sanitize_filename(raw, expected):
    assert sanitize_filename(raw) == expected


def test_mock_client_upload_and_exists(tmp_path):
    client = MockStorageClient(tmp_path / "bucket", bucket="mi-bucket")
    result = client.upload_bytes("originals/doc_1/a.txt", b"hola", "text/plain")

    assert result.bucket == "mi-bucket"
    assert result.object_name == "originals/doc_1/a.txt"
    assert result.uploaded_at
    assert (tmp_path / "bucket" / "originals" / "doc_1" / "a.txt").read_bytes() == b"hola"
    assert client.object_exists("originals/doc_1/a.txt") is True
    assert client.object_exists("originals/doc_1/otro.txt") is False


@pytest.mark.parametrize("name", ["../fuera.txt", "a/../../fuera.txt"])
def test_mock_client_blocks_path_traversal(tmp_path, name):
    client = MockStorageClient(tmp_path / "bucket")
    with pytest.raises(StorageError):
        client.upload_bytes(name, b"x", "text/plain")


def test_upload_original_uses_naming_and_content_type(tmp_path):
    client = MockStorageClient(tmp_path)
    result = upload_original("doc_1", "guia.md", b"# hola", client)
    assert result.object_name.startswith("originals/doc_1/")
    assert result.object_name.endswith("_guia.md")
    assert client.object_exists(result.object_name)


def test_upload_result_json(tmp_path):
    client = MockStorageClient(tmp_path)
    result = upload_result_json("doc_1", "job_9", b"{}", client)
    assert result.object_name.startswith("generated/doc_1/")
    assert result.object_name.endswith("_job_9.json")
    assert client.object_exists(result.object_name)


class _BrokenClient:
    def upload_bytes(self, object_name, data, content_type):
        raise StorageError("sin red")

    def object_exists(self, object_name):
        raise RuntimeError("sin red")


class _SilentClient:
    """Dice que subió, pero el objeto no existe (la verificación debe fallar)."""

    def upload_bytes(self, object_name, data, content_type):
        return StorageResult(bucket="x", object_name=object_name)

    def object_exists(self, object_name):
        return False


def test_verify_upload_never_raises():
    assert verify_upload("x", _BrokenClient()) is False


def test_upload_fails_when_object_cannot_be_verified():
    with pytest.raises(StorageError, match="verificarse"):
        upload_original("doc_1", "a.txt", b"x", _SilentClient())


def test_upload_propagates_storage_errors():
    with pytest.raises(StorageError):
        upload_original("doc_1", "a.txt", b"x", _BrokenClient())


def test_factory_returns_mock_by_default(storage_dir):
    client = get_storage_client()
    assert isinstance(client, MockStorageClient)
    client.upload_bytes("a/b.txt", b"x", "text/plain")
    assert (storage_dir / "a" / "b.txt").exists()


def test_factory_rejects_unknown_provider(monkeypatch):
    monkeypatch.setenv("STORAGE_PROVIDER", "ftp")
    get_settings.cache_clear()
    with pytest.raises(NuevaMenteError, match="STORAGE_PROVIDER"):
        get_storage_client()


def test_list_objects_prefix_and_pagination(tmp_path):
    client = MockStorageClient(tmp_path / "bucket", bucket="test-bucket")
    client.upload_bytes("originals/doc_1/a.txt", b"a", "text/plain")
    client.upload_bytes("originals/doc_1/b.txt", b"b", "text/plain")
    client.upload_bytes("generated/doc_1/job_1.json", b"{}", "application/json")
    client.upload_bytes("generated/doc_2/job_2.json", b"{}", "application/json")
    client.upload_bytes("other.txt", b"x", "text/plain")

    # Prefijo originals/
    listing = client.list_objects(prefix="originals/")
    assert listing.bucket == "test-bucket"
    assert listing.namespace == "mock-namespace"
    assert listing.prefix == "originals/"
    assert listing.count == 2
    names = [o.name for o in listing.objects]
    assert "originals/doc_1/a.txt" in names
    assert "originals/doc_1/b.txt" in names
    assert all(o.size == 1 for o in listing.objects)
    assert all(o.etag is None for o in listing.objects)
    assert all(o.time_modified is not None for o in listing.objects)

    # Prefijo generated/
    listing = client.list_objects(prefix="generated/")
    assert listing.count == 2
    names = [o.name for o in listing.objects]
    assert "generated/doc_1/job_1.json" in names
    assert "generated/doc_2/job_2.json" in names

    # Sin prefijo (todos)
    listing = client.list_objects(prefix=None)
    assert listing.count == 5

    # Paginación con limit
    listing = client.list_objects(prefix="originals/", limit=1)
    assert listing.count == 1
    assert listing.next_start is not None
    listing2 = client.list_objects(prefix="originals/", limit=1, start=listing.next_start)
    assert listing2.count == 1
    assert listing.objects[0].name != listing2.objects[0].name
    assert listing2.next_start is None


def test_list_objects_empty_prefix(tmp_path):
    client = MockStorageClient(tmp_path / "empty")
    listing = client.list_objects(prefix="originals/")
    assert listing.count == 0
    assert listing.objects == []
    assert listing.next_start is None


def test_mock_client_protocol_completeness(tmp_path):
    """Verifica que MockStorageClient satisface todo el Protocol StorageClient."""
    client: object = MockStorageClient(tmp_path)
    # Duck-typing check: todos los métodos del Protocol existen
    assert hasattr(client, "upload_bytes")
    assert hasattr(client, "object_exists")
    assert hasattr(client, "list_objects")
