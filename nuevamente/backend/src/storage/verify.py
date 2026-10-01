"""Verificación post-upload (OCI-005)."""
from src.storage.base import StorageClient


def verify_upload(object_name: str, client: StorageClient) -> bool:
    """Confirma que `object_name` es recuperable desde el bucket tras el upload.

    Devuelve `False` (nunca lanza) si no se puede confirmar, para que quien
    llama decida cómo degradar el resultado en vez de asumir éxito.
    """
    try:
        return client.object_exists(object_name)
    except Exception:
        return False
