"""Acceso a la persistencia de Jobs y Documentos (DT-08).

SQLite local, `settings.DATABASE_URL`. Implementación real sobre el
contrato declarado en `db/models.py`. La conexión se crea bajo demanda y
se cierra por fila (suficiente para el volumen de un hackathon y evita
problemas de hilos con FastAPI).
"""
import os
import sqlite3
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path

from src.core.config import get_settings
from src.db.models import Job, JobStatus

_TABLA_JOBS = """
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    status TEXT NOT NULL,
    result_object_name TEXT,
    result_json TEXT,
    error TEXT
)
"""
_TABLA_DOCS = """
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    raw_text TEXT NOT NULL
)
"""


def _ruta_db() -> str:
    url = get_settings().DATABASE_URL
    if not url.startswith("sqlite:///"):
        raise ValueError(f"DATABASE_URL debe ser sqlite:///... (obtenido: {url!r})")
    path = url.replace("sqlite:///", "", 1)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    return path


@contextmanager
def _conn() -> Iterator[sqlite3.Connection]:
    conn = sqlite3.connect(_ruta_db())
    conn.execute(_TABLA_JOBS)
    conn.execute(_TABLA_DOCS)
    conn.commit()
    try:
        yield conn
    finally:
        conn.close()


def _row_a_job(row: sqlite3.Row) -> Job:
    # pydantic valida el Literal JobStatus (no se instancia `Literal` a mano)
    return Job(
        job_id=row["job_id"],
        document_id=row["document_id"],
        status=row["status"],
        result_object_name=row["result_object_name"],
        result_json=row["result_json"],
        error=row["error"],
    )


# ── Jobs ────────────────────────────────────────────────────────────
def create_job(document_id: str) -> Job:
    """Crea un `Job` nuevo en estado `QUEUED` y lo persiste."""
    job = Job(job_id=os.urandom(8).hex(), document_id=document_id, status="QUEUED")
    with _conn() as conn:
        conn.execute(
            "INSERT INTO jobs (job_id, document_id, status) VALUES (?, ?, ?)",
            (job.job_id, job.document_id, job.status),
        )
        conn.commit()
    return job


def update_job_status(job_id: str, status: JobStatus, error: str | None = None) -> None:
    """Actualiza el estado de un `Job` existente."""
    with _conn() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, error = ? WHERE job_id = ?",
            (status, error, job_id),
        )
        conn.commit()


def set_job_result(job_id: str, result_object_name: str, result_json: str | None = None) -> None:
    """Asocia el objeto de resultado de OCI y el JSON final a un `Job`."""
    with _conn() as conn:
        conn.execute(
            "UPDATE jobs SET result_object_name = ?, result_json = ? WHERE job_id = ?",
            (result_object_name, result_json, job_id),
        )
        conn.commit()


def get_job(job_id: str) -> Job | None:
    """Recupera un `Job` por id, o `None` si no existe."""
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT job_id, document_id, status, result_object_name, result_json, error "
            "FROM jobs WHERE job_id = ?",
            (job_id,),
        )
        row = cur.fetchone()
    return _row_a_job(row) if row else None


# ── Documentos (texto crudo ingerido) ───────────────────────────────
def save_document(document_id: str, filename: str, file_type: str, raw_text: str) -> None:
    """Persiste el texto crudo y metadatos de un documento ingerido."""
    with _conn() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO documents "
            "(document_id, filename, file_type, raw_text) VALUES (?, ?, ?, ?)",
            (document_id, filename, file_type, raw_text),
        )
        conn.commit()


def get_document(document_id: str) -> dict | None:
    """Recupera un documento por id, o `None` si no existe."""
    with _conn() as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.execute(
            "SELECT document_id, filename, file_type, raw_text "
            "FROM documents WHERE document_id = ?",
            (document_id,),
        )
        row = cur.fetchone()
    return dict(row) if row else None