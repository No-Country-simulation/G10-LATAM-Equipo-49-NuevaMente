"""AUD-003, 011, 012, 013, 014, 022 — proveedores de embeddings, índice vectorial y errores."""
import sys
import time
import types

import pytest

from src.core.config import get_settings
from src.core.exceptions import LLMProviderError, NuevaMenteError
from src.embeddings.embed_chunks import embed_chunks
from src.embeddings.providers.gemini import GeminiEmbeddingProvider
from src.embeddings.providers.mock import MockEmbeddingProvider
from src.processing.chunking import chunk_text
from src.processing.cleaning import clean_text
from src.processing.models import DocumentChunk
from src.vectorstore.client import _collection_name
from src.vectorstore.memory import InMemoryVectorStore
from src.vectorstore.search import similarity_search
from src.vectorstore.store import persist_chunks
from tests.audit._support import DOC_CLOUD

# Fuente: https://ai.google.dev/gemini-api/docs/deprecations (consultada el 2026-10-11).
MODELOS_DADOS_DE_BAJA = {
    "text-embedding-004": "apagado 2026-01-14",
    "gemini-embedding-001": "apagado 2026-07-14 (reemplazo: gemini-embedding-2)",
    "gemini-2.5-flash": "retiro programado 2026-06/10 (fuentes difieren; verificar)",
}


# REGRESIÓN PERMANENTE — AUD-003 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_003_los_modelos_por_defecto_no_estan_dados_de_baja():
    s = get_settings()
    en_uso = {s.GEMINI_EMBEDDING_MODEL, s.GEMINI_MODEL}
    assert en_uso.isdisjoint(MODELOS_DADOS_DE_BAJA), en_uso & set(MODELOS_DADOS_DE_BAJA)


class _Registro:
    calls = 0
    client_kwargs: dict | None = None
    embed_kwargs: dict | None = None


def _instalar_genai_falso(registro: _Registro, error: Exception) -> dict:
    class Models:
        def embed_content(self, **kwargs):
            registro.calls += 1
            registro.embed_kwargs = kwargs
            raise error

    class Client:
        def __init__(self, **kwargs):
            registro.client_kwargs = kwargs
            self.models = Models()

    genai = types.ModuleType("google.genai")
    genai.Client = Client
    google = types.ModuleType("google")
    google.genai = genai
    previos = {k: sys.modules.get(k) for k in ("google", "google.genai")}
    sys.modules.update({"google": google, "google.genai": genai})
    return previos


def _restaurar(previos: dict) -> None:
    for nombre, modulo in previos.items():
        if modulo is None:
            sys.modules.pop(nombre, None)
        else:
            sys.modules[nombre] = modulo


def _llamar_con_error(monkeypatch, error: Exception) -> _Registro:
    monkeypatch.setenv("LLM_MAX_RETRIES", "3")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "7")
    get_settings.cache_clear()
    monkeypatch.setattr(time, "sleep", lambda s: None)
    registro = _Registro()
    previos = _instalar_genai_falso(registro, error)
    try:
        with pytest.raises(LLMProviderError):
            GeminiEmbeddingProvider(api_key="k").embed_documents(["x"])
    finally:
        _restaurar(previos)
    return registro


# REGRESIÓN PERMANENTE — AUD-011a corregido el 2026-10-15 (antes xfail(strict))
def test_aud_011_un_error_de_autenticacion_no_se_reintenta(monkeypatch):
    assert _llamar_con_error(monkeypatch, PermissionError("403 API key not valid")).calls == 1


# REGRESIÓN PERMANENTE — AUD-011b corregido el 2026-10-15 (antes xfail(strict))
def test_aud_011_el_timeout_configurado_llega_al_cliente(monkeypatch):
    kwargs = _llamar_con_error(monkeypatch, TimeoutError("lento")).client_kwargs or {}
    assert {"http_options", "timeout"} & set(kwargs)


