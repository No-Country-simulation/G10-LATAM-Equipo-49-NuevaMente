"""Tests de `validation/claims_extractor.py` (VAL-001)."""

from src.validation.claims_extractor import extract_claims
from src.validation.models import Claim


def test_extrae_oraciones_con_contenido():
    texto = "El agua hierve a 100 grados. La temperatura ambiente es 20. OK."
    claims = extract_claims(texto)
    assert [c.text for c in claims] == [
        "El agua hierve a 100 grados.",
        "La temperatura ambiente es 20.",
    ]


def test_descarta_titulos_y_lineas_cortas():
    """Títulos cortos y líneas de plantilla no generan claims."""
    texto = "Vista previa\nGuía Práctica\nEl contenido real tiene varias palabras aquí."
    claims = extract_claims(texto)
    assert [c.text for c in claims] == ["El contenido real tiene varias palabras aquí."]


def test_trunca_en_400_caracteres():
    largo = "A " + "palabra " * 300
    claims = extract_claims(largo)
    assert len(claims[0].text) == 400


def test_texto_vacio_o_none_devuelve_lista_vacia():
    assert extract_claims("") == []
    assert extract_claims(None) == []


def test_ignora_oraciones_sin_minusculas():
    """Frases solo mayúsculas (p.ej. avisos) se descartan."""
    claims = extract_claims("ADVERTENCIA IMPORTANTE. Esto sí es un claim válido.")
    assert [c.text for c in claims] == ["Esto sí es un claim válido."]


def test_devuelve_objetos_claim():
    claims = extract_claims("Esto es una prueba válida.")
    assert all(isinstance(c, Claim) for c in claims)
