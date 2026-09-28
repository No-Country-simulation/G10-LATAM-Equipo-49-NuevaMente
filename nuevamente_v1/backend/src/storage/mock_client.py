"""Cliente mock de almacenamiento, para desarrollo y tests sin cuenta OCI
real (sección "Mocks" del encargo).

# TODO: implementación futura — sin lógica real todavía.
"""
from src.storage.base import StorageClient, StorageResult


class MockStorageClient:
    """Implementación futura de `StorageClient` que no realiza ninguna
    llamada de red (p. ej. podría escribir bajo `data/mock_oci/` una vez
    implementado).
    """

    def upload_bytes(self, object_name: str, data: bytes, content_type: str) -> StorageResult:
        ...

    def object_exists(self, object_name: str) -> bool:
        ...
# Nota: cumple el Protocol correspondiente por forma estructural (duck typing) — no se usa issubclass() en tiempo de importación porque el Protocol no está marcado @runtime_checkable.
