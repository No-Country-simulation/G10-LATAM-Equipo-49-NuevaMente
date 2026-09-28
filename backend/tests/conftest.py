"""Configuración de tests: entorno hermético y sin red.

Fuerza `LLM_PROVIDER=mock`/`EMBEDDING_PROVIDER=mock`, desactiva OCI (para que
`PipelineOrchestrator._storage_client` elija `MockStorageClient`) y desvía la
base SQLite a `/tmp` para no ensuciar `backend/data/`.
"""
import os

os.environ.setdefault("LLM_PROVIDER", "mock")
os.environ.setdefault("EMBEDDING_PROVIDER", "mock")
os.environ["OCI_NAMESPACE"] = ""
os.environ["OCI_BUCKET_NAME"] = ""
os.environ["DATABASE_URL"] = "sqlite:////tmp/opencode/nuevamente_test.db"
os.environ["RETRIEVAL_MIN_SCORE"] = "0.1"

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402
from src.core.config import get_settings  # noqa: E402


@pytest.fixture(autouse=True)
def _settings_limpios() -> None:
    """Resetea el cache de `get_settings` y la tabla de jobs por test."""
    get_settings.cache_clear()
    from src.db import session as db

    with db._conn() as conn:  # noqa: SLF001 — test accede a helper interno
        conn.execute("DELETE FROM jobs")


@pytest.fixture(scope="session")
def client() -> TestClient:
    """`TestClient` sobre la app con el orquestador en modo mock."""
    from src.api.main import _orchestrator, app
    from src.storage.mock_client import MockStorageClient

    _orchestrator._storage = MockStorageClient()
    return TestClient(app)