"""API pública del monolito (COMP-11, FE-API-001 → FE-API-002).

Endpoints (Fase 6 del Plan Técnico): `GET /health`, `POST /ingest`,
`POST /adapt`, `GET /adapt/{job_id}`. Cada handler delega en
`PipelineOrchestrator`: este archivo no contiene lógica de negocio.

Todo error se devuelve como `{"error": {"code": ..., "message": ...}}`.
"""
import json

from fastapi import BackgroundTasks, FastAPI, File, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response

from src.api.orchestrator import PipelineOrchestrator
from src.api.schemas import (
    AdaptAcceptedResponse,
    AdaptRequest,
    ErrorResponse,
    HealthResponse,
    IngestResponse,
    JobPendingResponse,
)
from src.core.config import get_settings
from src.core.exceptions import JobNotFoundError, NuevaMenteError
from src.core.logging import configure_logging, get_logger
from src.db.models import FINAL_STATUSES
from src.db.session import get_job
from src.output.schema import NuevaMenteOutput

configure_logging()
log = get_logger(__name__)
settings = get_settings()

app = FastAPI(
    title=f"{settings.APP_NAME} API",
    version=settings.APP_VERSION,
    description="API del MVP NuevaMente: ingesta de documentos y adaptación (mock).",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

orchestrator = PipelineOrchestrator()


def error_response(status_code: int, code: str, message: str) -> JSONResponse:
    return JSONResponse(
        status_code=status_code, content={"error": {"code": code, "message": message}}
    )


@app.exception_handler(NuevaMenteError)
async def handle_domain_error(request: Request, exc: NuevaMenteError) -> JSONResponse:
    log.warning("domain_error", path=request.url.path, code=exc.code, error=exc.message)
    return error_response(exc.http_status, exc.code, exc.message)


@app.exception_handler(RequestValidationError)
async def handle_validation_error(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = "; ".join(
        f"{'.'.join(str(part) for part in err['loc'])}: {err['msg']}" for err in exc.errors()
    )
    return error_response(422, "INVALID_REQUEST", f"Solicitud inválida — {details}")


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    log.exception("unexpected_error", path=request.url.path)
    return error_response(500, "INTERNAL_ERROR", "Error interno del servidor.")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Smoke test antes de cada demo."""
    return HealthResponse()


@app.post(
    "/ingest",
    response_model=IngestResponse,
    status_code=201,
    responses={400: {"model": ErrorResponse}, 502: {"model": ErrorResponse}},
)
def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    """RF-001. Sube PDF, Markdown o TXT (≤ MAX_FILE_SIZE_MB) y devuelve `document_id`.

    Errores: 400 INVALID_FILE | SCANNED_PDF | DOCUMENT_TOO_LARGE, 502 STORAGE_ERROR.
    """
    # Se lee como máximo tamaño+1 bytes: basta para detectar el exceso sin cargar todo en memoria.
    max_bytes = get_settings().MAX_FILE_SIZE_MB * 1024 * 1024
    content = file.file.read(max_bytes + 1)
    return orchestrator.ingest(file.filename or "", content)


@app.post(
    "/adapt",
    response_model=AdaptAcceptedResponse,
    status_code=202,
    responses={400: {"model": ErrorResponse}, 404: {"model": ErrorResponse}},
)
def request_adaptation(
    request: AdaptRequest, background_tasks: BackgroundTasks
) -> AdaptAcceptedResponse:
    """RF-009..RF-013 (mock). Encola un `Job`; consultar con `GET /adapt/{job_id}`."""
    job = orchestrator.request_adaptation(request)
    background_tasks.add_task(orchestrator.execute_job, job.job_id, request)
    return AdaptAcceptedResponse(job_id=job.job_id)


@app.get(
    "/adapt/{job_id}",
    response_model=None,
    responses={
        200: {"model": NuevaMenteOutput},
        202: {"model": JobPendingResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)
def get_adaptation_result(job_id: str) -> Response:
    """200 con el resultado final, 202 mientras se procesa, 404 si el job no existe."""
    job = get_job(job_id)
    if job is None:
        raise JobNotFoundError("No existe un job con ese job_id")

    if job.status not in FINAL_STATUSES:
        return JSONResponse(
            status_code=202, content={"job_id": job.job_id, "status": job.status}
        )
    if job.status == "ERROR" or job.result_json is None:
        return error_response(500, "INTERNAL_ERROR", job.error or "La adaptación falló.")
    return JSONResponse(content=json.loads(job.result_json))
