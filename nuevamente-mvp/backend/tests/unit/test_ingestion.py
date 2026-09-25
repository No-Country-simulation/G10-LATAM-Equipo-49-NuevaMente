import pytest
from src.ingestion.service import IngestionService
from src.core.exceptions import InvalidFileError, ScannedPdfError


def test_ingest_txt_ok():
    service = IngestionService()
    result = service.ingest("nota.txt", b"contenido de prueba valido")
    assert result.file_type == "txt"
    assert result.document_id.startswith("doc_")


def test_ingest_md_ok():
    service = IngestionService()
    result = service.ingest("guia.md", b"# Titulo\n\nContenido markdown")
    assert result.file_type == "md"


def test_ingest_empty_file_rejected():
    service = IngestionService()
    with pytest.raises(InvalidFileError):
        service.ingest("vacio.txt", b"")


def test_ingest_unsupported_extension_rejected():
    service = IngestionService()
    with pytest.raises(InvalidFileError):
        service.ingest("archivo.exe", b"contenido")


def test_ingest_file_too_large_rejected():
    service = IngestionService()
    big_content = b"a" * (11 * 1024 * 1024)  # 11 MB > MAX_FILE_SIZE_MB
    with pytest.raises(InvalidFileError):
        service.ingest("grande.txt", big_content)
