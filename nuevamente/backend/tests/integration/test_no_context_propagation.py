"""Test de propagación de NO_CONTEXT (BE-RAG-011 / RF-009)."""
import os

import pytest
import inspect

from src.api.orchestrator import PipelineOrchestrator
from src.core.exceptions import NoContextError
from src.db.session import create_job, get_job, save_document
from src.db.models import DocumentRecord
from src.rag.retrieval_service import DefaultRetrievalService
from src.vectorstore.memory import InMemoryVectorStore
from src.embeddings.providers.mock import MockEmbeddingProvider


@pytest.fixture(autouse=True)
def mock_env():
    """Configura mock providers para tests deterministas."""
    os.environ["LLM_PROVIDER"] = "mock"
    os.environ["EMBEDDING_PROVIDER"] = "mock"
    os.environ["VECTORSTORE_PROVIDER"] = "memory"
    os.environ["STORAGE_PROVIDER"] = "mock"
    yield


def test_execute_job_sets_no_context_status_when_retrieval_empty():
    """`execute_job` marca el job como NO_CONTEXT cuando retrieval devuelve vacío."""
    os.environ["LLM_PROVIDER"] = "mock"
    os.environ["EMBEDDING_PROVIDER"] = "mock"
    os.environ["VECTORSTORE_PROVIDER"] = "memory"
    os.environ["STORAGE_PROVIDER"] = "mock"

    # Usar store en memoria vacío
    store = InMemoryVectorStore()
    embedder = MockEmbeddingProvider()

    # Crear retriever que siempre devuelve vacío
    retrieval = DefaultRetrievalService(store=store, embedder=MockEmbeddingProvider())

    orchestrator = PipelineOrchestrator()
    orchestrator.retrieval = retrieval  # Inyectar retriever vacío

    # Primero crear el documento en la BD para que no falle con DocumentNotFoundError
    from src.db.session import save_document
    from src.db.models import DocumentRecord
    from datetime import UTC, datetime

    record = DocumentRecord(
        document_id="doc_con_chunks",
        filename="test.txt",
        file_type="text/plain",
        size_bytes=100,
        page_count=1,
        char_count=100,
        chunk_count=0,
        storage_object_name=None,
        warnings=[],
        created_at=datetime.now(UTC).isoformat(),
    )
    save_document(record, [])
    # No añadimos chunks al vectorstore, así que el retrieval devolverá vacío

    from src.db.session import create_job
    from src.api.schemas import AdaptRequest

    job = create_job("doc_con_chunks")
    job_id = job.job_id

    request = AdaptRequest(
        document_id="doc_con_chunks",
        perfil="Principiante / Transición de Carrera",
        formato="Guía Práctica Paso a Paso (Tutorial)",
        nicho="General",
        nivel_detalle="estandar",
    )

    orchestrator = PipelineOrchestrator()
    orchestrator.retrieval = DefaultRetrievalService(
        store=InMemoryVectorStore(), embedder=MockEmbeddingProvider()
    )

    orchestrator.execute_job(job_id, request)

    from src.db.session import get_job
    job = get_job(job_id)
    assert job.status == "NO_CONTEXT", f"Esperaba NO_CONTEXT, got {job.status}"
    assert job.error is not None


def test_execute_job_sets_error_status_for_other_errors():
    """`execute_job` marca el job como ERROR para otros errores de dominio."""
    os.environ["LLM_PROVIDER"] = "mock"
    os.environ["EMBEDDING_PROVIDER"] = "mock"
    os.environ["VECTORSTORE_PROVIDER"] = "memory"
    os.environ["STORAGE_PROVIDER"] = "mock"

    store = InMemoryVectorStore()
    embedder = MockEmbeddingProvider()
    retrieval = DefaultRetrievalService(store=store, embedder=MockEmbeddingProvider())

    orchestrator = PipelineOrchestrator()
    orchestrator.retrieval = retrieval

    # Job para documento que no existe en BD
    from src.db.session import create_job
    job = create_job("doc_no_existe_en_bd")
    job_id = job.job_id

    from src.api.schemas import AdaptRequest
    request = AdaptRequest(
        document_id="doc_que_no_existe_en_bd",
        perfil="Principiante / Transición de Carrera",
        formato="Guía Práctica Paso a Paso (Tutorial)",
        nicho="General",
        nivel_detalle="estandar",
    )

    orchestrator = PipelineOrchestrator()
    orchestrator.retrieval = DefaultRetrievalService(
        store=InMemoryVectorStore(), embedder=MockEmbeddingProvider()
    )
    orchestrator.execute_job(job_id, request)

    from src.db.session import get_job
    job = get_job(job_id)
    assert job.status == "ERROR", f"Esperaba ERROR, got {job.status}"


def test_no_context_error_caught_before_generic_error():
    """NoContextError se captura ANTES que NuevaMenteError genérico."""
    # Este test verifica el orden de los except en execute_job
    source = inspect.getsource(PipelineOrchestrator.execute_job)
    # NoContextError debe aparecer antes que NuevaMenteError en el código
    no_context_idx = source.index("except NoContextError")
    nueva_mente_idx = source.index("except NuevaMenteError")
    assert no_context_idx < nueva_mente_idx, "NoContextError debe capturarse antes"