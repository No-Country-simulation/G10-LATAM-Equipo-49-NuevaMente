"""Tests unitarios de chunking (QA-002, TEST-UNIT-001).

Criterio clave: un texto de 5000 caracteres nunca produce chunks con
`text` vacío; el límite `MAX_DOCUMENT_CHARS` eleva `NuevaMenteError`.
"""
import pytest
from src.core.config import get_settings
from src.core.exceptions import NuevaMenteError
from src.processing.chunking import chunk_text


def test_chunk_vacio_no_genera_chunks():
    assert chunk_text("   \n  ", doc_id="d1") == []


def test_texto_corto_un_solo_chunk():
    chunks = chunk_text("Hola mundo. Esto es una prueba.", doc_id="d1")
    assert len(chunks) == 1
    assert chunks[0].text
    assert chunks[0].doc_id == "d1"


def test_texto_largo_nunca_genera_chunk_vacio():
    parrafo = "Oración número {i} de relleno. " * 400
    chunks = chunk_text(parrafo, doc_id="d1")
    assert len(chunks) > 1
    assert all(c.text.strip() for c in chunks)


def test_posiciones_validas():
    chunks = chunk_text("una oración larga. Otra oración. Y otra más para completar.", doc_id="d1")
    for c in chunks:
        assert 0 <= c.char_start < c.char_end


def test_documento_demasiado_grande_rechazado():
    settings = get_settings()
    largo = settings.MAX_DOCUMENT_CHARS + 1
    with pytest.raises(NuevaMenteError):
        chunk_text("a" * largo, doc_id="d1")