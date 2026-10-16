"""Arranque común de los scripts de reproducción (se ejecutan desde la raíz del proyecto `nuevamente/`).

Uso:  python repro/repro_01_pipeline.py     (con las dependencias de requirements-dev.txt instaladas)
Cada script usa una base SQLite y un storage TEMPORALES: no toca datos reales ni requiere credenciales.
"""
import os
import pathlib
import sys
import tempfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
if os.environ.get("AUD_SHIMS"):  # solo para entornos sin dependencias (réplicas de la auditoría)
    sys.path.insert(0, os.environ["AUD_SHIMS"])
sys.path.insert(0, str(ROOT / "backend"))
TMP = pathlib.Path(tempfile.mkdtemp(prefix="aud_"))
DOC_CLOUD = (ROOT / "backend/tests/audit/fixtures/arquitectura_cloud.md").read_text(encoding="utf-8")


def fresh_env(**extra):
    d = pathlib.Path(tempfile.mkdtemp(prefix="aud_", dir=TMP))
    os.environ.update(
        DATABASE_URL=f"sqlite:///{d / 't.db'}", MOCK_STORAGE_DIR=str(d / "st"),
        STORAGE_PROVIDER="mock", VECTORSTORE_PROVIDER="memory", EMBEDDING_PROVIDER="mock",
        LLM_PROVIDER="mock", CHROMA_PERSIST_DIR=str(d / "chroma"),
    )
    for k, v in extra.items():
        os.environ[k] = str(v)
    if "RETRIEVAL_MIN_SCORE" not in extra:
        os.environ.pop("RETRIEVAL_MIN_SCORE", None)
    from src.core.config import get_settings
    from src.embeddings.factory import get_embedding_provider
    from src.vectorstore.factory import get_vectorstore
    get_settings.cache_clear(); get_embedding_provider.cache_clear(); get_vectorstore.cache_clear()
    return d
