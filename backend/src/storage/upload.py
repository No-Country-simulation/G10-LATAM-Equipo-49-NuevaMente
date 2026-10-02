"""Subida de original y de resultado (OCI-003, OCI-005)."""
from src.storage.base import StorageClient, StorageResult
from src.storage.oci_client import build_object_name


def upload_original(
    document_id: str, filename: str, content: bytes, client: StorageClient
) -> StorageResult:
    """Sube el archivo original ingresado por el usuario (RF-017)."""
    object_name = build_object_name("originales", document_id, filename)
    return client.upload_bytes(object_name, content, _content_type(filename))


def upload_result_json(
    document_id: str, job_id: str, payload: bytes, client: StorageClient
) -> StorageResult:
    """Sube el JSON de resultado final (RF-017, RF-020)."""
    object_name = build_object_name("resultados", document_id, f"{job_id}.json")
    return client.upload_bytes(object_name, payload, "application/json")


def _content_type(filename: str) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return "application/pdf"
    if name.endswith(".md") or name.endswith(".markdown"):
        return "text/markdown"
    if name.endswith(".json"):
        return "application/json"
    return "text/plain"