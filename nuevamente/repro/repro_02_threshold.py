from _boot import *
d = fresh_env()
from src.api.orchestrator import PipelineOrchestrator
from src.rag.retrieval_service import DefaultRetrievalService
from src.rag.context_builder import build_context
from src.core.exceptions import NoContextError
orc = PipelineOrchestrator(); r = orc.ingest("arq.md", DOC_CLOUD.encode())
svc = DefaultRetrievalService()
print("Umbral RETRIEVAL_MIN_SCORE=0.25 (default). Consultas SIN relación con el documento:")
for q in ["receta de paella valenciana con arroz y pollo", "campeonato mundial de fútbol resultados de la liga", "the quick brown fox jumps over the lazy dog", "de la y el en los las"]:
    m = svc.retrieve(doc_id=r.document_id, perfil="Principiante / Transición de Carrera", nicho="General", tema=q)
    try: build_context(m); veredicto = "ACEPTADA como contexto"
    except NoContextError: veredicto = "NO_CONTEXT"
    print(f"  {q[:52]:54} scores={[round(x.score,2) for x in m]} -> {veredicto}")
