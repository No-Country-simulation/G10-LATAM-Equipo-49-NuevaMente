"""Selección del cliente de almacenamiento según `STORAGE_PROVIDER` (RNF-005)."""
from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError
from src.storage.base import StorageClient
from src.storage.mock_client import MockStorageClient
from src.storage.oci_client import OCIStorageClient


def get_storage_client() -> StorageClient:
    """Devuelve el cliente configurado: `mock` (disco local) u `oci`."""
    settings = get_settings()
    provider = settings.STORAGE_PROVIDER.lower()
    if provider == "mock":
        return MockStorageClient(settings.resolve_path(settings.MOCK_STORAGE_DIR))
    if provider == "oci":
        return OCIStorageClient()
    raise NuevaMenteError(
        f"STORAGE_PROVIDER inválido: {settings.STORAGE_PROVIDER!r}. Valores válidos: 'mock' u 'oci'."
    )