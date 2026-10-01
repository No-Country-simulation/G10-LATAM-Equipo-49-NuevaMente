"""Cliente OCI real (OCI-002, DT-07).

Naming convention (DT-07): `{tipo}/{doc_id}/{timestamp}_{nombre}`.

# TODO: implementación futura — NO instanciar
# `oci.object_storage.ObjectStorageClient(...)` ni realizar ninguna
# llamada real al SDK de OCI en esta fase (CONTRACT-ONLY).
"""
from src.storage.base import StorageClient, StorageResult


class OCIStorageClient:
    """Implementación futura de `StorageClient` sobre OCI Object Storage."""

    def upload_bytes(self, object_name: str, data: bytes, content_type: str) -> StorageResult:
        ...

    def object_exists(self, object_name: str) -> bool:
        ...
# Nota: cumple el Protocol correspondiente por forma estructural (duck typing) — no se usa issubclass() en tiempo de importación porque el Protocol no está marcado @runtime_checkable.


def build_object_name(tipo: str, doc_id: str, nombre: str) -> str:
    """Construye el nombre de objeto según la convención DT-07:
    `{tipo}/{doc_id}/{timestamp}_{nombre}`.

    Implementación futura.
    """
    ...
