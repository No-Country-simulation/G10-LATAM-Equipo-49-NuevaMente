"""Orquestador del pipeline (COMP-11).

Coordina, EN ORDEN, los servicios de cada capa. `api/main.py` solo delega
aquí (regla de COMP-11: "main.py solo orquesta").

Estado de implementación:
    - Ingesta (RF-001): COMPLETA → validar, extraer, limpiar, chunkear,
      generar embeddings, subir el original y persistir documento + chunks +
      indexar (de forma atómica, con compensación ante fallos — AUD-004).
    - Adaptación (`/adapt`): RAG y generación configurados explícitamente.
      Si no hay contexto suficiente se devuelve `status=NO_CONTEXT` (AUD-002).
"""
from datetime import UTC, datetime

from src.api.schemas import AdaptRequest, IngestResponse
from src.core.config import get_settings
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
    delete_document,
    get_chunks,
    get_document,
    save_document,
    save_job_result,
    update_job_status,
)
from src.embeddings.embed_chunks import embed_chunks
from src.embeddings.factory import get_embedding_provider
from src.generation.factory import get_llm_provider
from src.generation.mock_adapter import MOCK_NOTICE, build_mock_content
from src.generation.models import AdaptationRequest
from src.generation.orchestrator import GenerationOrchestrator
from src.generation.profiles import FORMATOS_MVP, NICHOS_MVP, PERFILES_MVP
from src.ingestion.router import IngestionRouter
from src.output.assembler import assemble_output
from src.output.schema import AlmacenamientoOCI, NuevaMenteOutput, Source
from src.processing.chunking import chunk_text
from src.processing.cleaning import prepare_document_text
from src.rag.context_builder import build_context
from src.rag.retrieval_service import DefaultRetrievalService
from src.storage.base import StorageClient, StorageResult
from src.storage.factory import get_storage_client
from src.storage.upload import upload_original, upload_result_json
from src.validation.fidelity_checker import DefaultValidationService
from src.validation.models import FidelityEvaluation
from src.vectorstore.base import VectorStore
from src.vectorstore.factory import get_vectorstore
from src.vectorstore.store import persist_chunks

log = get_logger(__name__)

_OVERVIEW_CHUNKS = 3


