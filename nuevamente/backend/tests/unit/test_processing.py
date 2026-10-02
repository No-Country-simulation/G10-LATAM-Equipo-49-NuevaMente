"""QA-002 — processing: DocumentChunk, limpieza y chunking."""
import pytest

from src.core.config import get_settings
from src.core.exceptions import DocumentTooLargeError, InvalidFileError
from src.ingestion.models import PageText
from src.processing.chunking import chunk_text
from src.processing.cleaning import clean_pdf_pages, clean_text, prepare_document_text
from src.processing.models import DocumentChunk


def _words(prefix: str, count: int) -> str:
    return " ".join(f"{prefix}{i}" for i in range(count))


def _set_chunking(monkeypatch, size: int, overlap: int) -> None:
    monkeypatch.setenv("CHUNK_SIZE", str(size))
    monkeypatch.setenv("CHUNK_OVERLAP", str(overlap))
    get_settings.cache_clear()


# ---------------------------------------------------------------- DocumentChunk
def _chunk(**overrides) -> DocumentChunk:
    data = {
        "id": "doc_a-chunk-0",
        "doc_id": "doc_a",
        "text": "texto",
        "position": 0,
        "char_start": 0,
        "char_end": 5,
    }
    data.update(overrides)
    return DocumentChunk(**data)


def test_chunk_valid_and_serializable():
    chunk = _chunk(section="Intro", page=2)
    dumped = chunk.model_dump()
    assert dumped["id"] == "doc_a-chunk-0"
    assert dumped["section"] == "Intro"
    assert dumped["page"] == 2


def test_chunk_rejects_empty_text():
    with pytest.raises(ValueError):
        _chunk(text="   ")


@pytest.mark.parametrize("start,end", [(5, 5), (7, 3), (-1, 4)])
def test_chunk_rejects_invalid_positions(start, end):
    with pytest.raises(ValueError):
        _chunk(char_start=start, char_end=end)


# --------------------------------------------------------------------- limpieza
def test_clean_text_preserves_markdown_indentation():
    md = "- item\n    - subitem\n\n```python\nif x:\n    y = 1\n```"
    cleaned = clean_text(md)
    assert "\n    - subitem" in cleaned
    assert "\n    y = 1" in cleaned


def test_clean_text_normalizes_whitespace_and_control_chars():
    raw = "\ufeffhola    mundo \x00\x07\r\n\r\n\r\n\r\nfin   \n"
    assert clean_text(raw) == "hola mundo\n\nfin"


def test_clean_text_empty():
    assert clean_text("") == ""


def _report_pages() -> list[PageText]:
    names = ["alfa", "beta", "gamma", "delta", "epsilon"]
    return [
        PageText(
            page=i + 1,
            text=f"Informe Anual 2025\nCuerpo {name} con contenido propio\nPágina {i + 1} de 5",
        )
        for i, name in enumerate(names)
    ]


def test_clean_pdf_pages_removes_repeated_headers_and_page_numbers():
    cleaned = clean_pdf_pages(_report_pages())
    assert [p.page for p in cleaned] == [1, 2, 3, 4, 5]
    for page in cleaned:
        assert "Informe Anual" not in page.text
        assert "Página" not in page.text
        assert page.text.startswith("Cuerpo ")


def test_clean_pdf_pages_drops_pages_left_empty():
    pages = [PageText(page=1, text="Contenido"), PageText(page=2, text="  \n ")]
    assert [p.page for p in clean_pdf_pages(pages)] == [1]


def test_prepare_document_text_pdf_keeps_pages_inside_text():
    text, pages = prepare_document_text("ignorado", _report_pages())
    assert text == "\n\n".join(p.text for p in pages)
    assert all(p.text in text for p in pages)


def test_prepare_document_text_plain():
    text, pages = prepare_document_text("hola    mundo  \n\n\n\n    sangria", [])
    assert text == "hola mundo\n\n    sangria"  # la sangría inicial se conserva
    assert pages == []


def test_prepare_document_text_rejects_empty_result():
    with pytest.raises(InvalidFileError):
        prepare_document_text("\x00\x01  \n", [])


# --------------------------------------------------------------------- chunking
def test_chunk_text_empty_returns_empty_list():
    assert chunk_text("", "doc_x") == []
    assert chunk_text("  \n ", "doc_x") == []


def test_chunk_text_short_text_is_one_chunk():
    chunks = chunk_text("Texto corto.", "doc_x")
    assert len(chunks) == 1
    assert chunks[0].text == "Texto corto."
    assert (chunks[0].char_start, chunks[0].char_end) == (0, 12)
    assert chunks[0].page is None
    assert chunks[0].section is None


def test_chunk_text_long_text_has_valid_offsets_and_overlap():
    text = _words("palabra", 700)
    chunks = chunk_text(text, "doc_x")

    assert len(chunks) > 3
    for i, chunk in enumerate(chunks):
        assert chunk.text.strip()
        assert len(chunk.text) <= 800
        assert chunk.doc_id == "doc_x"
        assert chunk.position == i
        assert chunk.id == f"doc_x-chunk-{i}"
        assert text[chunk.char_start : chunk.char_end] == chunk.text
    assert [c.char_start for c in chunks] == sorted({c.char_start for c in chunks})
    assert chunks[1].char_start < chunks[0].char_end  # hay overlap
    assert chunks[-1].char_end == len(text)


def test_chunk_text_handles_repeated_text():
    text = "alfa beta gamma " * 300
    chunks = chunk_text(text, "doc_x")
    starts = [c.char_start for c in chunks]
    assert len(chunks) > 3
    assert starts == sorted(set(starts))
    for chunk in chunks:
        assert text[chunk.char_start : chunk.char_end] == chunk.text


def test_chunk_text_is_deterministic():
    text = _words("termino", 500)
    first = [c.model_dump() for c in chunk_text(text, "doc_x")]
    second = [c.model_dump() for c in chunk_text(text, "doc_x")]
    assert first == second


def test_chunk_text_assigns_markdown_sections(monkeypatch):
    _set_chunking(monkeypatch, 200, 20)
    text = f"# Intro\n\n{_words('alfa', 80)}\n\n## Detalles\n\n{_words('beta', 80)}"
    chunks = chunk_text(text, "doc_x")

    assert chunks[0].section == "Intro"
    assert chunks[-1].section == "Detalles"
    assert {c.section for c in chunks} == {"Intro", "Detalles"}


def test_chunk_text_assigns_pdf_pages(monkeypatch):
    _set_chunking(monkeypatch, 300, 50)
    page_one = PageText(page=1, text=_words("uno", 120))
    page_two = PageText(page=2, text=_words("dos", 120))
    text = f"{page_one.text}\n\n{page_two.text}"

    chunks = chunk_text(text, "doc_x", [page_one, page_two])

    assert chunks[0].page == 1
    assert chunks[-1].page == 2
    pages = [c.page for c in chunks]
    assert None not in pages
    assert pages == sorted(pages)


def test_chunk_text_rejects_too_large_documents(monkeypatch):
    monkeypatch.setenv("MAX_DOCUMENT_CHARS", "100")
    get_settings.cache_clear()
    with pytest.raises(DocumentTooLargeError, match="demasiado grande"):
        chunk_text("palabra " * 50, "doc_x")
