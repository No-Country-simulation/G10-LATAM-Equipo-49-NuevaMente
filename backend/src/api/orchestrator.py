"""Orquestador del pipeline completo (INT-001, INT-002, INT-003, COMP-11).

Responsabilidad: coordinar, EN ORDEN, las llamadas a los servicios de cada
capa (COMP-01 → COMP-09) para resolver una solicitud `POST /adapt`. Este
módulo NO contiene la lógica de cada paso (vive en cada Service); solo
coordina, para que `api/main.py` no acumule lógica de negocio (COMP-11).

Flujo implementado (modo mock, determinista):
    retrieval (COMP-05) → generación (COMP-06) → validación (COMP-07) →
    ensamblado (COMP-08) → persistencia en OCI (COMP-09).
"""
from src.api.schemas import AdaptRequest
from src.core.config import get_settings
from src.core.exceptions import DocumentNotFoundError, NoContextError, StorageError
from src.db import session as db
from src.generation.builders import build_contexto_items
from src.generation.models import AdaptationRequest
from src.generation.orchestrator import GenerationOrchestrator
from src.output.assembler import assemble_output
from src.output.schema import AlmacenamientoOCI, NuevaMenteOutput, Source
from src.processing.chunking import chunk_text
from src.rag.context_builder import build_context
from src.rag.retrieval_service import DefaultRetrievalService
from src.validation.fidelity_checker import DefaultValidationService

# Vectorstore singleton en memoria (modo mock; ChromaDB real en el futuro)
_VECTORSTORE = None


def _get_vectorstore():
    global _VECTORSTORE
    if _VECTORSTORE is None:
        from src.vectorstore.memory import InMemoryVectorStore

        _VECTORSTORE = InMemoryVectorStore()
    return _VECTORSTORE


class PipelineOrchestrator:
    """Flujo CU-001 / CU-002: /ingest (persistir doc + cargar vectorstore)
    y /adapt (recuperar, generar, validar, ensamblar, persistir en OCI)."""

    def __init__(self, storage_client=None):
        self._storage = storage_client
        self.generation = GenerationOrchestrator()
        self.validation = DefaultValidationService()
        self.retrieval = DefaultRetrievalService(store=_get_vectorstore())

    def _storage_client(self):
        if self._storage is None:
            settings = get_settings()
            if settings.OCI_NAMESPACE and settings.OCI_BUCKET_NAME:
                from src.storage.oci_client import OCIStorageClient

                self._storage = OCIStorageClient()
            else:
                from src.storage.mock_client import MockStorageClient

                self._storage = MockStorageClient()
        return self._storage

    # ── /ingest ─────────────────────────────────────────────────────
    def register_document(self, result) -> None:
        """Persiste el texto crudo en SQLite y carga los chunks + embeddings
        en el vectorstore (en modo mock, sin red)."""

        from src.embeddings.factory import get_embedding_provider

        db.save_document(result.document_id, result.filename, result.file_type, result.raw_text)

        store = _get_vectorstore()
        chunks = chunk_text(result.raw_text, result.document_id, result.pages)
        embedder = get_embedding_provider()
        vectors = embedder.embed_documents([c.text for c in chunks])
        store.add(
            result.document_id,
            [c.id for c in chunks],
            vectors,
            [{"page": c.page, "section": c.section} for c in chunks],
            [c.text for c in chunks],
        )

    # ── /adapt ──────────────────────────────────────────────────────
    def run_adaptation(self, request: AdaptRequest, job_id: str = "") -> NuevaMenteOutput:
        """Ejecuta el pipeline completo y devuelve el `NuevaMenteOutput`.

        Lanza:
            DocumentNotFoundError: si `request.document_id` no existe.
            NoContextError: si el retrieval no encuentra contexto suficiente
                (se traduce a `status=NO_CONTEXT`, no se propaga como 500).
        """
        doc = db.get_document(request.document_id)
        if doc is None:
            raise DocumentNotFoundError(f"document_id {request.document_id!r} no existe")

        matches = self.retrieval.retrieve(
            request.document_id,
            request.perfil,
            nicho=request.nicho,
            tema=doc["filename"],
        )
        try:
            contexto = build_context(matches)
        except NoContextError:
            return assemble_output(
                doc_id=request.document_id,
                perfil=request.perfil,
                formato=request.formato,
                nivel_detalle=request.nivel_detalle,
                nicho=request.nicho,
                contenido=None,
                fidelidad=self.validation.validate("", ""),
            )

        contenido = self.generation.generate_content(
            AdaptationRequest(
                document_id=request.document_id,
                perfil=request.perfil,
                formato=request.formato,
                nicho=request.nicho,
                nivel_detalle=request.nivel_detalle,
            ),
            contexto,
        )
        fidelidad = self.validation.validate(contenido.cuerpo, contexto)
        items = build_contexto_items(contexto, request.formato, request.perfil)

        output = assemble_output(
            doc_id=request.document_id,
            perfil=request.perfil,
            formato=request.formato,
            nivel_detalle=request.nivel_detalle,
            nicho=request.nicho,
            contenido=contenido,
            fidelidad=fidelidad,
            sources=[Source(chunk_id=m.chunk_id, page=m.page) for m in matches],
            items=items,
        )
        output.almacenamiento_oci = self._persistir_resultado(request, output, job_id="")
        return output

    def _persistir_resultado(
        self,
        request: AdaptRequest,
        output: NuevaMenteOutput,
        job_id: str,
    ) -> AlmacenamientoOCI:
        """Sube el JSON final a OCI (OCI-003) y verifica (OCI-005). Si la
        persistencia falla, degrada a PARTIAL sin propagar 500."""
        from src.storage.base import StorageClient
        from src.storage.upload import upload_result_json

        client: StorageClient = self._storage_client()
        try:
            payload = output.model_dump_json().encode("utf-8")
            result = upload_result_json(request.document_id, job_id, payload, client)
            ok = client.object_exists(result.object_name)
            if not ok:
                raise StorageError(f"verificación post-upload falló para {result.object_name}")
        except Exception:
            return AlmacenamientoOCI(
                bucket="", object_name_json=None,
                uploaded_at=None,
            )
        return AlmacenamientoOCI(
            bucket=result.bucket,
            object_name_json=result.object_name,
            uploaded_at=result.uploaded_at,
        )