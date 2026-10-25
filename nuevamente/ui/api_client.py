"""Cliente HTTP hacia la API del monolito (COMP-10 → COMP-11).

La interfaz no importa nada del backend: solo habla HTTP. La URL se configura
con la variable de entorno `API_URL` (por defecto http://127.0.0.1:8000).

MEJORA AUD-021 — 2026-10-15: el docstring decía "8011" mientras el código y la
API usan 8000; se corrige el texto para que coincida.
"""
import os

import httpx
import requests

API_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip("/")
N8N_WEBHOOK_URL = os.getenv("N8N_WEBHOOK_URL", "").rstrip("/")

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
    document_id: str, perfil: str, formato: str, nicho: str | None
) -> dict:
    """Llama a `POST /adapt`. Devuelve `{"job_id", "status"}`."""
    payload = {
        "document_id": document_id,
        "perfil": perfil,
        "formato": formato,
        "nicho": nicho or "General",
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


def notify_n8n(job_id: str, status: str, result: dict | None = None) -> None:
    """Envía notificación al webhook de n8n (opcional, fire-and-forget).

    No bloquea el flujo principal si n8n está caído o el webhook falla.
    """
    if not N8N_WEBHOOK_URL:
        return
    payload = {"job_id": job_id, "status": status}
    if result is not None:
        payload["result"] = result
    try:
        response = httpx.post(N8N_WEBHOOK_URL, json=payload, timeout=10.0)
        response.raise_for_status()
    except httpx.HTTPError:
        # n8n es opcional: no bloquear el flujo principal
        pass


def submit_to_workflow(uploaded_file, perfil: str, formato: str, nicho: str) -> dict:
    """Envía el archivo y las opciones pedagógicas directamente al webhook de n8n.

    n8n recibe el archivo binario y los parámetros como campos de formulario
    multipart, maneja el flujo completo de ingesta + adaptación y devuelve
    el resultado final.

    Args:
        uploaded_file: objeto UploadedFile de Streamlit (tiene .name, .getvalue(), .type).
        perfil: perfil destinatario seleccionado por el usuario.
        formato: formato de salida seleccionado por el usuario.
        nicho: nicho/sector seleccionado por el usuario.

    Devuelve:
        dict con el resultado devuelto por el webhook de n8n.

    Lanza:
        ApiError: si el webhook no responde, devuelve error HTTP, o N8N_WEBHOOK_URL
            no está configurada.
    """
    if not N8N_WEBHOOK_URL:
        raise ApiError("N8N_NOT_CONFIGURED", "N8N_WEBHOOK_URL no está configurada.")

    # 1. Archivo binario con la clave exacta "file"
    files = {
        "file": (uploaded_file.name, uploaded_file.getvalue(), uploaded_file.type)
    }

    # 2. Opciones pedagógicas como campos de texto del formulario
    data = {
        "perfil": perfil,
        "formato": formato,
        "nicho": nicho,
    }

    # 3. POST multipart: files y data por separado (NUNCA json=)
    try:
        response = requests.post(N8N_WEBHOOK_URL, files=files, data=data, timeout=300)
    except requests.Timeout as exc:
        raise ApiError("API_TIMEOUT", "El workflow de n8n tardó demasiado en responder.") from exc
    except requests.ConnectionError as exc:
        raise ApiError(
            "API_UNREACHABLE",
            f"No fue posible conectar con el webhook de n8n en {N8N_WEBHOOK_URL}.",
        ) from exc

    if response.status_code >= 400:
        try:
            error = response.json().get("error", {})
            raise ApiError(
                error.get("code", "N8N_ERROR"),
                error.get("message", f"Error del webhook de n8n (HTTP {response.status_code})."),
                response.status_code,
            )
        except (ValueError, AttributeError) as exc:
            raise ApiError(
                "N8N_ERROR",
                f"Respuesta inesperada del webhook de n8n (HTTP {response.status_code}).",
                response.status_code,
            ) from exc

    return response.json()

