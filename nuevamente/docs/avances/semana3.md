# Avances Semana 3 — Implementación DT-09 (Gemini) + DT-02 (ChromaDB)

**Fecha:** 2026-10-07
**Rama:** `develop`
**Commit:** `b4c13b6`
**Autor:** Equipo Backend (implementación autónoma)

---

## Resumen ejecutivo

Se cerró el bloqueante **DT-09** (proveedor LLM + embeddings Gemini) y se implementó **DT-02** (Vector Store ChromaDB embebido persistente), desbloqueando los backlog items críticos `INT-001` (mock LLM → real) e `INT-002` (mock embeddings → real).

La arquitectura ahora permite intercambiar proveedores (`mock` ↔ `gemini`) vía variable de entorno sin tocar código de pipeline (RNF-005). Los embeddings reales persisten en ChromaDB y sobreviven a reinicios del proceso.

---

## Cambios principales

### 1. Proveedor de Embeddings Gemini (DT-09)
**Archivo:** `nuevamente/backend/src/embeddings/providers/gemini.py`

- Implementación real sobre `google-genai` SDK
- Procesamiento en **lotes de 100** (límite API Gemini)
- **Reintentos con backoff exponencial** (configurable vía `LLM_MAX_RETRIES`, `LLM_TIMEOUT_SECONDS`)
- **Importación perezosa** del cliente → tests de importación CI pasan sin la dependencia cargada
- Traducción de errores a `LLMProviderError` → envuelto por `embed_chunks()` en `NuevaMenteError` (cumple OUT-004)

### 2. Factory LLM + Providers (DT-09)
**Archivos nuevos:**
- `nuevamente/backend/src/generation/factory.py` — `get_llm_provider()` con `@lru_cache`
- `nuevamente/backend/src/generation/providers/gemini.py` — `GeminiLLMProvider.generate()` con retry/backoff
- `nuevamente/backend/src/generation/providers/mock.py` — `MockLLMProvider` determinista (marcador `[MOCK-LLM]`)
- `nuevamente/backend/src/generation/providers/__init__.py`

### 3. ChromaDB Persistente (DT-02)
**Archivos:**
- `nuevamente/backend/src/vectorstore/client.py` — `get_chroma_client()` + `get_chroma_collection()` segregada por `EMBEDDING_PROVIDER` + `EMBEDDING_DIMENSIONS` (evita conflicto mock 256-dims vs Gemini 768-dims)
- `nuevamente/backend/src/vectorstore/store.py` — `ChromaVectorStore` real: `upsert`, query coseno (1-distancia), `count()` con filtro `doc_id`
- `nuevamente/backend/src/vectorstore/factory.py` — retorna `ChromaVectorStore` para `VECTORSTORE_PROVIDER=chroma`

### 4. Configuración y Validación
**`nuevamente/backend/src/core/config.py`:**
- Defaults reales: `GEMINI_MODEL=gemini-2.5-flash`, `GEMINI_EMBEDDING_MODEL=text-embedding-004`
- Nuevo campo `EMBEDDING_DIMENSIONS=768` para validar colección Chroma
- **Validador `@model_validator`**: exige `GEMINI_API_KEY` si `LLM_PROVIDER=gemini` o `EMBEDDING_PROVIDER=gemini`

**`nuevamente/.env.example`:**
- Providers por defecto en `mock` (seguros sin credenciales)
- Gemini documentado y comentado como instrucciones de activación
- Nombres unificados (`GEMINI_MODEL`, `GEMINI_EMBEDDING_MODEL`)
- `OCI_BUCKET_NAME` como ejemplo comentado (no filtra recurso real)

### 5. Dependencias
**`nuevamente/backend/requirements.txt`:**
- `google-genai>=1.0,<2.0` descomentado
- Duplicado `uvicorn` removido

**`nuevamente/backend/requirements-rag.txt` (nuevo):**
- `chromadb>=0.5,<1.0` y `oci>=2.130,<3.0` como extras opcionales
- No penalizan el CI (se instalan solo cuando `VECTORSTORE_PROVIDER=chroma` o `STORAGE_PROVIDER=oci`)

### 6. Tests (13 nuevos)
| Archivo | Tests | Cobertura |
|---|---|---|
| `test_embeddings_gemini.py` | 7 | Contrato, lotes 100, retry exitoso, retry agotado, factory |
| `test_vectorstore_chroma.py` | 6 | Add/query, filtro doc_id, count, persistencia, segregación dimensiones, upsert |

**`tests/conftest.py`**: `cache_clear()` para todos los factories (embeddings, LLM, vectorstore, chroma client/collection).

### 7. Documentación
- `docs/architecture.md` §8: DT-09 🔴 → ✅ resuelto
- `docs/TRACEABILITY.md`: REQ-06, REQ-07, REQ-09 actualizados a **IMPLEMENTADO / PARCIAL**
- `README.md`: Limitaciones actualizadas — RAG + embeddings reales funcionan; solo generación LLM es mock

---

## Verificación

```bash
cd nuevamente/backend
pip install -r requirements-dev.txt
ruff check --config pyproject.toml src tests ../ui     # ✅ All checks passed
pytest -q                                               # ✅ 202 passed
python -c "import importlib, pkgutil, src; [importlib.import_module(n) for _,n,_ in pkgutil.walk_packages(src.__path__, prefix='src.')]; print('OK')"  # ✅
```

---

## Queda pendiente (fuera de Semana 3)

| Item | Descripción | Backlog |
|---|---|---|
| `GenerationOrchestrator.generate_content()` | Prompts reales + mapeo a `ContenidoAdaptado` | BE-GEN-003, GEN-001/002/004/005 |
| LLM-juez en validación | `DefaultValidationService` usa LLM para SI/NO/PARCIAL (DT-05) | VAL-001, VAL-002, BE-VAL-002 |
| OCI Object Storage real | Probar `STORAGE_PROVIDER=oci` contra bucket real | OCI-003, OCI-005 |
| Demo scenarios | Seleccionar 3 documentos DEMO-000 y preparar escenarios | DEMO-001/002/003 |

---

## Impacto en arquitectura

```
ANTES (Semana 2):              AHORA (Semana 3):
┌─────────────────┐            ┌─────────────────┐
│ Embeddings mock │            │ Embeddings:     │
│ (256 dims, RAM) │     ──▶    │  mock (256)     │
│ VectorStore RAM │            │  gemini (768)   │◀── .env
└─────────────────┘            │ VectorStore:    │
                               │  ChromaDB       │
                               │  persistente    │
                               │  segregado      │
                               └─────────────────┘
```

El pipeline de ingesta → embeddings → vectorstore → retrieval ya funciona **end-to-end con proveedores reales**. Solo la generación final (`/adapt`) usa mock LLM, que se activará en la siguiente iteración.

---

## Nota de seguridad

El archivo `.env` en la raíz del repo (untracked) contiene un `GITHUB_TOKEN` en claro. **Recomendación:** rotar el token y mover `.env` fuera del árbol del repositorio antes de cualquier commit accidental. `SEC-001`/`SEC-002` cubren esto.