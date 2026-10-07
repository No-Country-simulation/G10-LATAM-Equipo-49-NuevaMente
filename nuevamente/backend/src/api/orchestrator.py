"""Orquestador del pipeline (COMP-11).

Coordina, EN ORDEN, los servicios de cada capa. `api/main.py` solo delega
aquí (regla de COMP-11: "main.py solo orquesta").

Estado de implementación:
    - Ingesta (RF-001): COMPLETA → validar, extraer, limpiar, chunkear,
      subir el original y persistir documento + chunks + indexar en vectorstore.
    - Adaptación (`/adapt`): RAG real con fallback a mock. El retrieval, el LLM
      y la validación de fidelidad se integran progresivamente.
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
from src.embeddings.embed_chunks import embed_chunks
from src.embeddings.factory import get_embedding_provider
from src.generation.mock_adapter import MOCK_NOTICE, build_mock_content
from src.generation.profiles import FORMATOS_MVP, NICHOS_MVP, PERFILES_MVP
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
from src.rag.context_builder import build_context
from src.rag.retrieval_service import DefaultRetrievalService
from src.storage.base import StorageClient
from src.storage.factory import get_storage_client
from src.storage.upload import upload_original, upload_result_json
from src.validation.fidelity_checker import DefaultValidationService
from src.vectorstore.factory import get_vectorstore
from src.vectorstore.store import persist_chunks

log = get_logger(__name__)


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

        # --- Paso 3.5: indexar chunks en el vectorstore ---
        with log_stage(log, "embeddings", document_id=doc_id):
            vectors = embed_chunks(chunks, get_embedding_provider())
        with log_stage(log, "vectorstore_index", document_id=doc_id):
            persist_chunks(chunks, vectors, get_vectorstore())

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
        if request.nicho not in NICHOS_MVP:
            raise InvalidRequestError(
                f"Nicho no soportado: {request.nicho!r}. Opciones: {', '.join(NICHOS_MVP)}."
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
        """Genera el resultado usando RAG con fallback a mock, y si hay `job_id`,
        guarda el JSON en el almacenamiento.

        Lanza:
            DocumentNotFoundError: si `request.document_id` no existe.
            NoContextError: si el retrieval no encuentra contexto suficiente
                (regla de negocio RF-009 — NO se degrada a mock).
        """
        document = get_document(request.document_id)
        if document is None:
            raise DocumentNotFoundError(
                "No existe un documento indexado con ese document_id"
            )
        chunks = get_chunks(request.document_id)
        if not chunks:
            raise NoContextError("El documento no tiene fragmentos disponibles.")

        store = get_vectorstore()
        # Fallback técnico: el documento existe pero no está indexado (índice vacío)
        if store.count(doc_id=request.document_id) == 0:
            content, used = build_mock_content(
                request.perfil, request.formato, request.nicho, chunks
            )
            output = NuevaMenteOutput(
                status="PARTIAL",
                metadatos=Metadatos(
                    doc_id=request.document_id,
                    perfil=request.perfil,
                    formato=request.formato,
                    nicho=request.nicho,
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

        # RAG real: retrieval + context_builder + validación
        # NoContextError se propaga: es regla de negocio (RF-009), no fallo técnico
        retrieval_service = DefaultRetrievalService()
        # Incluir el primer chunk como "tema" para que la query tenga términos
        # del documento y los embeddings mock produzcan match (no hay semántica).
        tema_para_retrieval = chunks[0].text[:200] if chunks else None
        matches = retrieval_service.retrieve(
            doc_id=request.document_id,
            perfil=request.perfil,
            nicho=request.nicho,
            tema=tema_para_retrieval,
        )
        contexto = build_context(matches)  # lanza NoContextError si no hay matches sobre umbral

        # Generar contenido (mock) y validar fidelidad contra el contexto
        mock_chunks = [
            type(
                "_MockChunk",
                (),
                {"id": m.chunk_id, "text": m.text, "page": m.page, "section": None},
            )()
            for m in matches[:3]
        ]
        content, used = build_mock_content(
            request.perfil, request.formato, request.nicho, mock_chunks
        )

        # Paso 4: validación de fidelidad
        validation_service = DefaultValidationService()
        fidelity_eval = validation_service.validate(content.cuerpo, contexto)

        output = NuevaMenteOutput(
            status="PARTIAL",
            metadatos=Metadatos(
                doc_id=request.document_id,
                perfil=request.perfil,
                formato=request.formato,
                nicho=request.nicho,
                sources=[Source(chunk_id=m.chunk_id, page=m.page) for m in matches[:3]],
            ),
            contenido_adaptado=content,
            evaluacion_calidad=EvaluacionCalidad(
                fidelidad_score=fidelity_eval.score,
                claims_no_soportados=fidelity_eval.claims_no_soportados,
                observaciones=fidelity_eval.observaciones or [MOCK_NOTICE],
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
