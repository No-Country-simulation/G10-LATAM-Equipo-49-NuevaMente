from _boot import *
import time, importlib.util
d = fresh_env()
spec = importlib.util.spec_from_file_location("helpers", str(ROOT / 'backend/tests/helpers.py')); H = importlib.util.module_from_spec(spec); spec.loader.exec_module(H)
from src.api.orchestrator import PipelineOrchestrator
orc = PipelineOrchestrator()
print("=== H-13  Coste de una ingesta de PDF grande en el hilo de la petición (sin timeout ni límite de páginas)")
for pages in (200, 800, 1600):
    text = "Párrafo de ejemplo sobre arquitectura cloud y contenedores. " * 8
    pdf = H.make_pdf([f"Pagina {i}\n{text}" for i in range(pages)])
    mb = len(pdf)/1024/1024
    t = time.perf_counter()
    try:
        r = orc.ingest(f"grande_{pages}.pdf", pdf); res = f"chunks={r.chunk_count}"
    except Exception as e: res = type(e).__name__
    print(f"  {pages:5} páginas  {mb:5.2f} MB (límite 10 MB)  -> {time.perf_counter()-t:6.1f} s  {res}")
print("\n=== H-14  Sobrecarga de abrir SQLite + executescript(schema) en CADA operación")
from src.db.session import create_job, get_job
j = create_job("doc_x")
t = time.perf_counter()
for _ in range(500): get_job(j.job_id)
print(f"  500 lecturas de get_job: {(time.perf_counter()-t)*1000/500:.2f} ms por lectura (UI hace polling cada 1 s por cliente)")