# REGRESIÓN PERMANENTE — AUD-011c corregido el 2026-10-15 (antes xfail(strict))
def test_aud_011_la_llamada_declara_task_type_y_dimensiones(monkeypatch):
    kwargs = _llamar_con_error(monkeypatch, TimeoutError("lento")).embed_kwargs or {}
    assert "config" in kwargs


# REGRESIÓN PERMANENTE — AUD-012a corregido el 2026-10-15 (antes xfail(strict))
def test_aud_012_la_coleccion_refleja_la_dimension_real_del_proveedor():
    real = len(MockEmbeddingProvider().embed_query("hola"))
    assert str(real) in _collection_name(get_settings())


# REGRESIÓN PERMANENTE — AUD-012b corregido el 2026-10-15 (antes xfail(strict))
def test_aud_012_cambiar_de_modelo_de_embeddings_cambia_la_coleccion(monkeypatch):
    monkeypatch.setenv("EMBEDDING_PROVIDER", "gemini")
    monkeypatch.setenv("GEMINI_API_KEY", "k")
    nombres = []
    for modelo in ("modelo-a", "modelo-b"):
        monkeypatch.setenv("GEMINI_EMBEDDING_MODEL", modelo)
        get_settings.cache_clear()
        nombres.append(_collection_name(get_settings()))
    assert nombres[0] != nombres[1]


class _Espia:
    metadatas: list[dict] = []

    def add(self, doc_id, chunk_ids, vectors, metadatas, documents):
        self.metadatas = metadatas


# REGRESIÓN PERMANENTE — AUD-013 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_013_el_indice_conserva_posicion_y_seccion():
    chunks = chunk_text(clean_text(DOC_CLOUD), "doc_x")
    espia = _Espia()
    persist_chunks(chunks, [[0.0]] * len(chunks), espia)
    assert all({"position", "section"} <= set(m) for m in espia.metadatas)


# REGRESIÓN PERMANENTE — AUD-014a corregido el 2026-10-15 (antes xfail(strict))
def test_aud_014_el_store_rechaza_longitudes_inconsistentes():
    with pytest.raises(Exception):
        InMemoryVectorStore().add("d", ["a", "b", "c"], [[1.0], [1.0]], [{}, {}], ["x", "y", "z"])


class _ProveedorCorto:
    def embed_documents(self, texts):
        return [[1.0, 0.0]]  # devuelve 1 vector para N textos


# REGRESIÓN PERMANENTE — AUD-014b corregido el 2026-10-15 (antes xfail(strict))
def test_aud_014_embed_chunks_valida_un_vector_por_chunk():
    chunks = [
        DocumentChunk(
            id=f"d-chunk-{i}", doc_id="d", text="texto", position=i, char_start=0, char_end=5
        )
        for i in range(3)
    ]
    with pytest.raises(NuevaMenteError):
        embed_chunks(chunks, _ProveedorCorto())


class _ProveedorConCuota:
    def embed_documents(self, texts):
        raise LLMProviderError("cuota agotada")


# REGRESIÓN PERMANENTE — AUD-022a corregido el 2026-10-15 (antes xfail(strict))
def test_aud_022_embed_chunks_conserva_el_tipo_de_error_del_proveedor():
    chunk = DocumentChunk(
        id="d-chunk-0", doc_id="d", text="hola", position=0, char_start=0, char_end=4
    )
    with pytest.raises(LLMProviderError):
        embed_chunks([chunk], _ProveedorConCuota())


class _StoreCaido:
    def query(self, vector, top_k, doc_id=None):
        raise RuntimeError("chroma no responde")


# REGRESIÓN PERMANENTE — AUD-022b corregido el 2026-10-15 (antes xfail(strict))
def test_aud_022_un_fallo_del_vector_store_no_se_reporta_como_storage_error():
    with pytest.raises(NuevaMenteError) as info:
        similarity_search([1.0], _StoreCaido(), 3)
    assert info.value.code != "STORAGE_ERROR"
