import json
import pathlib


class MockOCIStorageClient:
    def __init__(self, base_dir: str = "./data/mock_oci"):
        self.base = pathlib.Path(base_dir)
        self.base.mkdir(parents=True, exist_ok=True)
        self.bucket = "mock-bucket"

    def upload_bytes(self, object_name: str, data: bytes, content_type: str) -> dict:
        path = self.base / object_name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return {"bucket": self.bucket, "object_name": object_name}

    def object_exists(self, object_name: str) -> bool:
        return (self.base / object_name).exists()
