"""AUD-001, 002, 004, 007, 008, 009, 010 — pipeline RAG y consistencia de estado.

Convención: `xfail(strict=True)` = defecto CONFIRMADO en la auditoría. Mientras el defecto exista el
test "falla como se espera"; cuando se corrija, el test pasa (XPASS) y la ejecución se marca en
rojo para obligar a retirar el marcador. Los tests sin marcador son controles positivos.
"""
import sqlite3
import threading
import time

import pytest

from src.api.orchestrator import PipelineOrchestrator
from src.api.schemas import AdaptRequest
from src.core.config import get_settings
from src.core.exceptions import NoContextError, NuevaMenteError
from src.db.session import get_job
from src.rag.context_builder import build_context
from src.rag.retrieval_service import DefaultRetrievalService
from src.vectorstore.factory import get_vectorstore
from src.vectorstore.memory import InMemoryVectorStore
from tests.audit._support import DOC_CLOUD, FORMATO, PERFIL, adapt, ingest_cloud_doc


# REGRESIÓN PERMANENTE — AUD-001 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_001_el_tema_pedido_orienta_las_fuentes():
    """Dos temas distintos deben recuperar fuentes distintas (REQ-08: top-k según la solicitud)."""
    orc, doc_id = ingest_cloud_doc()
    redes = adapt(orc, doc_id, tema="balanceador de carga y redes")
    seguridad = adapt(orc, doc_id, tema="cifrado de datos y gestión de secretos")
    assert [s.chunk_id for s in redes.metadatos.sources] != [
        s.chunk_id for s in seguridad.metadatos.sources
    ]


# REGRESIÓN PERMANENTE — AUD-002 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_002_no_context_es_un_resultado_de_negocio_no_un_error(monkeypatch):
    """Si ningún chunk supera el umbral el job debe terminar en NO_CONTEXT (contrato Fase 6)."""
    monkeypatch.setenv("RETRIEVAL_MIN_SCORE", "0.999")
    get_settings.cache_clear()
    orc, doc_id = ingest_cloud_doc()
    request = AdaptRequest(document_id=doc_id, perfil=PERFIL, formato=FORMATO)
    job = orc.request_adaptation(request)
    orc.execute_job(job.job_id, request)
    assert get_job(job.job_id).status == "NO_CONTEXT"


# REGRESIÓN PERMANENTE — AUD-010 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_010_una_consulta_ajena_al_documento_no_se_acepta_como_contexto():
    orc, doc_id = ingest_cloud_doc()
    matches = DefaultRetrievalService().retrieve(
        doc_id=doc_id, perfil=PERFIL, nicho="General",
        tema="receta de paella valenciana con arroz y pollo",
    )
    with pytest.raises(NoContextError):
        build_context(matches)


class _EmbeddingsCaidos:
    def embed_documents(self, texts):
        raise RuntimeError("503 servicio de embeddings no disponible")

    def embed_query(self, text):
        raise RuntimeError("503")


# REGRESIÓN PERMANENTE — AUD-004 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_004_una_ingesta_fallida_no_deja_estado_parcial(monkeypatch):
    import src.api.orchestrator as orchestrator_module

    monkeypatch.setattr(orchestrator_module, "get_embedding_provider", lambda: _EmbeddingsCaidos())
    with pytest.raises(NuevaMenteError):
        PipelineOrchestrator().ingest("falla.md", DOC_CLOUD.encode("utf-8"))

    settings = get_settings()
    # *******************************************************************
    #  AUD-004 corregido: ahora la ingesta falla ANTES de crear cualquier
    #  efecto, así que la tabla `documents` puede no existir todavía. Su
    #  ausencia equivale a 0 documentos (antes se persistía primero y la
    #  tabla siempre existía, dejando una fila parcial).
    # *******************************************************************
    conexion = sqlite3.connect(settings.sqlite_path)
    existe_tabla = conexion.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name='documents'"
    ).fetchone()
    docs = (
        conexion.execute("SELECT COUNT(*) FROM documents").fetchone()[0] if existe_tabla else 0
    )
    conexion.close()
    originales = list(settings.resolve_path(settings.MOCK_STORAGE_DIR).rglob("*.md"))
    assert docs == 0 and originales == []


# REGRESIÓN PERMANENTE — AUD-007 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_007_un_reinicio_no_degrada_el_resultado_en_silencio():
    orc, doc_id = ingest_cloud_doc()
    get_vectorstore.cache_clear()  # equivale a reiniciar el proceso con el store en memoria
    try:
        salida = adapt(orc, doc_id)
    except NuevaMenteError:
        return  # un fallo explícito es aceptable
    avisa = "índice" in " ".join(salida.evaluacion_calidad.observaciones).lower()
    assert get_vectorstore().count(doc_id) > 0 or avisa


# REGRESIÓN PERMANENTE — AUD-008 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_008_el_store_en_memoria_es_seguro_entre_hilos():
    store = InMemoryVectorStore()
    n = 3000
    store.add("seed", [f"s{i}" for i in range(n)], [[1.0] * 8] * n, [{}] * n, ["t"] * n)
    errores: list[str] = []
    detener = threading.Event()

    def escritor():
        i = 0
        while not detener.is_set():
            i += 1
            store.add(f"d{i}", [f"c{threading.get_ident()}-{i}"], [[1.0] * 8], [{}], ["t"])

    def lector():
        limite = time.time() + 5
        while time.time() < limite and not errores:
            try:
                store.query([1.0] * 8, 5)
            except Exception as exc:
                errores.append(f"{type(exc).__name__}: {exc}")

    hilos = [threading.Thread(target=escritor) for _ in range(2)]
    lectores = [threading.Thread(target=lector) for _ in range(2)]
    for t in hilos + lectores:
        t.start()
    for t in lectores:
        t.join()
    detener.set()
    for t in hilos:
        t.join()
    assert errores == []


# REGRESIÓN PERMANENTE — AUD-009 corregido el 2026-10-15 (antes xfail(strict))
def test_aud_009_las_plantillas_no_cuentan_como_afirmaciones_no_soportadas():
    orc, doc_id = ingest_cloud_doc()
    salida = adapt(orc, doc_id)
    plantilla = [
        c
        for c in salida.evaluacion_calidad.claims_no_soportados
        if c.startswith(("#", "Nicho"))
    ]
    assert plantilla == []


# ------------------------------------------------------------ controles positivos
def test_ok_los_offsets_de_los_chunks_son_exactos():
    from src.processing.chunking import chunk_text
    from src.processing.cleaning import clean_text

    texto = clean_text(DOC_CLOUD)
    chunks = chunk_text(texto, "doc_x")
    assert len(chunks) > 3
    assert all(texto[c.char_start : c.char_end] == c.text for c in chunks)


def test_ok_el_umbral_se_aplica_en_similarity_search():
    from src.vectorstore.memory import InMemoryMatch
    from src.vectorstore.search import similarity_search

    class Store:
        def query(self, vector, top_k, doc_id=None):
            return [InMemoryMatch("a", "x", 0.10), InMemoryMatch("b", "y", 0.40)]

    assert [m.chunk_id for m in similarity_search([1.0], Store(), 5)] == ["b"]
