import sqlite3
import json
import pathlib

from src.core.config import settings
from src.db.models import Job

DB_PATH = pathlib.Path(settings.DATABASE_URL.replace("sqlite:///", ""))
DB_PATH.parent.mkdir(parents=True, exist_ok=True)


def _connect():
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """CREATE TABLE IF NOT EXISTS jobs (
            job_id TEXT PRIMARY KEY,
            document_id TEXT NOT NULL,
            status TEXT NOT NULL,
            result_object TEXT,
            error TEXT
        )"""
    )
    return conn


def create_job(job_id: str, document_id: str) -> None:
    with _connect() as conn:
        conn.execute(
            "INSERT INTO jobs (job_id, document_id, status) VALUES (?, ?, 'QUEUED')",
            (job_id, document_id),
        )


def update_job(job_id: str, status: str, result_object: str | None = None, error: str | None = None) -> None:
    with _connect() as conn:
        conn.execute(
            "UPDATE jobs SET status = ?, result_object = ?, error = ? WHERE job_id = ?",
            (status, result_object, error, job_id),
        )


def get_job(job_id: str) -> Job | None:
    with _connect() as conn:
        row = conn.execute(
            "SELECT job_id, document_id, status, result_object, error FROM jobs WHERE job_id = ?",
            (job_id,),
        ).fetchone()
    if not row:
        return None
    return Job(job_id=row[0], document_id=row[1], status=row[2], result_object=row[3], error=row[4])
