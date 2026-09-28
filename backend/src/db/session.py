"""Acceso a la persistencia de Jobs (DT-08).

Tecnología prevista: SQLite local, `settings.DATABASE_URL`. Implementación
futura — ningún acceso real a base de datos ocurre en este módulo.
"""
from src.db.models import Job, JobStatus


def create_job(document_id: str) -> Job:
    """Crea un `Job` nuevo en estado `QUEUED` y lo persiste.

    Implementación futura.
    """
    ...


def update_job_status(job_id: str, status: JobStatus, error: str | None = None) -> None:
    """Actualiza el estado de un `Job` existente.

    Implementación futura.
    """
    ...


def get_job(job_id: str) -> Job | None:
    """Recupera un `Job` por id, o `None` si no existe.

    Implementación futura.
    """
    ...
