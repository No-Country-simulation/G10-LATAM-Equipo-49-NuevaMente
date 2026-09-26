import os
from pathlib import Path

import oci
from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[2] / ".env"


class OciStorageService:
    def __init__(self, client=None, config_file=None, profile=None,
                 namespace=None, bucket=None, prefix=None):
        load_dotenv(ENV_FILE)
        self.config_file = config_file or os.getenv("OCI_CONFIG_FILE", "~/.oci/config")
        self.profile = profile or os.getenv("OCI_PROFILE", "DEFAULT")
        self.namespace = namespace or os.getenv("OCI_NAMESPACE")
        self.bucket = bucket or os.getenv("OCI_BUCKET_NAME")
        default_prefix = os.getenv("OCI_PREFIX", "")
        self.prefix = (prefix if prefix is not None else default_prefix).strip("/")
        self._client = client

    def _get_client(self):
        if self._client is None:
            config = oci.config.from_file(os.path.expanduser(self.config_file), self.profile)
            self._client = oci.object_storage.ObjectStorageClient(config)
        return self._client

    def list_objects(self, prefix=None, limit=100, start=None):
        if not self.namespace or not self.bucket:
            raise ValueError("OCI_NAMESPACE y OCI_BUCKET_NAME son obligatorios")

        client = self._get_client()
        req_prefix = prefix or self.prefix or None
        response = client.list_objects(
            self.namespace, self.bucket, prefix=req_prefix, limit=limit, start=start,
            fields="size,etag,timeCreated,timeModified"
        )
        data = response.data
        objects = data.objects or []
        return {
            "bucket": self.bucket,
            "namespace": self.namespace,
            "prefix": req_prefix,
            "count": len(objects),
            "next_start": getattr(data, "next_start_with", None),
            "objects": [
                {
                    "name": obj.name,
                    "size": obj.size,
                    "etag": obj.etag,
                    "time_modified": obj.time_modified.isoformat() if obj.time_modified else None,
                }
                for obj in objects
            ],
        }