"""Cliente mock de almacenamiento, para desarrollo y tests sin cuenta OCI
real (sección "Mocks" del encargo).

Escribe bajo `data/mock_oci/` para que las pruebas no golpeen la red y el
estado sea inspeccionable en disco.
"""
from datetime import UTC, datetime
from pathlib import Path

from src.core.config import get_settings
from src.storage.base import StorageListing, StorageObject, StorageResult


class MockStorageClient:
    """Implementación de `StorageClient` que no realiza ninguna llamada de
    red: escribe los "objetos" como archivos bajo `data/mock_oci/`."""

    def __init__(self, root: str | Path | None = None):
        if root is None:
            default = Path(get_settings().CHROMA_PERSIST_DIR).parent / "mock_oci"
            self.root = Path(default)
        else:
            self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)

    def _path(self, object_name: str) -> Path:
        safe = str(object_name).replace("..", "_")
        p = self.root / safe
        p.parent.mkdir(parents=True, exist_ok=True)
        return p

    def upload_bytes(self, object_name: str, data: bytes, content_type: str) -> StorageResult:
        self._path(object_name).write_bytes(data)
        return StorageResult(
            bucket="mock",
            object_name=object_name,
            uploaded_at=datetime.now(UTC).isoformat(),
        )

    def object_exists(self, object_name: str) -> bool:
        return self._path(object_name).is_file()

    def get_namespace(self) -> str:
        return "mock-namespace"

    def list_objects(
        self,
        prefix: str | None = None,
        limit: int = 100,
        start: str | None = None,
    ) -> StorageListing:
        objs = []
        for p in sorted(self.root.rglob("*")):
            if not p.is_file():
                continue
            name = str(p.relative_to(self.root))
            if prefix and not name.startswith(prefix):
                continue
            objs.append(StorageObject(name=name, size=p.stat().st_size))
        if start:
            objs = [o for o in objs if o.name >= start]
        page = objs[:limit]
        return StorageListing(
            bucket="mock",
            namespace="mock-namespace",
            prefix=prefix,
            count=len(page),
            next_start=objs[limit].name if len(objs) > limit else None,
            objects=page,
        )