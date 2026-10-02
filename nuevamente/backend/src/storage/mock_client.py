"""Cliente mock de almacenamiento: guarda los objetos en disco local.

Permite desarrollar y ejecutar tests sin cuenta OCI (STORAGE_PROVIDER=mock).
Los objetos quedan bajo `MOCK_STORAGE_DIR` (por defecto `data/mock_oci/`).
"""
from datetime import UTC, datetime
from pathlib import Path

from src.core.exceptions import StorageError
from src.storage.base import StorageResult


class MockStorageClient:
    """Implementación de `StorageClient` sin red (cumple el Protocol por forma)."""

    def __init__(self, base_dir: Path, bucket: str = "mock-bucket") -> None:
        self._base_dir = Path(base_dir).resolve()
        self._bucket = bucket

    def _resolve(self, object_name: str) -> Path:
        path = (self._base_dir / object_name).resolve()
        if self._base_dir != path and self._base_dir not in path.parents:
            raise StorageError("Nombre de objeto inválido.")
        return path

    def upload_bytes(self, object_name: str, data: bytes, content_type: str) -> StorageResult:
        path = self._resolve(object_name)
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
        except OSError as exc:
            raise StorageError(f"No fue posible guardar el objeto: {exc}") from exc
        return StorageResult(
            bucket=self._bucket,
            object_name=object_name,
            url=path.as_uri(),
            uploaded_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )

    def object_exists(self, object_name: str) -> bool:
        return self._resolve(object_name).is_file()
