from _boot import *
import types, re, logging, io
d = fresh_env()
from src.core.config import get_settings

print("=== H-09  Proveedor Gemini: timeout configurado no se aplica; reintenta errores NO reintentables; sin task_type/dimensiones")
calls = {"n": 0, "client_kwargs": None, "embed_kwargs": None}
class FakeModels:
    def embed_content(self, **kw):
        calls["n"] += 1; calls["embed_kwargs"] = kw
        raise PermissionError("403 API key not valid")      # error de autenticación: NO se arregla reintentando
class FakeClient:
    def __init__(self, **kw): calls["client_kwargs"] = kw; self.models = FakeModels()
genai = types.ModuleType("google.genai"); genai.Client = FakeClient
google = types.ModuleType("google"); google.genai = genai
sys.modules["google"] = google; sys.modules["google.genai"] = genai
import time as _t; sleeps = []; _orig = _t.sleep; _t.sleep = lambda s: sleeps.append(s)
os.environ.update(LLM_TIMEOUT_SECONDS="7", LLM_MAX_RETRIES="3"); get_settings.cache_clear()
from src.embeddings.providers.gemini import GeminiEmbeddingProvider
p = GeminiEmbeddingProvider(api_key="k")
try: p.embed_documents(["x"])
except Exception as e: err = e
_t.sleep = _orig
print(f"  LLM_TIMEOUT_SECONDS=7 -> argumentos de genai.Client: {calls['client_kwargs']}  (el timeout no llega al cliente)")
print(f"  argumentos de embed_content: {sorted(calls['embed_kwargs'])}  (sin config: task_type / output_dimensionality)")
print(f"  error de AUTENTICACIÓN (403) -> intentos={calls['n']} esperas={sleeps} (reintenta {calls['n']-1} veces algo que no puede resolverse)")
print(f"  excepción final: {type(err).__name__}: {str(err)[:100]}")
from src.core.exceptions import NuevaMenteError
from src.embeddings.embed_chunks import embed_chunks
from src.processing.models import DocumentChunk
c = [DocumentChunk(id="d-chunk-0", doc_id="d", text="hola mundo", position=0, char_start=0, char_end=10)]
try: embed_chunks(c, p)
except NuevaMenteError as e: print(f"  tras embed_chunks -> {type(e).__name__} code={e.code} http={e.http_status}  (LLMProviderError/502 degradado a INTERNAL_ERROR/500)")

print("\n=== H-10  Modelos por defecto y nombre de colección")
s = get_settings()
print(f"  GEMINI_EMBEDDING_MODEL por defecto = {s.GEMINI_EMBEDDING_MODEL!r}   GEMINI_MODEL = {s.GEMINI_MODEL!r}")
from src.vectorstore.client import _collection_name
from src.embeddings.providers.mock import MockEmbeddingProvider
for prov in ("mock", "gemini"):
    os.environ.update(EMBEDDING_PROVIDER=prov, GEMINI_API_KEY="k"); get_settings.cache_clear()
    print(f"  EMBEDDING_PROVIDER={prov:6} -> colección {_collection_name(get_settings())!r}")
print(f"  longitud REAL de un vector del mock = {len(MockEmbeddingProvider().embed_query('hola'))}  (la colección 'mock' se etiqueta con 768)")
os.environ.update(EMBEDDING_PROVIDER="gemini", GEMINI_EMBEDDING_MODEL="otro-modelo-768"); get_settings.cache_clear()
print(f"  cambiar GEMINI_EMBEDDING_MODEL no cambia la colección: {_collection_name(get_settings())!r} (mezcla de espacios vectoriales incompatibles)")
os.environ.pop("GEMINI_EMBEDDING_MODEL"); os.environ["EMBEDDING_PROVIDER"]="mock"; get_settings.cache_clear()

print("\n=== H-11  Metadatos perdidos en el índice vectorial (persist_chunks)")
import inspect, src.vectorstore.store as VS
print("  ", [l.strip() for l in inspect.getsource(VS.persist_chunks).splitlines() if "metadatas =" in l][0])
print("   -> position, section, char_start/char_end no se guardan: el índice no permite reconstruir orden ni sección")

print("\n=== H-12  Inyección en logs: un nombre de archivo sin espacios con salto de línea falsifica líneas de log")
from src.core.logging import get_logger
buf = io.StringIO(); h = logging.StreamHandler(buf); h.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
lg = logging.getLogger("aud"); lg.handlers = [h]; lg.setLevel(logging.INFO); lg.propagate = False
get_logger("aud").info("pipeline_stage", filename="x.md\nERROR pipeline_stage stage=storage_upload result=ok")
print("  salida:", repr(buf.getvalue()))
print("  líneas de log generadas por UN evento:", len(buf.getvalue().strip().splitlines()))
