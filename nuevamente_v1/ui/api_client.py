"""Cliente HTTP hacia la API del monolito (COMP-10 → COMP-11)."""
from src.output.schema import NuevaMenteOutput  # noqa: F401 — referencia de contrato


def ingest(file_bytes: bytes, filename: str) -> dict:
    """Llama a `POST /ingest`. Implementación futura."""
    ...


def request_adapt(document_id: str, perfil: str, formato: str, nicho: str | None, nivel_detalle: str) -> dict:
    """Llama a `POST /adapt`. Implementación futura."""
    ...


def poll_adapt_result(job_id: str) -> dict:
    """Llama a `GET /adapt/{job_id}`. Implementación futura."""
    ...
