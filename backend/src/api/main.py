"""API pública del monolito (COMP-11, FE-API-001 → FE-API-002).

Contrato de endpoints (Fase 6 del Plan Técnico). Este archivo declara
ÚNICAMENTE la forma de la API — rutas, métodos HTTP, request/response
models — sin lógica ejecutable: cada handler delega (en la implementación
futura) en `PipelineOrchestrator`, nunca contiene lógica de negocio propia
(regla explícita de COMP-11: "main.py solo orquesta").

# NOTA: `app = FastAPI(...)` y los decoradores `@app.post/get(...)` son
# declaración de contrato (firma + rutas + schemas), no ejecución de
# lógica de negocio. Ningún handler llama a un servicio real.
"""
from fastapi import FastAPI, UploadFile, File

from src.api.schemas import (
    IngestResponse,
    AdaptRequest,
    AdaptAcceptedResponse,
    HealthResponse,
)
from src.output.schema import NuevaMenteOutput

app = FastAPI(title="NuevaMente API")


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Ver Fase 6. Implementación futura (smoke test antes de cada demo)."""
    ...


@app.post("/ingest", response_model=IngestResponse, status_code=201)
def ingest_document(file: UploadFile = File(...)) -> IngestResponse:
    """RF-001. Delega en `ingestion.router.IngestionRouter` +
    `storage.upload.upload_original` (implementación futura).

    Errores (ver `api/schemas.py::ErrorResponse`):
        400 INVALID_FILE — archivo inválido/corrupto/tamaño excedido.
    """
    ...


@app.post("/adapt", response_model=AdaptAcceptedResponse, status_code=202)
def request_adaptation(request: AdaptRequest) -> AdaptAcceptedResponse:
    """RF-009..RF-013. Encola un `Job` y delega el procesamiento en
    `api.orchestrator.PipelineOrchestrator` (implementación futura,
    asíncrona — background task o worker, a definir).

    Errores:
        404 DOCUMENT_NOT_FOUND — `document_id` inexistente.
    """
    ...


@app.get("/adapt/{job_id}", response_model=NuevaMenteOutput)
def get_adaptation_result(job_id: str) -> NuevaMenteOutput:
    """Consulta el estado/resultado de un `Job` (ver `db.session.get_job`).

    Implementación futura.
    """
    ...
