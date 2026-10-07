"""Tests de `rag/context_builder.py` — ensamblado de contexto y regla
NO_CONTEXT (BE-RAG-010, BE-RAG-011).

La regla NO_CONTEXT es la que impide que el sistema invoque al LLM cuando no
hay contexto suficiente (RF-009). Estos tests la cubren en sus dos causas:
lista vacía y matches por debajo del umbral.
"""
import pytest

from src.core.exceptions import NoContextError
from src.rag.context_builder import build_context
from src.vectorstore.memory import InMemoryMatch


def _match(chunk_id="c1", text="texto relevante", score=0.9, page=None):
    return InMemoryMatch(chunk_id=chunk_id, text=text, score=score, page=page)


# ------------------------------------------------------------------ NO_CONTEXT


def test_lista_vacia_lanza_no_context():
    with pytest.raises(NoContextError):
        build_context([])


def test_todos_por_debajo_del_umbral_lanza_no_context():
    """Si ningún match supera `RETRIEVAL_MIN_SCORE`, corta el flujo."""
    matches = [_match(score=0.1), _match(score=0.2)]

    with pytest.raises(NoContextError):
        build_context(matches)


def test_el_mensaje_de_error_menciona_no_context():
    with pytest.raises(NoContextError, match="NO_CONTEXT"):
        build_context([])


# -------------------------------------------------------------------- contexto


def test_un_match_valido_produce_contexto_con_referencia_y_texto():
    contexto = build_context([_match(chunk_id="c7", text="el sueño profundo")])

    assert "[c7]" in contexto
    assert "el sueño profundo" in contexto


def test_referencia_incluye_la_pagina_cuando_existe():
    contexto = build_context([_match(chunk_id="c1", page=12)])

    assert "[c1 (p.12)]" in contexto


def test_referencia_omite_la_pagina_cuando_es_none():
    assert build_context([_match(chunk_id="c1", page=None)]).startswith("[c1] ")


def test_varios_matches_se_unen_con_linea_en_blanco():
    contexto = build_context(
        [_match(chunk_id="c1", text="uno"), _match(chunk_id="c2", text="dos")]
    )

    assert contexto == "[c1] uno\n\n[c2] dos"


def test_los_matches_bajo_umbral_se_descartan_aunque_haya_otros_validos():
    contexto = build_context(
        [_match(chunk_id="c_bueno", score=0.9), _match(chunk_id="c_malo", score=0.01)]
    )

    assert "c_bueno" in contexto
    assert "c_malo" not in contexto


def test_score_igual_al_umbral_se_incluye():
    """El corte es `>=`: un match justo en el umbral cuenta como contexto."""
    from src.core.config import get_settings

    assert get_settings().RETRIEVAL_MIN_SCORE == 0.25
    contexto = build_context([_match(chunk_id="c_limite", score=0.25)])

    assert "c_limite" in contexto
