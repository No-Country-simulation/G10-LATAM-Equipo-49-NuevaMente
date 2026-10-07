"""Tests de `validation/pedagogical_eval.py` (VAL-003, VAL-004)."""

from src.validation.pedagogical_eval import evaluate_pedagogical_metadata


def test_devuelve_claves_esperadas():
    meta = evaluate_pedagogical_metadata("concepto clave uno concepto clave dos")
    assert set(meta.keys()) == {"conceptos_clave", "prerrequisitos", "dificultad"}


def test_conceptos_clave_no_es_lista_vacia():
    meta = evaluate_pedagogical_metadata("concepto clave uno concepto clave dos")
    assert isinstance(meta["conceptos_clave"], list)
    assert len(meta["conceptos_clave"]) <= 4


def test_prerrequisitos_lista_vacia():
    meta = evaluate_pedagogical_metadata("texto cualquiera")
    assert meta["prerrequisitos"] == []


def test_dificultad_estandar():
    assert evaluate_pedagogical_metadata("x")["dificultad"] == "estandar"
