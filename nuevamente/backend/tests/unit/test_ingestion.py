"""QA-001 — ingesta: validadores, extractores y router (PDF/MD/TXT)."""
import re

import pytest

from src.core.config import get_settings
from src.core.exceptions import InvalidFileError, ScannedPdfError
from src.ingestion.md_extractor import extract_markdown_text
from src.ingestion.pdf_extractor import extract_pdf_text
from src.ingestion.router import IngestionRouter
from src.ingestion.txt_extractor import extract_txt_text
from src.ingestion.validators import (
    detect_type,
    display_name,
    validate_signature,
    validate_size,
)
from tests.helpers import encrypt_pdf, make_pdf


# ------------------------------------------------------------------ validadores
def test_validate_size_ok():
    validate_size(b"contenido")


def test_validate_size_empty():
    with pytest.raises(InvalidFileError, match="vacío"):
        validate_size(b"")


def test_validate_size_exceeds_limit(monkeypatch):
    monkeypatch.setenv("MAX_FILE_SIZE_MB", "1")
    get_settings.cache_clear()
    validate_size(b"x" * 1024 * 1024)
    with pytest.raises(InvalidFileError, match="1 MB"):
        validate_size(b"x" * (1024 * 1024 + 1))


@pytest.mark.parametrize(
    "filename,expected",
    [
        ("a.pdf", "pdf"),
        ("INFORME.PDF", "pdf"),
        ("notas.md", "md"),
        ("notas.markdown", "md"),
        ("texto.txt", "txt"),
        ("C:\\docs\\texto.TXT", "txt"),
    ],
)
def test_detect_type(filename, expected):
    assert detect_type(filename) == expected


@pytest.mark.parametrize("filename", ["a.docx", "sinextension", "", "   ", "archivo.exe"])
def test_detect_type_rejects_unsupported(filename):
    with pytest.raises(InvalidFileError):
        detect_type(filename)


def test_display_name_strips_paths():
    assert display_name("C:\\Users\\ana\\doc.pdf") == "doc.pdf"
    assert display_name("/tmp/x/doc.pdf") == "doc.pdf"


def test_validate_signature_pdf():
    validate_signature("pdf", make_pdf(["hola"]))
    with pytest.raises(InvalidFileError, match="PDF válido"):
        validate_signature("pdf", b"esto no es un pdf")
    validate_signature("txt", b"cualquier cosa")


# ------------------------------------------------------------- texto plano / MD
def test_txt_utf8():
    assert extract_txt_text("canción".encode()) == "canción"


def test_txt_utf8_with_bom_is_decoded_without_bom():
    assert extract_txt_text("\ufeffcanción".encode()) == "canción"


def test_txt_windows_1252_is_accepted():
    assert extract_txt_text("canción".encode("cp1252")) == "canción"


def test_txt_binary_rejected():
    with pytest.raises(InvalidFileError, match="binario"):
        extract_txt_text(b"abc\x00def")


def test_txt_undecodable_rejected():
    with pytest.raises(InvalidFileError, match="UTF-8"):
        extract_txt_text(b"\x81\x8d\x8f")


def test_txt_blank_rejected():
    with pytest.raises(InvalidFileError, match="vacío"):
        extract_txt_text(b"  \n\t ")


def test_markdown_ok_and_blank():
    assert extract_markdown_text(b"# Titulo\n\ntexto") == "# Titulo\n\ntexto"
    with pytest.raises(InvalidFileError, match="Markdown está vacío"):
        extract_markdown_text(b"\n\n  ")


# ------------------------------------------------------------------------- PDF
def test_pdf_extracts_text_per_page():
    raw, pages = extract_pdf_text(make_pdf(["Primera pagina", "Segunda pagina"]))
    assert [p.page for p in pages] == [1, 2]
    assert "Primera pagina" in pages[0].text
    assert "Segunda pagina" in pages[1].text
    assert "Primera pagina" in raw and "Segunda pagina" in raw


def test_pdf_without_text_is_scanned_error():
    with pytest.raises(ScannedPdfError, match="escaneado"):
        extract_pdf_text(make_pdf(["", ""]))


def test_pdf_corrupt_is_invalid_file():
    with pytest.raises(InvalidFileError, match="corrupto"):
        extract_pdf_text(b"%PDF-1.4\nesto esta roto")


def test_pdf_with_password_gives_clear_error():
    with pytest.raises(InvalidFileError, match="contraseña"):
        extract_pdf_text(encrypt_pdf(make_pdf(["secreto"])))


# ---------------------------------------------------------------------- router
def test_router_txt():
    result = IngestionRouter().ingest("notas.txt", "Hola mundo".encode())
    assert re.fullmatch(r"doc_[0-9a-f]{12}", result.document_id)
    assert result.file_type == "txt"
    assert result.raw_text == "Hola mundo"
    assert result.pages == []
    assert result.filename == "notas.txt"
    assert result.warnings == []


def test_router_document_ids_are_unique():
    router = IngestionRouter()
    ids = {router.ingest("a.txt", b"hola").document_id for _ in range(20)}
    assert len(ids) == 20


def test_router_pdf_warns_about_pages_without_text():
    result = IngestionRouter().ingest("C:\\x\\doc.pdf", make_pdf(["Texto real", "", "Mas texto"]))
    assert result.file_type == "pdf"
    assert result.filename == "doc.pdf"
    assert len(result.pages) == 3
    assert len(result.warnings) == 1
    assert "1 de 3" in result.warnings[0]


def test_router_rejects_unsupported_and_fake_pdf():
    router = IngestionRouter()
    with pytest.raises(InvalidFileError):
        router.ingest("a.docx", b"x")
    with pytest.raises(InvalidFileError, match="PDF válido"):
        router.ingest("falso.pdf", b"no soy un pdf")
