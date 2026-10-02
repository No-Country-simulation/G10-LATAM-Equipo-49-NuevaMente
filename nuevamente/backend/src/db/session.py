"""Acceso a la persistencia de documentos, chunks y jobs (DT-08).

SQLite local (`settings.DATABASE_URL`) con la biblioteca estándar. Cada
operación abre su propia conexión, así que es segura entre hilos (la API
ejecuta los handlers síncronos y las tareas en segundo plano en un pool).
"""
import json
import sqlite3
import uuid
from collections.abc import Iterator
from contextlib import contextmanager

from src.core.config import get_settings
from src.db.models import DocumentRecord, Job, JobStatus
from src.processing.models import DocumentChunk

_SCHEMA = """
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    page_count INTEGER NOT NULL,
    char_count INTEGER NOT NULL,
    chunk_count INTEGER NOT NULL,
    storage_object_name TEXT,
    warnings TEXT NOT NULL,
    created_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS chunks (
    document_id TEXT NOT NULL,
    position INTEGER NOT NULL,
    id TEXT NOT NULL,
    text TEXT NOT NULL,
    section TEXT,
    page INTEGER,
    char_start INTEGER NOT NULL,
    char_end INTEGER NOT NULL,
    PRIMARY KEY (document_id, position)
);
CREATE TABLE IF NOT EXISTS jobs (
    job_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL,
    status TEXT NOT NULL,
    result_object_name TEXT,
    result_json TEXT,
    error TEXT
);
"""


@contextmanager
def _connect() -> Iterator[sqlite3.Connection]:
    path = get_settings().sqlite_path
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, timeout=10)
    conn.row_factory = sqlite3.Row
    try:
        conn.executescript(_SCHEMA)
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def save_document(record: DocumentRecord, chunks: list[DocumentChunk]) -> None:
    """Guarda el documento y sus chunks de forma atómica (una sola transacción)."""
    with _connect() as conn:
        conn.execute(
            "INSERT INTO documents VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                record.document_id,
                record.filename,
                record.file_type,
                record.size_bytes,
                record.page_count,
                record.char_count,
                record.chunk_count,
                record.storage_object_name,
                json.dumps(record.warnings, ensure_ascii=False),
                record.created_at,
            ),
        )
        conn.executemany(
            "INSERT INTO chunks VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            [
                (
                    record.document_id,
                    c.position,
                    c.id,
                    c.text,
                    c.section,
                    c.page,
                    c.char_start,
                    c.char_end,
                )
                for c in chunks
            ],
        )


def get_document(document_id: str) -> DocumentRecord | None:
    """Recupera los metadatos de un documento, o `None` si no existe."""
    with _connect() as conn:
        row = conn.execute(
            "SELECT * FROM documents WHERE document_id = ?", (document_id,)
        ).fetchone()
    if row is None:
        return None
    data = dict(row)
    data["warnings"] = json.loads(data["warnings"])
    return DocumentRecord(**data)


def get_chunks(document_id: str) -> list[DocumentChunk]:
    """Recupera los chunks de un documento, ordenados por posición."""
    with _connect() as conn:
        rows = conn.execute(
            "SELECT id, document_id, text, position, section, page, char_start, char_end "
            "FROM chunks WHERE document_id = ? ORDER BY position",
            (document_id,),
        ).fetchall()
    return [
        DocumentChunk(
            id=r["id"],
            doc_id=r["document_id"],
            text=r["text"],
            position=r["position"],
            section=r["section"],
            page=r["page"],
            char_start=r["char_start"],
            char_end=r["char_end"],
        )
        for r in rows
    ]


def _row_to_job(row: sqlite3.Row) -> Job:
    return Job(**dict(row))


def create_job(document_id: str) -> Job:
    """Crea un `Job` nuevo en estado `QUEUED` y lo persiste."""
    job = Job(job_id=f"job_{uuid.uuid4().hex[:12]}", document_id=document_id, status="QUEUED")
    with _connect() as conn:
        conn.execute(
            "INSERT INTO jobs (job_id, document_id, status) VALUES (?, ?, ?)",
            (job.job_id, job.document_id, job.status),
        )
    return job


def update_job_status(job_id: str, status: JobStatus, error: str | None = None) -> None:
    """Actualiza el estado de un `Job` existente."""
    with _connect() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, error = ? WHERE job_id = ?", (status, error, job_id)
        )


def save_job_result(
    job_id: str,
    status: JobStatus,
    result_json: str,
    result_object_name: str | None = None,
) -> None:
    """Guarda el resultado final (JSON validado) de un job y su estado."""
    with _connect() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, result_json = ?, result_object_name = ?, error = NULL "
            "WHERE job_id = ?",
            (status, result_json, result_object_name, job_id),
        )


def get_job(job_id: str) -> Job | None:
    """Recupera un `Job` por id, o `None` si no existe."""
    with _connect() as conn:
        row = conn.execute("SELECT * FROM jobs WHERE job_id = ?", (job_id,)).fetchone()
    return _row_to_job(row) if row is not None else None
