"""API pública del monolito (COMP-11, FE-API-001 → FE-API-002).

`main.py` solo orquesta: cada handler delega en `PipelineOrchestrator`;
no contiene lógica de negocio propia (regla COMP-11). Los errores de dominio
se traducen a `ErrorResponse` vía exception handlers.

Flujo implementado:
    POST /ingest        → valida, extrae, persiste (SQLite + embeddings) → 201
    POST /adapt         → crea Job QUEUED, procesa en background → 202
    GET  /adapt/{id}    → estado/resultado del Job → 200
    GET  /health        → smoke test
"""
from fastapi import FastAPI, File, UploadFile
from fastapi.concurrency import run_in_threadpool
from fastapi.responses import JSONResponse

from src.api.orchestrator import PipelineOrchestrator
from src.api.schemas import (
    AdaptAcceptedResponse,
    AdaptRequest,
    ErrorDetail,
    ErrorResponse,
    HealthResponse,
    IngestResponse,
)
from src.core.exceptions import (
    DocumentNotFoundError,
    InvalidFileError,
    NoContextError,
    NuevaMenteError,
    ScannedPdfError,
)
from src.db import session as db
from src.ingestion.router import IngestionRouter
from src.output.schema import AlmacenamientoOCI, EvaluacionCalidad, Metadatos, NuevaMenteOutput

app = FastAPI(title="NuevaMente API")

_orchestrator = PipelineOrchestrator()
_router = IngestionRouter()


# ── Errores → ErrorResponse (contrato de errores, Fase 6) ───────────
def _error(content: ErrorResponse, status: int) -> JSONResponse:
    return JSONResponse(status_code=status, content=content.model_dump())


@app.exception_handler(InvalidFileError)
async def invalid_file(request, exc: InvalidFileError) -> JSONResponse:
    return _error(ErrorResponse(error=ErrorDetail(code=exc.code, message=str(exc))), 400)


@app.exception_handler(ScannedPdfError)
async def scanned_pdf(request, exc: ScannedPdfError) -> JSONResponse:
    return _error(ErrorResponse(error=ErrorDetail(code=exc.code, message=str(exc))), 400)


@app.exception_handler(DocumentNotFoundError)
async def document_not_found(request, exc: DocumentNotFoundError) -> JSONResponse:
    return _error(ErrorResponse(error=ErrorDetail(code=exc.code, message=str(exc))), 404)


@app.exception_handler(NuevaMenteError)
async def dominio_error(request, exc: NuevaMenteError) -> JSONResponse:
    return _error(ErrorResponse(error=ErrorDetail(code=exc.code, message=str(exc))), 500)


# ── Endpoints ────────────────────────────────────────────────────────
@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@app.post("/ingest", response_model=IngestResponse, status_code=201)
async def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    """RF-001. Delega en `ingestion.router.IngestionRouter` y persiste el
    documento + embeddings en el vectorstore (modo mock, sin red)."""
    content = await file.read()
    result = await run_in_threadpool(_router.ingest, file.filename or "", content)
    await run_in_threadpool(_orchestrator.register_document, result)
    return IngestResponse(
        document_id=result.document_id,
        file_type=result.file_type,
        status="INGESTED",
    )


@app.post("/adapt", response_model=AdaptAcceptedResponse, status_code=202)
async def request_adaptation(request: AdaptRequest) -> AdaptAcceptedResponse:
    """RF-009..RF-013. Encola un `Job` y delega el procesamiento en
    `PipelineOrchestrator` (asíncrono)."""
    if db.get_document(request.document_id) is None:
        raise DocumentNotFoundError(f"document_id {request.document_id!r} no existe")

    job = db.create_job(request.document_id)
    await run_in_threadpool(_procesar_job, job_id=job.job_id, request=request)
    return AdaptAcceptedResponse(job_id=job.job_id, status="PROCESSING")


@app.get("/adapt/{job_id}", response_model=NuevaMenteOutput)
def get_adaptation_result(job_id: str) -> NuevaMenteOutput:
    """Consulta el estado/resultado de un `Job` (ver `db.session.get_job`)."""
    job = db.get_job(job_id)
    if job is None:
        raise DocumentNotFoundError(f"job_id {job_id!r} no existe")

    if job.result_json:
        return NuevaMenteOutput.model_validate_json(job.result_json)

    # En curso o fallado: devuelve el estado vigente sin inventar contenido.
    return NuevaMenteOutput(
        status=job.status,
        metadatos=Metadatos(doc_id=job.document_id, perfil="", formato="", nivel_detalle=""),
        evaluacion_calidad=EvaluacionCalidad(observaciones=[job.error] if job.error else []),
        almacenamiento_oci=AlmacenamientoOCI(bucket=""),
    )


def _procesar_job(job_id: str, request: AdaptRequest) -> None:
    """Ejecuta el pipeline y persiste el resultado JSON en el Job."""
    db.update_job_status(job_id, "PROCESSING")
    try:
        output = _orchestrator.run_adaptation(request, job_id=job_id)
        db.set_job_result(
            job_id,
            result_object_name=output.almacenamiento_oci.object_name_json or "",
            result_json=output.model_dump_json(),
        )
        db.update_job_status(job_id, output.status)
    except NoContextError:
        db.update_job_status(job_id, "NO_CONTEXT")
    except NuevaMenteError as exc:
        db.update_job_status(job_id, "ERROR", error=str(exc))
    except Exception as exc:  # noqa: BLE001 — degradar a ERROR
        db.update_job_status(job_id, "ERROR", error=str(exc))