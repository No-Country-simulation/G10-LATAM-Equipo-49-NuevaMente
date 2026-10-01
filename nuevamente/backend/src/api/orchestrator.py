"""Orquestador del pipeline (COMP-11).

Coordina, EN ORDEN, los servicios de cada capa. `api/main.py` solo delega
aquí (regla de COMP-11: "main.py solo orquesta").

Estado de implementación:
    - Ingesta (RF-001): COMPLETA → validar, extraer, limpiar, chunkear,
      subir el original y persistir documento + chunks.
    - Adaptación (`/adapt`): MOCK → usa los primeros chunks reales; el
      retrieval (RAG), el LLM y la validación de fidelidad se integran en
      Semana 2 y 3 sin cambiar este contrato.
"""
from datetime import UTC, datetime

from src.api.schemas import AdaptRequest, IngestResponse
from src.core.exceptions import (
    DocumentNotFoundError,
    InvalidFileError,
    InvalidRequestError,
    NoContextError,
    NuevaMenteError,
    StorageError,
)
from src.core.logging import get_logger, log_stage
from src.db.models import DocumentRecord, Job
from src.db.session import (
    create_job,
    get_chunks,
    get_document,
    save_document,
    save_job_result,
    update_job_status,
)
from src.generation.mock_adapter import MOCK_NOTICE, build_mock_content
from src.generation.profiles import FORMATOS_MVP, PERFILES_MVP
from src.ingestion.router import IngestionRouter
from src.output.schema import (
    AlmacenamientoOCI,
    EvaluacionCalidad,
    Metadatos,
    NuevaMenteOutput,
    Source,
)
from src.processing.chunking import chunk_text
from src.processing.cleaning import prepare_document_text
from src.storage.base import StorageClient
from src.storage.factory import get_storage_client
from src.storage.upload import upload_original, upload_result_json

log = get_logger(__name__)

NIVELES_DETALLE = ("breve", "estandar", "profundo")


