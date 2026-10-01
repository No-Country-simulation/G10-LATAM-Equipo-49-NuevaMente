"""Taxonomía de errores de dominio (contrato de errores del sistema).

Cada excepción mapea a un `code` y a un `http_status` que la API traduce a
`{"error": {"code": ..., "message": ...}}` (Plan Técnico, Fase 6).
"""


class NuevaMenteError(Exception):
    """Excepción base de dominio. Toda excepción propia hereda de esta."""

    code: str = "INTERNAL_ERROR"
    http_status: int = 500

    @property
    def message(self) -> str:
        return str(self) or "Error interno."


class InvalidFileError(NuevaMenteError):
    """Archivo inválido, corrupto, de tipo no soportado o de tamaño excedido.

    Usada por: ingestion (RF-001, ING-005, ING-006, ING-008, ING-009).
    """

    code = "INVALID_FILE"
    http_status = 400


class ScannedPdfError(NuevaMenteError):
    """PDF sin texto extraíble (posible documento escaneado, ING-007)."""

    code = "SCANNED_PDF"
    http_status = 400


class DocumentTooLargeError(NuevaMenteError):
    """El texto del documento supera `MAX_DOCUMENT_CHARS` (PROC-005)."""

    code = "DOCUMENT_TOO_LARGE"
    http_status = 400


class InvalidRequestError(NuevaMenteError):
    """Parámetros de solicitud inválidos (perfil, formato o nivel desconocidos)."""

    code = "INVALID_REQUEST"
    http_status = 400


class DocumentNotFoundError(NuevaMenteError):
    """`document_id` inexistente al solicitar `/adapt` (Fase 6)."""

    code = "DOCUMENT_NOT_FOUND"
    http_status = 404


class JobNotFoundError(NuevaMenteError):
    """`job_id` inexistente al consultar `GET /adapt/{job_id}`."""

    code = "JOB_NOT_FOUND"
    http_status = 404


class NoContextError(NuevaMenteError):
    """El retrieval no encontró contexto suficiente (BE-RAG-011).

    Regla de negocio: si se produce este error, el sistema NO debe invocar
    al LLM de generación libremente; debe responder `status=NO_CONTEXT`.
    """

    code = "NO_CONTEXT"
    http_status = 422


class LLMProviderError(NuevaMenteError):
    """Fallo del proveedor de LLM (timeout, error de API, cuota) — Fase 14."""

    code = "LLM_ERROR"
    http_status = 502


class StorageError(NuevaMenteError):
    """Fallo de red o de credenciales hacia el almacenamiento (COMP-09)."""

    code = "STORAGE_ERROR"
    http_status = 502
