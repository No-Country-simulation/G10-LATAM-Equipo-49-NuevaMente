"""Fixtures compartidas: cada test usa su propia base SQLite y su propio almacenamiento mock."""
from pathlib import Path

import pytest

from src.core.config import get_settings


@pytest.fixture(autouse=True)
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("STORAGE_PROVIDER", "mock")
    monkeypatch.setenv("MOCK_STORAGE_DIR", str(tmp_path / "storage"))
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "10")
    monkeypatch.setenv("CHUNK_SIZE", "800")
    monkeypatch.setenv("CHUNK_OVERLAP", "150")
    monkeypatch.setenv("MAX_DOCUMENT_CHARS", "2000000")
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


@pytest.fixture
def storage_dir(tmp_path: Path) -> Path:
    return tmp_path / "storage"


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from src.api.main import app

    return TestClient(app)
