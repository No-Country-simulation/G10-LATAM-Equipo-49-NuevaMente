import uuid

from src.api.schemas import AdaptRequest
from src.embeddings.factory import get_embedding_provider
from src.generation.llm_provider import get_llm_provider
from src.rag.retrieval_service import RetrievalService
from src.rag.context_builder import build_query, build_context
from src.generation.orchestrator import GenerationService
from src.generation.models import GenerationRequest
from src.validation.fidelity_checker import validate_fidelity
from src.output.assembler import assemble_output
from src.storage.oci_client import OCIStorageClient
from src.storage.mock_client import MockOCIStorageClient
from src.storage.upload import upload_result_json
from src.db.session import update_job
from src.core.config import settings
from src.core.logging import get_logger

log = get_logger(__name__)


def _get_storage_client():
    if settings.ENVIRONMENT == "development" and settings.LLM_PROVIDER == "mock":
        return MockOCIStorageClient()
    return OCIStorageClient()


def run_adaptation_pipeline(job_id: str, request: AdaptRequest) -> None:
    update_job(job_id, "PROCESSING")

    embedding_provider = get_embedding_provider()
    llm_provider = get_llm_provider()
    retrieval_service = RetrievalService(embedding_provider)
    generation_service = GenerationService(llm_provider)

    try:
        query = build_query(request.perfil, request.formato, request.nicho, request.nivel_detalle)
        retrieved = retrieval_service.retrieve(request.document_id, query)
        context = build_context(retrieved)

        if context is None:  # regla NO_CONTEXT — nunca se llama al LLM sin contexto
            output = assemble_output(
                doc_id=request.document_id, profile=request.perfil, format_=request.formato,
                niche=request.nicho, detail_level=request.nivel_detalle,
                sources=[], content=None, fidelity=None,
                extra_observations=["No se encontró contexto relevante para este documento."],
            )
            update_job(job_id, "NO_CONTEXT")
            _persist_and_finish(job_id, request.document_id, output)
            return

        gen_request = GenerationRequest(
            context=context.text, profile=request.perfil, format=request.formato,
            niche=request.nicho, detail_level=request.nivel_detalle,
        )
        content = generation_service.generate(gen_request)
        fidelity = validate_fidelity(llm_provider, content.cuerpo, context.text)

        output = assemble_output(
            doc_id=request.document_id, profile=request.perfil, format_=request.formato,
            niche=request.nicho, detail_level=request.nivel_detalle,
            sources=context.sources, content=content, fidelity=fidelity,
        )
        _persist_and_finish(job_id, request.document_id, output)
        update_job(job_id, output.status)

    except Exception as exc:  # noqa: BLE001
        log.error("pipeline_failed", job_id=job_id, error=str(exc))
        update_job(job_id, "ERROR", error=str(exc))


def _persist_and_finish(job_id: str, document_id: str, output) -> None:
    storage = _get_storage_client()
    result = upload_result_json(storage, document_id, job_id, output.model_dump())
    output.almacenamiento_oci.object_name_json = result["object_name_json"]
    output.almacenamiento_oci.uploaded_at = result["uploaded_at"]
    update_job(job_id, output.status, result_object=result["object_name_json"])

    import json, pathlib
    results_dir = pathlib.Path("./data/results")
    results_dir.mkdir(parents=True, exist_ok=True)
    (results_dir / f"{job_id}.json").write_text(
        json.dumps(output.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8"
    )
