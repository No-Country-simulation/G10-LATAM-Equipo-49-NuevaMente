"""Contrato del cliente de almacenamiento (COMP-09).

Tomado del ejemplo de la especificación de arquitectura. Cualquier
implementación (OCI real o mock) debe cumplir este `Protocol`; ningún otro
componente debe conocer el SDK de OCI directamente (RNF-005).
"""
from typing import Protocol
from pydantic import BaseModel


class StorageResult(BaseModel):
    bucket: str
    object_name: str
    url: str | None = None
    uploaded_at: str | None = None


class StorageClient(Protocol):
    """Sube bytes a almacenamiento de objetos y verifica su existencia."""

    def upload_bytes(
        self,
        object_name: str,
        data: bytes,
        content_type: str,
    ) -> StorageResult:
        """Sube `data` bajo `object_name`.

        Lanza:
            StorageError: ante fallo de red o de credenciales.

        Implementación futura.
        """
        ...

    def object_exists(self, object_name: str) -> bool:
        """Verifica que `object_name` exista en el bucket (post-upload,
        OCI-005).

        Implementación futura.
        """
        ...
