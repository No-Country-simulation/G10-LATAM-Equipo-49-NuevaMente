"""DT-08 — persistencia SQLite de documentos, chunks y jobs."""
import pytest

from src.db.models import DocumentRecord
from src.db.session import (
    create_job,
    get_chunks,
    get_document,
    get_job,
    save_document,
    save_job_result,
    update_job_status,
)
from src.processing.models import DocumentChunk


def _record(doc_id: str = "doc_a") -> DocumentRecord:
    return DocumentRecord(
        document_id=doc_id,
        filename="guia.pdf",
        file_type="pdf",
        size_bytes=1234,
        page_count=2,
        char_count=50,
        chunk_count=2,
        storage_object_name="originals/doc_a/x_guia.pdf",
        warnings=["1 de 2 páginas sin texto"],
        created_at="2026-01-01T00:00:00+00:00",
    )


def _chunks(doc_id: str = "doc_a") -> list[DocumentChunk]:
    return [
        DocumentChunk(
            id=f"{doc_id}-chunk-0", doc_id=doc_id, text="uno", position=0,
            section="Intro", page=1, char_start=0, char_end=3,
        ),
        DocumentChunk(
            id=f"{doc_id}-chunk-1", doc_id=doc_id, text="dos", position=1,
            char_start=5, char_end=8,
        ),
    ]


def test_document_roundtrip_with_chunks():
    save_document(_record(), _chunks())

    document = get_document("doc_a")
    assert document is not None
    assert document.filename == "guia.pdf"
    assert document.warnings == ["1 de 2 páginas sin texto"]
    assert document.storage_object_name == "originals/doc_a/x_guia.pdf"

    chunks = get_chunks("doc_a")
    assert [c.position for c in chunks] == [0, 1]
    assert chunks[0].section == "Intro" and chunks[0].page == 1
    assert chunks[1].section is None and chunks[1].page is None


def test_unknown_document_and_chunks():
    assert get_document("doc_nope") is None
    assert get_chunks("doc_nope") == []


def test_chunks_are_isolated_per_document():
    save_document(_record("doc_a"), _chunks("doc_a"))
    save_document(_record("doc_b"), _chunks("doc_b")[:1])
    assert len(get_chunks("doc_a")) == 2
    assert len(get_chunks("doc_b")) == 1


def test_save_document_is_atomic_on_duplicates():
    save_document(_record(), _chunks())
    with pytest.raises(Exception):
        save_document(_record(), _chunks())
    assert len(get_chunks("doc_a")) == 2


def test_job_lifecycle():
    job = create_job("doc_a")
    assert job.job_id.startswith("job_")
    assert job.status == "QUEUED"
    assert get_job(job.job_id).status == "QUEUED"

    update_job_status(job.job_id, "PROCESSING")
    assert get_job(job.job_id).status == "PROCESSING"

    save_job_result(job.job_id, "PARTIAL", '{"status": "PARTIAL"}', "generated/doc_a/x.json")
    done = get_job(job.job_id)
    assert done.status == "PARTIAL"
    assert done.result_json == '{"status": "PARTIAL"}'
    assert done.result_object_name == "generated/doc_a/x.json"
    assert done.error is None


def test_job_error_and_unknown_job():
    job = create_job("doc_a")
    update_job_status(job.job_id, "ERROR", "falló")
    assert get_job(job.job_id).error == "falló"
    assert get_job("job_nope") is None
