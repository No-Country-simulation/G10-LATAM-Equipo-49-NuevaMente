from _boot import *
import json
d = fresh_env()
from src.api.orchestrator import PipelineOrchestrator
from src.api.schemas import AdaptRequest
from src.rag.retrieval_service import DefaultRetrievalService
from src.db.session import get_job, get_chunks
import src.api.main as main   # handlers REALES (capa HTTP simulada)

doc = DOC_CLOUD.encode()
orc = PipelineOrchestrator()
r = orc.ingest("arquitectura_cloud.md", doc)
print(f"INGESTA: doc={r.document_id} chunks={r.chunk_count}")
chunks = get_chunks(r.document_id)
print("  secciones por chunk:", [c.id.split('-')[-1]+':'+(c.section or '-') for c in chunks][:8])

print("\n=== H-02  La consulta de retrieval NO depende de lo que pide el usuario")
PERFILES = ["Principiante / Transición de Carrera","Desarrollador Junior / Semi Senior","Líder Técnico / Arquitecto","Gestor / Ejecutivo (No Técnico)"]
combos = {}
for p in PERFILES:
    for n in ["General","Fintech","Salud"]:
        out = orc.run_adaptation(AdaptRequest(document_id=r.document_id, perfil=p, formato="Resumen Ejecutivo (TL;DR)", nicho=n))
        combos[(p,n)] = tuple(s.chunk_id.split('-')[-1] for s in out.metadatos.sources)
print("  fuentes devueltas para 4 perfiles x 3 nichos =", len(combos), "solicitudes distintas")
print("  conjuntos de fuentes DISTINTOS:", sorted(set(combos.values())))
print("  -> 'chunk 0' = el inicio del documento (la consulta es chunks[0].text[:200], orchestrator.py:208)")

svc = DefaultRetrievalService()
for tema in ["balanceador de carga y redes", "cifrado de datos y secretos", "costos y escalado automático"]:
    m = svc.retrieve(doc_id=r.document_id, perfil=PERFILES[0], nicho="General", tema=tema)
    print(f"  consulta REAL del usuario tema={tema!r:38} -> {len(m)} resultados sobre el umbral 0.25 {[round(x.score,2) for x in m]}")

print("\n=== H-06  Validación de fidelidad circular / aviso mock contado como 'afirmación no soportada'")
out = orc.run_adaptation(AdaptRequest(document_id=r.document_id, perfil=PERFILES[0], formato="Resumen Ejecutivo (TL;DR)"))
ec = out.evaluacion_calidad
print("  status:", out.status, "| fidelidad_score:", ec.fidelidad_score)
print("  claims_no_soportados:", [c[:70]+'…' for c in ec.claims_no_soportados])
print("  observaciones:", ec.observaciones)

print("\n=== H-03  NO_CONTEXT (regla de negocio) llega al cliente como HTTP 500 INTERNAL_ERROR")
d2 = fresh_env(RETRIEVAL_MIN_SCORE="0.999")
orc2 = PipelineOrchestrator(); r2 = orc2.ingest("a.md", doc)
req = AdaptRequest(document_id=r2.document_id, perfil=PERFILES[0], formato="Resumen Ejecutivo (TL;DR)")
job = orc2.request_adaptation(req); orc2.execute_job(job.job_id, req)
j = get_job(job.job_id); print("  estado del job:", j.status, "| error:", j.error)
resp = main.get_adaptation_result(job.job_id)
body = getattr(resp, "content", None) or resp.body
print("  respuesta REAL de GET /adapt/{job}: HTTP", resp.status_code, body)
