from src.processing.chunking import chunk_text


def test_chunking_short_text_returns_one_chunk():
    chunks = chunk_text("Texto corto de prueba.", "doc_test")
    assert len(chunks) == 1
    assert chunks[0].doc_id == "doc_test"


def test_chunking_long_text_returns_multiple_chunks_with_overlap(sample_text):
    chunks = chunk_text(sample_text * 5, "doc_test")
    assert len(chunks) > 1
    assert all(c.text.strip() for c in chunks)  # ningún chunk vacío


def test_chunking_empty_text_returns_empty_list():
    assert chunk_text("", "doc_test") == []
    assert chunk_text("   ", "doc_test") == []


def test_chunking_assigns_page_from_pages(sample_pages):
    full_text = "\n\n".join(p["text"] for p in sample_pages)
    chunks = chunk_text(full_text, "doc_test", pages=sample_pages)
    assert any(c.page == 1 for c in chunks)
