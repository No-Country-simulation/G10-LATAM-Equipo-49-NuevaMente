from typing import Literal
from pydantic import BaseModel


class Job(BaseModel):
    job_id: str
    document_id: str
    status: Literal["QUEUED", "PROCESSING", "SUCCESS", "NO_CONTEXT", "PARTIAL", "ERROR"]
    result_object: str | None = None
    error: str | None = None
