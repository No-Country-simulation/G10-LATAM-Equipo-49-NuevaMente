from _boot import *
import sqlite3, threading, time
d = fresh_env()
from src.api.orchestrator import PipelineOrchestrator
from src.api.schemas import AdaptRequest
import src.api.orchestrator as O
from src.core.exceptions import NuevaMenteError
from src.vectorstore.factory import get_vectorstore
from src.db.session import get_job
doc = DOC_CLOUD.encode()
P = "Principiante / Transición de Carrera"; F = "Resumen Ejecutivo (TL;DR)"

print("=== H-04  Ingesta parcial: si falla el embedding, el documento YA quedó guardado")
class DownProvider:
    def embed_documents(self, t): raise RuntimeError("503 servicio de embeddings no disponible")
    def embed_query(self, t): raise RuntimeError("503")
orig = O.get_embedding_provider; O.get_embedding_provider = lambda: DownProvider()
try:
    PipelineOrchestrator().ingest("falla.md", doc); print("  (no falló)")
except NuevaMenteError as e:
    print(f"  Cliente recibe error: {type(e).__name__} code={e.code} http={e.http_status} msg={e.message[:90]!r}")
O.get_embedding_provider = orig
con = sqlite3.connect(str(__import__('src.core.config',fromlist=['x']).get_settings().sqlite_path))
docs = con.execute("select document_id, chunk_count from documents").fetchall()
nch = con.execute("select count(*) from chunks").fetchone()[0]
import pathlib; st = pathlib.Path(__import__('src.core.config',fromlist=['x']).get_settings().resolve_path(os.environ['MOCK_STORAGE_DIR']))
print(f"  Estado resultante -> documentos en SQLite: {docs} | chunks: {nch} | originales en storage: {len(list(st.rglob('*.md')))} | vectores indexados: {get_vectorstore().count()}")
orphan = docs[0][0]
out = PipelineOrchestrator().run_adaptation(AdaptRequest(document_id=orphan, perfil=P, formato=F))
print(f"  Un cliente que conozca ese id puede adaptar el documento 'fallido': status={out.status}, fidelidad={out.evaluacion_calidad.fidelidad_score} (cae al modo mock sin error)")

print("\n=== H-05  Reinicio del proceso: SQLite persiste, el índice vectorial (memory, valor por defecto) se pierde")
d = fresh_env(); orc = PipelineOrchestrator(); r = orc.ingest("a.md", doc)
a = orc.run_adaptation(AdaptRequest(document_id=r.document_id, perfil=P, formato=F))
print(f"  antes del reinicio: vectores={get_vectorstore().count(r.document_id)} fidelidad={a.evaluacion_calidad.fidelidad_score} fuentes={len(a.metadatos.sources)}")
get_vectorstore.cache_clear()   # = reinicio del proceso con VECTORSTORE_PROVIDER=memory
b = orc.run_adaptation(AdaptRequest(document_id=r.document_id, perfil=P, formato=F))
print(f"  tras el reinicio : vectores={get_vectorstore().count(r.document_id)} status={b.status} fidelidad={b.evaluacion_calidad.fidelidad_score} fuentes={len(b.metadatos.sources)}  <- degradación SILENCIOSA, sin error ni aviso de índice perdido")

print("\n=== H-07  Condición de carrera en InMemoryVectorStore (dict mutado mientras otro hilo lo recorre)")
from src.vectorstore.memory import InMemoryVectorStore
errors = []; stop = threading.Event()
s = InMemoryVectorStore()
s.add("seed", [f"s{i}" for i in range(3000)], [[1.0]*8]*3000, [{} for _ in range(3000)], ["t"]*3000)
def writer():
    n = 0
    while not stop.is_set():
        n += 1; s.add(f"d{n}", [f"c{n}"], [[1.0]*8], [{}], ["t"])
def reader():
    t_end = time.time()+4
    while time.time() < t_end:
        try: s.query([1.0]*8, 5)
        except Exception as e: errors.append(type(e).__name__+": "+str(e)); 
ws = [threading.Thread(target=writer) for _ in range(2)]; rs = [threading.Thread(target=reader) for _ in range(2)]
[t.start() for t in ws+rs]; [t.join() for t in rs]; stop.set(); [t.join() for t in ws]
print(f"  errores de lectura en 4 s con 2 escritores + 2 lectores: {len(errors)}  ejemplo: {errors[0] if errors else 'ninguno'}")

print("\n=== H-08  add() con longitudes distintas descarta chunks en silencio (zip sin strict)")
m = InMemoryVectorStore(); m.add("d", ["a","b","c"], [[1.0],[1.0]], [{},{}], ["x","y","z"])
print(f"  3 chunk_ids, 2 vectores -> indexados: {m.count()} (esperado: error o 3). Sin excepción.")
