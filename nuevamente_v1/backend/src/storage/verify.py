"""Verificación post-upload (OCI-005)."""
from src.storage.base import StorageClient


def verify_upload(object_name: str, client: StorageClient) -> bool:
    """Confirma que `object_name` es recuperable desde el bucket tras el
    upload. Si falla, el `status` del resultado final debe degradar a
    "PARTIAL" en vez de asumir éxito silenciosamente (COMP-09, Riesgos).

    Implementación futura.
    """
    ...