class PipelineOrchestrator:
    """Punto único de coordinación entre capas."""

    def __init__(
        self,
        storage_client: StorageClient | None = None,
        ingestion_router: IngestionRouter | None = None,
    ) -> None:
        self._storage_client = storage_client
        self._router = ingestion_router or IngestionRouter()
        # Inyectable en tests; si es None se construye por solicitud.
        self.retrieval: DefaultRetrievalService | None = None

    def _storage(self) -> StorageClient:
        return self._storage_client or get_storage_client()

    # ------------------------------------------------------------------ ingesta
    def ingest(self, filename: str, content: bytes) -> IngestResponse:
        """RF-001: valida, extrae, limpia, chunkea, sube el original y persiste.

        Lanza:
            InvalidFileError, ScannedPdfError, DocumentTooLargeError,
            EmbeddingError, VectorStoreError, StorageError.

        *********************************************************************
        MEJORA AUD-004 — 2026-10-15
        Antes se subía el original y se persistía en SQLite ANTES de generar
        embeddings e indexar: si los embeddings fallaban, quedaban 1 documento +
        chunks + 1 original huérfano y 0 vectores (estado parcial que además era
        adaptable en silencio). Ahora los embeddings se calculan PRIMERO (sin
        efectos) y, si algo falla después, se compensa borrando índice, fila y
        objeto. Criterio de cierre: tras un fallo, 0 filas y 0 objetos.
        *********************************************************************
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

        # Paso 3: embeddings ANTES de cualquier efecto observable.
        with log_stage(log, "embeddings", document_id=doc_id):
            vectors = embed_chunks(chunks, get_embedding_provider())

        store = get_vectorstore()
        stored: StorageResult | None = None
        try:
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

            with log_stage(log, "vectorstore_index", document_id=doc_id):
                persist_chunks(chunks, vectors, store)
        except Exception:
            self._compensate_ingest(doc_id, stored, store)
            raise

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

    def _compensate_ingest(
        self,
        doc_id: str,
        stored: StorageResult | None,
        store: VectorStore,
    ) -> None:
        """Deshace una ingesta parcial (índice, filas y objeto) — AUD-004."""
        try:
            store.delete(doc_id)
        except Exception as exc:  # pragma: no cover - best effort
            log.warning("ingest_rollback_index_failed", document_id=doc_id, error=str(exc))
        try:
            delete_document(doc_id)
        except Exception as exc:  # pragma: no cover - best effort
            log.warning("ingest_rollback_db_failed", document_id=doc_id, error=str(exc))
        if stored is not None:
            try:
                self._storage().delete_object(stored.object_name)
            except Exception as exc:  # pragma: no cover - best effort
                log.warning("ingest_rollback_object_failed", document_id=doc_id, error=str(exc))

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

    @staticmethod
    def _overview_query(chunks: list) -> str:
        """Consulta *overview* cuando la solicitud no especifica `tema`.

        *********************************************************************
        MEJORA AUD-001 — 2026-10-15
        Antes, sin tema, la consulta era `chunks[0].text[:200]`, un recorte
        arbitrario del inicio del documento. Ahora se resume el documento con
        sus primeros fragmentos (similitud al centroide aproximado).
        *********************************************************************
        """
        return " ".join(chunk.text for chunk in chunks[:_OVERVIEW_CHUNKS])

    def _ensure_indexed(self, doc_id: str, chunks: list, store: VectorStore) -> None:
        """Reindexa el documento si el índice está vacío (tras un reinicio).

        *********************************************************************
        MEJORA AUD-007 — 2026-10-15
        Con el índice en memoria un reinicio dejaba `count(doc)=0` y el pipeline
        respondía con contenido mock SIN avisar. Si detectamos un índice vacío,
        reindexamos desde los chunks persistidos (reproducible); si la
        reindexación falla, el error se propaga (nada de degradación silenciosa).
        *********************************************************************
        """
        with log_stage(log, "vectorstore_reindex", document_id=doc_id):
            vectors = embed_chunks(chunks, get_embedding_provider())
            persist_chunks(chunks, vectors, store)

    def run_adaptation(
        self, request: AdaptRequest, job_id: str | None = None
    ) -> NuevaMenteOutput:
        """Genera el resultado con RAG y el proveedor configurado. En modo mock
        explícito usa fragmentos del documento; si hay `job_id`, guarda el JSON.

        Lanza:
            DocumentNotFoundError: si `request.document_id` no existe.
            NoContextError: si el documento no tiene fragmentos persistidos
                (fallo técnico); si el retrieval no encuentra contexto
                suficiente se devuelve `status=NO_CONTEXT` como resultado de
                negocio (RF-009, AUD-002).
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
        if store.count(doc_id=request.document_id) == 0:
            self._ensure_indexed(request.document_id, chunks, store)

        retrieval_service = self.retrieval or DefaultRetrievalService()
        # AUD-001: la consulta depende de la solicitud (tema). Sin tema, overview.
        tema = request.tema or self._overview_query(chunks)
        matches = retrieval_service.retrieve(
            doc_id=request.document_id,
            perfil=request.perfil,
            nicho=request.nicho,
            tema=tema,
            formato=request.formato,
        )

        try:
            contexto = build_context(matches)
        except NoContextError:
            # AUD-002: NO_CONTEXT es un resultado de negocio (HTTP 200), no un 500.
            output = assemble_output(
                doc_id=request.document_id,
                perfil=request.perfil,
                formato=request.formato,
                nicho=request.nicho,
                contenido=None,
                fidelidad=FidelityEvaluation(score=None),
                sources=[],
            )
            if job_id is not None:
                self._store_result(output, document.storage_object_name, request, job_id)
            return output

        # El modo mock es una opción explícita; un fallo del LLM no degrada
        # silenciosamente la respuesta.
        gen_request = AdaptationRequest(
            document_id=request.document_id,
            perfil=request.perfil,
            formato=request.formato,
            nicho=request.nicho,
        )
        is_mock = get_settings().LLM_PROVIDER.lower() == "mock"
        # CAMBIO H-02 INICIO — 2026-10-24
        if is_mock:
            chunks_by_id = {chunk.id: chunk for chunk in chunks}
            mock_chunks = [
                chunks_by_id[m.chunk_id] for m in matches if m.chunk_id in chunks_by_id
            ][:3]
            content, _used = build_mock_content(
                request.perfil, request.formato, request.nicho, mock_chunks
            )
        else:
            provider = get_llm_provider()
            content = GenerationOrchestrator().generate_content(
                gen_request, contexto, provider
            )
        # CAMBIO H-02 FIN — 2026-10-24

        # Paso 4: validación de fidelidad.
        validation_service = DefaultValidationService()
        fidelity_eval = validation_service.validate(content.cuerpo, contexto)

        sources = [Source(chunk_id=m.chunk_id, page=m.page) for m in matches[:3]]
        output = assemble_output(
            doc_id=request.document_id,
            perfil=request.perfil,
            formato=request.formato,
            nicho=request.nicho,
            contenido=content,
            fidelidad=fidelity_eval,
            sources=sources,
            es_mock=is_mock,
        )
        if is_mock and MOCK_NOTICE not in output.evaluacion_calidad.observaciones:
            output.evaluacion_calidad.observaciones.append(MOCK_NOTICE)

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
        except NoContextError as exc:
            log.warning("job_no_context", job_id=job_id, error=exc.message)
            update_job_status(job_id, "NO_CONTEXT", exc.message)
        except NuevaMenteError as exc:
            log.error("job_failed", job_id=job_id, code=exc.code, error=exc.message)
            update_job_status(job_id, "ERROR", exc.message)
        # CAMBIO H-02 INICIO — 2026-10-24
        except Exception:
            log.exception("job_failed_unexpectedly", job_id=job_id)
            update_job_status(job_id, "ERROR", "Error interno al generar la adaptación.")
        # CAMBIO H-02 FIN — 2026-10-24
        except Exception:
            log.exception("job_failed", job_id=job_id, code="INTERNAL_ERROR")
            update_job_status(job_id, "ERROR", "Error interno durante la adaptación.")
