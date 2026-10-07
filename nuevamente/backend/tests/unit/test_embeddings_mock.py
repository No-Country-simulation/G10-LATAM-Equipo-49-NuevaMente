"""Tests del proveedor de embeddings en modo mock.

El foco es el determinismo (DT-05): el vector de un texto no debe depender
de qué otros textos se procesaron antes en el mismo proceso.
"""
import math

import pytest

from src.core.exceptions import NuevaMenteError
from src.embeddings.factory import get_embedding_provider
from src.embeddings.providers.mock import DIM, MockEmbeddingProvider


@pytest.fixture
def provider():
    return MockEmbeddingProvider()


# ---------------------------------------------------------------- determinismo


def test_mismo_texto_mismo_vector(provider):
    """Mismo texto, mismo vector."""
    texto = "El vectorstore recupera chunks por similitud coseno."
    assert provider.embed_query(texto) == provider.embed_query(texto)


def test_embed_documents_conserva_el_orden(provider):
    """`embed_documents` devuelve un vector por texto, en el mismo orden."""
    textos = ["primer texto", "segundo texto", "tercer texto"]
    vectores = provider.embed_documents(textos)
    assert len(vectores) == len(textos)
    assert vectores[0] == provider.embed_query("primer texto")
    assert vectores[2] == provider.embed_query("tercer texto")


def test_token_conserva_indice_sin_importar_el_orden(provider):
    """El índice de un token no depende de texts previos.

    Este es el test que fija el bug de la implementación de `OCI`: allí el
    índice se asignaba por orden de aparición y el vocabulario se vaciaba al
    llegar a `DIM`, de modo que la misma palabra caía en una dimensión
    distinta según qué se hubiera procesado antes.

    Para reproducirlo hay que provocar el vaciado *entre* las dos consultas:
    se indexa el texto objetivo, luego se fuerza el desborde del vocabulario
    (`DIM + 2` tokens nuevos) y se vuelve a consultar.
    """
    provider.embed_query("palabra objetivo")
    antes = provider.embed_query("palabra objetivo")

    provider.embed_query(" ".join(f"otro{i}" for i in range(DIM + 2)))
    despues = provider.embed_query("palabra objetivo")

    assert antes == despues


def test_embedding_de_texto_largo_va_a_otras_dimensiones(provider):
    """Un texto con muchos tokens distintos no colapsa a un vector nulo.

    Guarda contra una implementación que devuelva siempre el vector cero:
    dos consultas compararían iguales y el test anterior no detectaría nada.
    """
    vector = provider.embed_query("palabra objetivo")
    assert any(v != 0.0 for v in vector)
    assert math.isclose(math.sqrt(sum(v * v for v in vector)), 1.0, rel_tol=1e-9)


def test_embed_query_es_estable_entre_instancias(provider):
    """Dos instancias distintas producen el mismo vector (sin estado global)."""
    otro = MockEmbeddingProvider()
    texto = "coherencia de embeddings sin estado global"
    assert provider.embed_query(texto) == otro.embed_query(texto)


# ------------------------------------------------------------------- forma


def test_vector_normalizado(provider):
    """El vector tiene norma 1 (o 0 si no hubo tokens)."""
    vector = provider.embed_query("vectores normalizados para coseno")
    assert math.isclose(math.sqrt(sum(v * v for v in vector)), 1.0, rel_tol=1e-9)


def test_vector_tiene_la_dimension_declarada(provider):
    assert len(provider.embed_query("dimension")) == DIM


def test_texto_vacio_devuelve_vector_nulo(provider):
    """Sin tokens no hay vector; la norma se evita con `or 1.0`."""
    vector = provider.embed_query("   ")
    assert vector == [0.0] * DIM


def test_texto_sin_tokens_validos(provider):
    """Solo signos de puntuación: no rompe."""
    assert provider.embed_query("¿¿¿ ... !!!") == [0.0] * DIM


def test_acentos_se_normalizan(provider):
    """Mayúsculas y acentos no cambian el resultado."""
    assert provider.embed_query("Vectorstore") == provider.embed_query("vectorstore")


# ------------------------------------------------------------------ factory


def test_factory_devuelve_mock_por_defecto(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "mock")
    assert isinstance(get_embedding_provider(), MockEmbeddingProvider)


def test_factory_acepta_mayusculas(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "MOCK")
    assert isinstance(get_embedding_provider(), MockEmbeddingProvider)


def test_factory_rechaza_proveedor_desconocido(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "openai")
    with pytest.raises(NuevaMenteError, match="EMBEDDING_PROVIDER"):
        get_embedding_provider()
