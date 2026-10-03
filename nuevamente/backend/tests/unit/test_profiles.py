"""Tests del catálogo de perfiles.

Cubre que `INTROS`/`TITULOS` estén sincronizados con el catálogo y que
`conceptos_clave` sea determinista.
"""
from src.generation.profiles import (
    FORMATOS_MVP,
    INTROS,
    PERFILES_MVP,
    TITULOS,
    conceptos_clave,
)


def test_todo_perfil_tiene_intro():
    """Cada perfil de `PERFILES_MVP` debe tener su apertura contextualizadora."""
    faltantes = [p for p in PERFILES_MVP if p not in INTROS]
    assert not faltantes, f"Perfiles sin INTROS: {faltantes}"


def test_todo_formato_tiene_titulo():
    """Cada formato de `FORMATOS_MVP` debe tener su título."""
    faltantes = [f for f in FORMATOS_MVP if f not in TITULOS]
    assert not faltantes, f"Formatos sin TITULOS: {faltantes}"


def test_intros_no_tienen_claves_sobrantes():
    """`INTROS` no debería tener perfiles que ya no existen en el catálogo."""
    sobrantes = [k for k in INTROS if k not in PERFILES_MVP]
    assert not sobrantes, f"INTROS con claves desconocidas: {sobrantes}"


def test_titulos_no_tienen_claves_sobrantes():
    """`TITULOS` no debería tener formatos que ya no existen en el catálogo."""
    sobrantes = [k for k in TITULOS if k not in FORMATOS_MVP]
    assert not sobrantes, f"TITULOS con claves desconocidas: {sobrantes}"


def test_conceptos_clave_es_determinista():
    """Mismo texto, mismos resultados."""
    texto = "El vectorstore recupera chunks por similitud coseno sobre embeddings densos."
    assert conceptos_clave(texto) == conceptos_clave(texto)


def test_conceptos_clave_excluye_stopwords():
    """Las palabras vacías no deben aparecer entre los conceptos."""
    resultado = conceptos_clave("de la el en y a los del se las por un una que con para")
    assert resultado == ["concepto"], f"Se esperaba el fallback, se obtuvo {resultado}"


def test_conceptos_clave_prioriza_frecuencia():
    """El término más repetido debe ir primero."""
    texto = "chunk chunk chunk embedding embedding vector"
    assert conceptos_clave(texto)[0] == "chunk"
