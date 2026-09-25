import json
from datetime import datetime, timezone

from src.storage.oci_client import OCIStorageClient
from src.core.logging import get_logger

log = get_logger(__name__)


def upload_original(client: OCIStorageClient, document_id: str, content: bytes, content_type: str) -> str:
    object_name = f"originals/{document_id}/original"
    client.upload_bytes(object_name, content, content_type)
    log.info("original_uploaded", document_id=document_id, object_name=object_name)
    return object_name


def upload_result_json(client: OCIStorageClient, document_id: str, job_id: str, payload: dict) -> dict:
    object_name = f"generated/{document_id}/{job_id}.json"
    data = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    client.upload_bytes(object_name, data, "application/json")

    verified = client.object_exists(object_name)  # OCI-005 — verificación post-upload
    log.info("result_uploaded", document_id=document_id, job_id=job_id, verified=verified)

    return {
        "bucket": client.bucket,
        "object_name_json": object_name,
        "uploaded_at": datetime.now(timezone.utc).isoformat(),
        "verified": verified,
    }
