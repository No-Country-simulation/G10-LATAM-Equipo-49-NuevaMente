"""Cliente OCI Object Storage (OCI-002, DT-07).

Convención de nombres: `{tipo}/{doc_id}/{timestamp}_{nombre}` (ver `naming.py`).
El SDK `oci` se importa de forma diferida: solo se necesita con
`STORAGE_PROVIDER=oci` (instalar `requirements-oci.txt`).

NOTA: esta implementación aún no se ha ejecutado contra un bucket real.
"""
from datetime import UTC, datetime

from src.core.config import get_settings
from src.core.exceptions import StorageError
from src.storage.base import StorageResult
from src.storage.naming import build_object_name
from src.storage.oci_config import load_oci_config

__all__ = ["OCIStorageClient", "build_object_name"]


class OCIStorageClient:
    """Implementación de `StorageClient` sobre OCI Object Storage."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._client = None
        self._namespace: str | None = self._settings.OCI_NAMESPACE or None

    def _object_storage(self):
        if self._client is None:
            import oci

            self._client = oci.object_storage.ObjectStorageClient(load_oci_config())
        return self._client

    def _get_namespace(self) -> str:
        if self._namespace is None:
            try:
                self._namespace = self._object_storage().get_namespace().data
            except StorageError:
                raise
            except Exception as exc:
                raise StorageError(f"No fue posible obtener el namespace de OCI: {exc}") from exc
        return self._namespace

    def upload_bytes(self, object_name: str, data: bytes, content_type: str) -> StorageResult:
        bucket = self._settings.OCI_BUCKET_NAME
        try:
            self._object_storage().put_object(
                self._get_namespace(),
                bucket,
                object_name,
                data,
                content_type=content_type,
            )
        except StorageError:
            raise
        except Exception as exc:
            raise StorageError(f"No fue posible subir el objeto a OCI: {exc}") from exc
        return StorageResult(
            bucket=bucket,
            object_name=object_name,
            uploaded_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )

    def object_exists(self, object_name: str) -> bool:
        try:
            self._object_storage().head_object(
                self._get_namespace(), self._settings.OCI_BUCKET_NAME, object_name
            )
        except StorageError:
            raise
        except Exception as exc:
            if getattr(exc, "status", None) == 404:
                return False
            raise StorageError(f"No fue posible verificar el objeto en OCI: {exc}") from exc
        return True