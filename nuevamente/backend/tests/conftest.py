"""Fixtures compartidas: cada test usa su propia base SQLite y su propio almacenamiento mock."""
from pathlib import Path

import pytest

from src.core.config import get_settings
from src.embeddings.factory import get_embedding_provider
from src.generation.factory import get_llm_provider
from src.vectorstore.client import get_chroma_collection
from src.vectorstore.factory import get_vectorstore


@pytest.fixture(autouse=True)
def isolated_env(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{tmp_path / 'test.db'}")
    monkeypatch.setenv("STORAGE_PROVIDER", "mock")
    monkeypatch.setenv("VECTORSTORE_PROVIDER", "memory")
    monkeypatch.setenv("MOCK_STORAGE_DIR", str(tmp_path / "storage"))
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "10")
    monkeypatch.setenv("CHUNK_SIZE", "800")
    monkeypatch.setenv("CHUNK_OVERLAP", "150")
    monkeypatch.setenv("MAX_DOCUMENT_CHARS", "2000000")
    monkeypatch.setenv("LLM_PROVIDER", "mock")
    monkeypatch.setenv("EMBEDDING_PROVIDER", "mock")
    get_settings.cache_clear()
    get_embedding_provider.cache_clear()
    get_llm_provider.cache_clear()
    get_vectorstore.cache_clear()
    get_chroma_collection.cache_clear()
    yield
    get_settings.cache_clear()
    get_embedding_provider.cache_clear()
    get_llm_provider.cache_clear()
    get_vectorstore.cache_clear()
    get_chroma_collection.cache_clear()


@pytest.fixture
def storage_dir(tmp_path: Path) -> Path:
    return tmp_path / "storage"


@pytest.fixture
def client():
    from fastapi.testclient import TestClient

    from src.api.main import app

    return TestClient(app)
