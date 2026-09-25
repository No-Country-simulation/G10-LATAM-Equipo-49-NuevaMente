import uuid

from fastapi import FastAPI, UploadFile, File, BackgroundTasks, HTTPException

from src.api.schemas import IngestResponse, AdaptRequest, AdaptAcceptedResponse
from src.api.orchestrator import run_adaptation_pipeline, _get_storage_client
from src.ingestion.service import IngestionService
from src.processing.chunking import chunk_text
from src.embeddings.factory import get_embedding_provider
from src.embeddings.embed_chunks import embed_chunks
from src.vectorstore.store import persist_chunks
from src.storage.upload import upload_original
from src.db.session import create_job, get_job
from src.core.exceptions import NuevaMenteError, InvalidFileError, ScannedPdfError, DocumentNotFoundError
from src.core.logging import configure_logging, get_logger

configure_logging()
log = get_logger(__name__)

app = FastAPI(title="NuevaMente API")

ingestion_service = IngestionService()


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest(file: UploadFile = File(...)):
    content = await file.read()
    try:
        result = ingestion_service.ingest(file.filename, content)

        chunks = chunk_text(result.raw_text, result.document_id, result.pages)
        provider = get_embedding_provider()
        vectors = embed_chunks(chunks, provider)
        persist_chunks(chunks, vectors)

        storage = _get_storage_client()
        upload_original(storage, result.document_id, content,
                         content_type="application/octet-stream")

        return IngestResponse(document_id=result.document_id, file_type=result.file_type,
                               status="INGESTED")
    except (InvalidFileError, ScannedPdfError) as exc:
        raise HTTPException(status_code=400, detail={"code": exc.code, "message": str(exc)})
    except NuevaMenteError as exc:
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR", "message": str(exc)})


@app.post("/adapt", response_model=AdaptAcceptedResponse, status_code=202)
def adapt(request: AdaptRequest, background_tasks: BackgroundTasks):
    job_id = f"job_{uuid.uuid4().hex[:10]}"
    create_job(job_id, request.document_id)
    background_tasks.add_task(run_adaptation_pipeline, job_id, request)
    return AdaptAcceptedResponse(job_id=job_id, status="PROCESSING")


@app.get("/adapt/{job_id}")
def get_adapt_result(job_id: str):
    import json, pathlib

    job = get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail={"code": "DOCUMENT_NOT_FOUND",
                                                       "message": "job_id inexistente"})
    if job.status in ("QUEUED", "PROCESSING"):
        return {"status": job.status}
    if job.status == "ERROR":
        return {"error": {"code": "INTERNAL_ERROR", "message": job.error}}

    result_path = pathlib.Path(f"./data/results/{job_id}.json")
    if not result_path.exists():
        raise HTTPException(status_code=500, detail={"code": "INTERNAL_ERROR",
                                                       "message": "Resultado no encontrado"})
    return json.loads(result_path.read_text(encoding="utf-8"))
