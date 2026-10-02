"""Cliente HTTP hacia la API del monolito (COMP-10 → COMP-11).

La interfaz no importa nada del backend: solo habla HTTP. La URL se configura
con la variable de entorno `API_URL` (por defecto http://127.0.0.1:8011).
"""
import os

import httpx

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")

_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".txt": "text/plain",
}
PENDING_STATUSES = ("QUEUED", "PROCESSING")


class ApiError(Exception):
    """Error devuelto por la API (o imposibilidad de contactarla)."""

    def __init__(self, code: str, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.status_code = status_code


def _request(method: str, path: str, timeout: float = 15.0, **kwargs) -> httpx.Response:
    try:
        return httpx.request(method, f"{API_URL}{path}", timeout=timeout, **kwargs)
    except httpx.TimeoutException as exc:
        raise ApiError("API_TIMEOUT", "La API tardó demasiado en responder.") from exc
    except httpx.HTTPError as exc:
        raise ApiError(
            "API_UNREACHABLE",
            f"No fue posible conectar con la API en {API_URL}. ¿Está encendida?",
        ) from exc


def _raise_for_error(response: httpx.Response) -> None:
    if response.status_code < 400:
        return
    try:
        error = response.json()["error"]
        raise ApiError(error["code"], error["message"], response.status_code)
    except (ValueError, KeyError, TypeError) as exc:
        raise ApiError(
            "INTERNAL_ERROR", f"Respuesta inesperada de la API (HTTP {response.status_code})."
        ) from exc


def health() -> bool:
    """Devuelve True si la API responde `{"status": "ok"}`."""
    try:
        response = _request("GET", "/health", timeout=3.0)
        return response.status_code == 200 and response.json().get("status") == "ok"
    except (ApiError, ValueError):
        return False


def ingest(file_bytes: bytes, filename: str) -> dict:
    """Llama a `POST /ingest`. Devuelve el JSON de la respuesta 201."""
    extension = os.path.splitext(filename)[1].lower()
    content_type = _CONTENT_TYPES.get(extension, "application/octet-stream")
    response = _request(
        "POST", "/ingest", timeout=60.0, files={"file": (filename, file_bytes, content_type)}
    )
    _raise_for_error(response)
    return response.json()


def request_adapt(
    document_id: str, perfil: str, formato: str, nicho: str | None, nivel_detalle: str
) -> dict:
    """Llama a `POST /adapt`. Devuelve `{"job_id", "status"}`."""
    payload = {
        "document_id": document_id,
        "perfil": perfil,
        "formato": formato,
        "nicho": nicho or None,
        "nivel_detalle": nivel_detalle,
    }
    response = _request("POST", "/adapt", json=payload)
    _raise_for_error(response)
    return response.json()


def poll_adapt_result(job_id: str) -> dict:
    """Llama a `GET /adapt/{job_id}`.

    Devuelve el resultado completo (status SUCCESS/PARTIAL/NO_CONTEXT/ERROR) o,
    si aún se procesa, `{"job_id", "status": "QUEUED" | "PROCESSING"}`.
    """
    response = _request("GET", f"/adapt/{job_id}")
    _raise_for_error(response)
    return response.json()

