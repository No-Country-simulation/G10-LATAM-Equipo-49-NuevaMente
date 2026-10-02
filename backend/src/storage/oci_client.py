"""Cliente OCI real (OCI-002, DT-07).

Implementación sobre OCI Object Storage que cumple `StorageClient`
(ver `storage/base.py`). Los objetos se construyen según la convención
DT-07: `{tipo}/{doc_id}/{timestamp}_{nombre}`.
"""
from datetime import UTC, datetime
from zoneinfo import ZoneInfo

import oci

from src.core.config import get_settings
from src.core.exceptions import StorageError
from src.storage.base import StorageListing, StorageObject, StorageResult


class OCIStorageClient:
    """Implementación de `StorageClient` sobre OCI Object Storage."""

    def __init__(self, client=None, bucket: str | None = None, namespace: str | None = None):
        settings = get_settings()
        self.__bucket = bucket or settings.OCI_BUCKET_NAME
        self.__namespace = namespace or settings.OCI_NAMESPACE
        self.__prefix = (settings.OCI_PREFIX or "").strip("/")
        self.__lock = None  # placeholder de extensión futura
        self.__client = client

    # ── helpers ──────────────────────────────────────────────────────
    def _get_client(self) -> "oci.object_storage.ObjectStorageClient":
        if self.__client is None:
            if not self.__bucket or not self.__namespace:
                raise StorageError("OCI_BUCKET_NAME y OCI_NAMESPACE son obligatorios")
            from src.storage.oci_config import load_oci_config

            self.__client = oci.object_storage.ObjectStorageClient(load_oci_config())
        return self.__client

    def _resolved_prefix(self, prefix: str | None) -> str | None:
        base = prefix if prefix is not None else self.__prefix
        return base.strip("/") if base else None

    # ── StorageClient Protocol ───────────────────────────────────────
    def get_namespace(self) -> str:
        if not self.__namespace:
            raise StorageError("OCI_NAMESPACE no configurado")
        return self.__namespace

    def upload_bytes(self, object_name: str, data: bytes, content_type: str) -> StorageResult:
        client = self._get_client()
        try:
            client.put_object(
                self.__namespace,
                self.__bucket,
                object_name,
                data,
                content_type=content_type,
            )
        except Exception as exc:  # SDK failures → dominio
            raise StorageError(f"upload falló para {object_name}: {exc}") from exc
        return StorageResult(
            bucket=self.__bucket,
            object_name=object_name,
            uploaded_at=datetime.now(UTC).isoformat(),
        )

    def object_exists(self, object_name: str) -> bool:
        client = self._get_client()
        try:
            client.head_object(self.__namespace, self.__bucket, object_name)
            return True
        except oci.exceptions.ServiceError as exc:
            if exc.status == 404:
                return False
            raise StorageError(f"object_exists falló para {object_name}: {exc}") from exc

    def list_objects(
        self,
        prefix: str | None = None,
        limit: int = 100,
        start: str | None = None,
    ) -> StorageListing:
        client = self._get_client()
        req_prefix = self._resolved_prefix(prefix)
        try:
            response = client.list_objects(
                self.__namespace,
                self.__bucket,
                prefix=req_prefix,
                limit=limit,
                start=start,
                fields="size,etag,timeCreated,timeModified",
            )
        except Exception as exc:
            raise StorageError(f"list_objects falló: {exc}") from exc

        data = response.data
        lst = [
            StorageObject(
                name=obj.name,
                size=obj.size,
                etag=obj.etag,
                time_modified=obj.time_modified.isoformat() if obj.time_modified else None,
            )
            for obj in (data.objects or [])
        ]
        return StorageListing(
            bucket=self.__bucket,
            namespace=self.__namespace,
            prefix=req_prefix,
            count=len(lst),
            next_start=getattr(data, "next_start_with", None),
            objects=lst,
        )


def build_object_name(tipo: str, doc_id: str, nombre: str) -> str:
    """Construye el nombre de objeto según la convención DT-07:
    `{tipo}/{doc_id}/{timestamp}_{nombre}`.

    El timestamp es UTC en formato `YYYYMMDDHHMMSS` — sin colisiones razonables
    y clasificable por fecha en el listado del bucket.
    """
    stamp = datetime.now(ZoneInfo("UTC")).strftime("%Y%m%d%H%M%S")
    sane = "/".join(nombre.split("/"))  # prevenir inyección de rutas desde el nombre del archivo
    return f"{tipo}/{doc_id}/{stamp}_{sane}"