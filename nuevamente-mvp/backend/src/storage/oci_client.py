import oci
from src.core.config import settings
from src.core.exceptions import StorageError


class OCIStorageClient:
    def __init__(self):
        try:
            config = oci.config.from_file(
                file_location=settings.OCI_CONFIG_FILE,
                profile_name=settings.OCI_PROFILE,
            )
            self.client = oci.object_storage.ObjectStorageClient(config)
            self.namespace = settings.OCI_NAMESPACE or self.client.get_namespace().data
            self.bucket = settings.OCI_BUCKET_NAME
        except Exception as exc:  # noqa: BLE001
            raise StorageError(f"No se pudo inicializar el cliente OCI: {exc}") from exc

    def upload_bytes(self, object_name: str, data: bytes, content_type: str) -> dict:
        try:
            self.client.put_object(
                namespace_name=self.namespace,
                bucket_name=self.bucket,
                object_name=object_name,
                put_object_body=data,
                content_type=content_type,
            )
        except Exception as exc:  # noqa: BLE001
            raise StorageError(f"Fallo al subir '{object_name}' a OCI") from exc

        return {"bucket": self.bucket, "object_name": object_name}

    def object_exists(self, object_name: str) -> bool:
        try:
            self.client.head_object(
                namespace_name=self.namespace, bucket_name=self.bucket, object_name=object_name,
            )
            return True
        except oci.exceptions.ServiceError as exc:
            if exc.status == 404:
                return False
            raise StorageError(f"Error verificando '{object_name}' en OCI") from exc