class PipelineOrchestrator:
    """Punto único de coordinación entre capas."""

    def __init__(
        self,
        storage_client: StorageClient | None = None,
        ingestion_router: IngestionRouter | None = None,
    ) -> None:
        self._storage_client = storage_client
        self._router = ingestion_router or IngestionRouter()

    def _storage(self) -> StorageClient:
        return self._storage_client or get_storage_client()

    # ------------------------------------------------------------------ ingesta
    def ingest(self, filename: str, content: bytes) -> IngestResponse:
        """RF-001: valida, extrae, limpia, chunkea, sube el original y persiste.

        Lanza:
            InvalidFileError, ScannedPdfError, DocumentTooLargeError, StorageError.
        """
        with log_stage(log, "ingestion", filename=filename, size_bytes=len(content)):
            result = self._router.ingest(filename, content)
        doc_id = result.document_id

        with log_stage(log, "cleaning", document_id=doc_id):
            text, pages = prepare_document_text(result.raw_text, result.pages)

        with log_stage(log, "chunking", document_id=doc_id):
            chunks = chunk_text(text, doc_id, pages)
        if not chunks:
            raise InvalidFileError("No se pudo generar ningún fragmento del documento.")

        with log_stage(log, "storage_upload", document_id=doc_id):
            stored = upload_original(doc_id, result.filename, content, self._storage())

        record = DocumentRecord(
            document_id=doc_id,
            filename=result.filename,
            file_type=result.file_type,
            size_bytes=len(content),
            page_count=len(result.pages),
            char_count=len(text),
            chunk_count=len(chunks),
            storage_object_name=stored.object_name,
            warnings=result.warnings,
            created_at=datetime.now(UTC).isoformat(timespec="seconds"),
        )
        with log_stage(log, "persist", document_id=doc_id):
            save_document(record, chunks)

        return IngestResponse(
            document_id=doc_id,
            file_type=result.file_type,
            filename=record.filename,
            size_bytes=record.size_bytes,
            page_count=record.page_count,
            char_count=record.char_count,
            chunk_count=record.chunk_count,
            storage_object_name=record.storage_object_name,
            warnings=record.warnings,
        )

    # ---------------------------------------------------------------- adaptación
    @staticmethod
    def _validate_request(request: AdaptRequest) -> None:
        if request.perfil not in PERFILES_MVP:
            raise InvalidRequestError(
                f"Perfil no soportado: {request.perfil!r}. Opciones: {', '.join(PERFILES_MVP)}."
            )
        if request.formato not in FORMATOS_MVP:
            raise InvalidRequestError(
                f"Formato no soportado: {request.formato!r}. Opciones: {', '.join(FORMATOS_MVP)}."
            )
        if request.nivel_detalle not in NIVELES_DETALLE:
            raise InvalidRequestError(
                f"Nivel de detalle no soportado: {request.nivel_detalle!r}. "
                f"Opciones: {', '.join(NIVELES_DETALLE)}."
            )

    def request_adaptation(self, request: AdaptRequest) -> Job:
        """Valida la solicitud y crea un `Job` en estado QUEUED.

        Lanza:
            InvalidRequestError: parámetros inválidos.
            DocumentNotFoundError: `document_id` inexistente.
        """
        self._validate_request(request)
        if get_document(request.document_id) is None:
            raise DocumentNotFoundError(
                "No existe un documento indexado con ese document_id"
            )
        return create_job(request.document_id)

    def run_adaptation(
        self, request: AdaptRequest, job_id: str | None = None
    ) -> NuevaMenteOutput:
        """Genera el resultado MOCK y, si hay `job_id`, guarda el JSON en el almacenamiento.

        Lanza:
            DocumentNotFoundError: si `request.document_id` no existe.
            NoContextError: si el documento no tiene chunks.
        """
        document = get_document(request.document_id)
        if document is None:
            raise DocumentNotFoundError(
                "No existe un documento indexado con ese document_id"
            )
        chunks = get_chunks(request.document_id)
        if not chunks:
            raise NoContextError("El documento no tiene fragmentos disponibles.")

        content, used = build_mock_content(
            request.perfil, request.formato, request.nicho, request.nivel_detalle, chunks
        )
        output = NuevaMenteOutput(
            status="PARTIAL",
            metadatos=Metadatos(
                doc_id=request.document_id,
                perfil=request.perfil,
                formato=request.formato,
                nicho=request.nicho,
                nivel_detalle=request.nivel_detalle,
                sources=[Source(chunk_id=c.id, page=c.page) for c in used],
            ),
            contenido_adaptado=content,
            evaluacion_calidad=EvaluacionCalidad(
                fidelidad_score=None, observaciones=[MOCK_NOTICE]
            ),
        )

        if job_id is not None:
            self._store_result(output, document.storage_object_name, request, job_id)
        return output

    def _store_result(
        self,
        output: NuevaMenteOutput,
        original_object: str | None,
        request: AdaptRequest,
        job_id: str,
    ) -> None:
        """Sube el JSON del resultado; si falla, degrada con una observación (COMP-09)."""
        try:
            with log_stage(log, "result_upload", document_id=request.document_id, job_id=job_id):
                stored = upload_result_json(
                    request.document_id,
                    job_id,
                    output.model_dump_json(indent=2).encode("utf-8"),
                    self._storage(),
                )
        except StorageError as exc:
            output.evaluacion_calidad.observaciones.append(
                f"No se pudo guardar el resultado en el almacenamiento: {exc.message}"
            )
            return
        output.almacenamiento_oci = AlmacenamientoOCI(
            bucket=stored.bucket,
            object_name_original=original_object,
            object_name_json=stored.object_name,
            uploaded_at=stored.uploaded_at,
        )

    def execute_job(self, job_id: str, request: AdaptRequest) -> None:
        """Tarea en segundo plano: ejecuta la adaptación y persiste el resultado."""
        update_job_status(job_id, "PROCESSING")
        try:
            output = self.run_adaptation(request, job_id=job_id)
            stored_name = (
                output.almacenamiento_oci.object_name_json if output.almacenamiento_oci else None
            )
            save_job_result(job_id, output.status, output.model_dump_json(), stored_name)
        except NuevaMenteError as exc:
            log.error("job_failed", job_id=job_id, code=exc.code, error=exc.message)
            update_job_status(job_id, "ERROR", exc.message)
        except Exception:
            log.exception("job_failed", job_id=job_id, code="INTERNAL_ERROR")
            update_job_status(job_id, "ERROR", "Error interno durante la adaptación.")
