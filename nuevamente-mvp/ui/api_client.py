import httpx

API_BASE = "http://localhost:8000"


def ingest_file(filename: str, content: bytes) -> dict:
    files = {"file": (filename, content)}
    response = httpx.post(f"{API_BASE}/ingest", files=files, timeout=60)
    response.raise_for_status()
    return response.json()


def request_adaptation(payload: dict) -> dict:
    response = httpx.post(f"{API_BASE}/adapt", json=payload, timeout=30)
    response.raise_for_status()
    return response.json()


def poll_result(job_id: str) -> dict:
    response = httpx.get(f"{API_BASE}/adapt/{job_id}", timeout=30)
    response.raise_for_status()
    return response.json()
