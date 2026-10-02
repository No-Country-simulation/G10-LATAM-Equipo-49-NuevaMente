"""Contrato del cliente de almacenamiento (COMP-09).

Cualquier implementación (OCI real o mock) debe cumplir este `Protocol`;
ningún otro componente debe conocer el SDK de OCI directamente (RNF-005).
El Protocol se extiende con `list_objects` y `get_namespace` para cubrir
el caso de lectura/listado que el rol cloud ya resolvió y probó (OCI-001/
OCI-002), además de la escritura/verificación (OCI-003/OCI-005).
"""
from typing import Protocol

from pydantic import BaseModel


class StorageResult(BaseModel):
    bucket: str
    object_name: str
    url: str | None = None
    uploaded_at: str | None = None


class StorageObject(BaseModel):
    """Metadatos devueltos por `list_objects` (forma mínima del listado)."""

    name: str
    size: int
    etag: str | None = None
    time_modified: str | None = None


class StorageListing(BaseModel):
    bucket: str
    namespace: str
    prefix: str | None = None
    count: int = 0
    next_start: str | None = None
    objects: list[StorageObject] = []


class StorageClient(Protocol):
    """Sube bytes a almacenamiento de objetos, verifica su existencia y
    puede listarlos."""

    def upload_bytes(
        self,
        object_name: str,
        data: bytes,
        content_type: str,
    ) -> StorageResult:
        """Sube `data` bajo `object_name`.

        Lanza:
            StorageError: ante fallo de red o de credenciales.
        """
        ...

    def object_exists(self, object_name: str) -> bool:
        """Verifica que `object_name` exista en el bucket (post-upload,
        OCI-005)."""
        ...

    def get_namespace(self) -> str:
        """Devuelve el namespace del tenancy configurado."""
        ...

    def list_objects(
        self,
        prefix: str | None = None,
        limit: int = 100,
        start: str | None = None,
    ) -> StorageListing:
        """Lista los objetos del bucket con paginación (`start` → `next_start`)."""
        ...