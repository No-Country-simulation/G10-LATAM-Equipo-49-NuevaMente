"""Taxonomía de errores de dominio (contrato de errores del sistema).

Cada excepción mapea a un `code` que viaja en las respuestas de error de
la API (ver Fase 6 del Plan Técnico y `api/schemas.py::ErrorPayload`).
Estas clases son parte del contrato (no contienen lógica): el manejo real
(dónde se lanzan, cómo se capturan) es implementación futura de cada
componente.
"""


class NuevaMenteError(Exception):
    """Excepción base de dominio. Toda excepción propia del sistema hereda de esta."""

    code: str = "INTERNAL_ERROR"


class InvalidFileError(NuevaMenteError):
    """Archivo inválido, corrupto, de tipo no soportado o de tamaño excedido.

    Usada por: ingestion (RF-001, ING-005, ING-006, ING-008, ING-009).
    """

    code = "INVALID_FILE"


class ScannedPdfError(NuevaMenteError):
    """PDF sin texto extraíble (posible documento escaneado, ING-007)."""

    code = "SCANNED_PDF"


class DocumentNotFoundError(NuevaMenteError):
    """`document_id` inexistente al solicitar `/adapt` (Fase 6)."""

    code = "DOCUMENT_NOT_FOUND"


class NoContextError(NuevaMenteError):
    """El retrieval no encontró contexto suficiente (BE-RAG-011).

    Regla de negocio: si se produce este error, el sistema NO debe invocar
    al LLM de generación libremente; debe responder `status=NO_CONTEXT`.
    """

    code = "NO_CONTEXT"


class LLMProviderError(NuevaMenteError):
    """Fallo del proveedor de LLM (timeout, error de API, cuota) — Fase 14."""

    code = "LLM_ERROR"


class StorageError(NuevaMenteError):
    """Fallo de red o de credenciales hacia OCI Object Storage (COMP-09)."""

    code = "STORAGE_ERROR"
