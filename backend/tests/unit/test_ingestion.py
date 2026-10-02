"""Tests de ingesta (QA-001): validadores y extractores.

Extensión inválida, tamaño excedido, PDF vacío (escaneado simulado) y
extracción MD/TXT.
"""
import pytest
from src.core.exceptions import InvalidFileError
from src.ingestion.md_extractor import extract_markdown_text
from src.ingestion.pdf_extractor import extract_pdf_text
from src.ingestion.router import IngestionRouter
from src.ingestion.txt_extractor import extract_txt_text
from src.ingestion.validators import detect_type, validate_size


# ── validators ──────────────────────────────────────────────────────
def test_detect_type_pdf_md_txt():
    assert detect_type("doc.pdf") == "pdf"
    assert detect_type("doc.md") == "md"
    assert detect_type("doc.markdown") == "md"
    assert detect_type("doc.txt") == "txt"


def test_detect_type_extension_invalida():
    with pytest.raises(InvalidFileError):
        detect_type("doc.exe")


def test_validate_size_vacio():
    with pytest.raises(InvalidFileError):
        validate_size(b"")


def test_validate_size_excede_maximo():
    with pytest.raises(InvalidFileError):
        validate_size(b"a" * (11 * 1024 * 1024))


# ── extractores ─────────────────────────────────────────────────────
def test_txt_utf8_y_vacio():
    assert extract_txt_text(b"hola mundo") == "hola mundo"
    with pytest.raises(InvalidFileError):
        extract_txt_text(b"   \n")


def test_markdown_utf8_y_vacio():
    assert extract_markdown_text(b"# Titulo\n\ncontenido") == "# Titulo\n\ncontenido"
    with pytest.raises(InvalidFileError):
        extract_markdown_text(b"\n\n   ")


def test_pdf_invalido_lanza_invalid_file():
    with pytest.raises(InvalidFileError):
        extract_pdf_text(b"no es un pdf")


# ── router ──────────────────────────────────────────────────────────
def test_router_ingest_txt_genera_document_id():
    router = IngestionRouter()
    res = router.ingest("nota.txt", b"contenido de prueba")
    assert res.file_type == "txt"
    assert res.raw_text == "contenido de prueba"
    assert len(res.document_id) == 24  # os.urandom(12).hex()


def test_router_ingest_extension_invalida():
    router = IngestionRouter()
    with pytest.raises(InvalidFileError):
        router.ingest("nota.rst", b"contenido")