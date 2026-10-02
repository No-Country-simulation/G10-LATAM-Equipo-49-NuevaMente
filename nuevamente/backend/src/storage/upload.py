"""Subida de original y de resultado (OCI-003, OCI-005)."""
from src.core.exceptions import StorageError
from src.storage.base import StorageClient, StorageResult
from src.storage.naming import build_object_name
from src.storage.verify import verify_upload

_CONTENT_TYPES = {
    ".pdf": "application/pdf",
    ".md": "text/markdown",
    ".markdown": "text/markdown",
    ".txt": "text/plain",
}


def _content_type(filename: str) -> str:
    dot = filename.rfind(".")
    extension = filename[dot:].lower() if dot != -1 else ""
    return _CONTENT_TYPES.get(extension, "application/octet-stream")


def _upload_and_verify(
    object_name: str, data: bytes, content_type: str, client: StorageClient
) -> StorageResult:
    result = client.upload_bytes(object_name, data, content_type)
    if not verify_upload(result.object_name, client):
        raise StorageError("El objeto subido no pudo verificarse en el almacenamiento.")
    return result


def upload_original(
    document_id: str, filename: str, content: bytes, client: StorageClient
) -> StorageResult:
    """Sube el archivo original ingresado por el usuario (RF-017).

    Lanza:
        StorageError: si la subida o su verificación fallan.
    """
    object_name = build_object_name("originals", document_id, filename)
    return _upload_and_verify(object_name, content, _content_type(filename), client)


def upload_result_json(
    document_id: str, job_id: str, payload: bytes, client: StorageClient
) -> StorageResult:
    """Sube el JSON de resultado final (RF-017, RF-020).

    Lanza:
        StorageError: si la subida o su verificación fallan.
    """
    object_name = build_object_name("generated", document_id, f"{job_id}.json")
    return _upload_and_verify(object_name, payload, "application/json", client)

