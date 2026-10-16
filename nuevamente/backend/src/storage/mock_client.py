"""Cliente mock de almacenamiento: guarda los objetos en disco local.

Permite desarrollar y ejecutar tests sin cuenta OCI (STORAGE_PROVIDER=mock).
Los objetos quedan bajo `MOCK_STORAGE_DIR` (por defecto `data/mock_oci/`).
"""
from datetime import UTC, datetime
from pathlib import Path

from src.core.exceptions import StorageError
from src.storage.base import StorageListing, StorageObject, StorageResult


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

    def delete_object(self, object_name: str) -> None:
        """Elimina el archivo local; idempotente (AUD-004, 2026-10-15)."""
        path = self._resolve(object_name)
        try:
            path.unlink(missing_ok=True)
        except OSError as exc:
            raise StorageError(f"No fue posible borrar el objeto: {exc}") from exc

    def list_objects(
        self,
        prefix: str | None = None,
        limit: int = 100,
        start: str | None = None,
    ) -> StorageListing:
        """Lista objetos en disco local con soporte de prefijo y paginación simple."""
        if not self._base_dir.exists():
            return StorageListing(
                bucket=self._bucket,
                namespace="mock-namespace",
                prefix=prefix,
                count=0,
                next_start=None,
                objects=[],
            )

        all_files = []
        for p in self._base_dir.rglob("*"):
            if p.is_file():
                rel = p.relative_to(self._base_dir)
                # ****************************************************************
                #  MEJORA — 2026-10-15 (portabilidad Windows/Linux)
                #  Se usa `as_posix()` para que los nombres de objeto usen siempre
                #  "/" como separador (como OCI). Antes, en Windows, `str(rel)`
                #  producía "\" y el filtrado por prefijo "originals/" no
                #  encontraba nada.
                # ****************************************************************
                obj_name = rel.as_posix()
                if prefix is None or obj_name.startswith(prefix):
                    all_files.append(obj_name)

        all_files.sort()

        if start:
            try:
                start_idx = all_files.index(start)
            except ValueError:
                start_idx = len(all_files)
        else:
            start_idx = 0

        page = all_files[start_idx : start_idx + limit]
        next_start = None
        if start_idx + limit < len(all_files):
            next_start = all_files[start_idx + limit]

        objects = []
        for obj_name in page:
            p = self._base_dir / obj_name
            stat = p.stat()
            objects.append(
                StorageObject(
                    name=obj_name,
                    size=stat.st_size,
                    etag=None,
                    time_modified=datetime.fromtimestamp(stat.st_mtime, UTC).isoformat(),
                )
            )

        return StorageListing(
            bucket=self._bucket,
            namespace="mock-namespace",
            prefix=prefix,
            count=len(page),
            next_start=next_start,
            objects=objects,
        )