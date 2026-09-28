"""Subida de original y de resultado (OCI-003, OCI-005)."""
from src.storage.base import StorageClient, StorageResult


def upload_original(document_id: str, filename: str, content: bytes, client: StorageClient) -> StorageResult:
    """Sube el archivo original ingresado por el usuario (RF-017).

    Implementación futura.
    """
    ...


def upload_result_json(document_id: str, job_id: str, payload: bytes, client: StorageClient) -> StorageResult:
    """Sube el JSON de resultado final (RF-017, RF-020).

    Implementación futura.
    """
    ...
