# Daily Sync — 2026-10-12 (actualizado 2026-10-14 con estado real)

**Equipo:** G10-LATAM-Equipo-49-NuevaMente  
**Responsable:** Pedro Orozco (@PedrOroz)  
**Roles asignados:** Backend RAG, Backend Generación, Backend Validación, Cloud/OCI

---

## 1. Resumen de lo trabajado (hasta ayer)

### 1.1 Configuración del Bucket OCI (EPIC-09)
| Tarea | Estado | Detalle |
|-------|--------|---------|
| **OCI-001** — Configurar credenciales OCI de forma segura | ✅ **Hecho** | Perfil en `~/.oci/config`, variables en `.env.example` |
| **OCI-002** — Crear cliente OCI y bucket (Always Free) | ✅ **Hecho** | Bucket `bucket-20260921-2152-nuevamente-docs-test` creado; SDK `oci>=2.130` en `requirements-oci.txt` |
| **OCI-003** — Naming convention y subida de documento original | ✅ **Hecho** | Convención `{tipo}/{doc_id}/{timestamp}_{nombre}` implementada; `upload_original` cableado en `orchestrator.ingest` |
| **OCI-005** — Subir JSON generado y verificar upload | ✅ **Hecho** | `upload_result_json` + `verify_upload` en `orchestrator._store_result` |

> **Archivos clave:** `src/storage/oci_config.py`, `src/storage/oci_client.py`, `src/storage/naming.py`, `src/storage/upload.py`, `src/storage/verify.py`, `src/storage/factory.py`

### 1.2 Configuración del Repositorio y CI/CD
| Acción | Estado |
|--------|--------|
| Fix CI workflow (`.github/workflows/ci.yml` movido a raíz, `working-directory: nuevamente/backend`) | ✅ **Hecho** (PR #8) |
| Portar contenido de demo de rama `OCI` a `develop` (perfiles, `conceptos_clave()`) | ✅ **Hecho** (PR #9) |
| Corregir contrato `LLMProvider` (faltaba en `develop`) | ✅ **Hecho** |
| Lint (ruff) + tests (115 → 122 → **229** passed) | ✅ **Verde** |

> **Decisión:** No se mergea la rama `OCI`; se portan módulos uno a uno con PRs independientes (ver `PLAN_INTEGRACION_OCI.md`).

### 1.3 Permisos y Roles para Agentes (Embeddings + Generación)
| Componente | Estado | Archivos involucrados |
|------------|--------|----------------------|
| **EmbeddingProvider** (contrato) | ✅ Definido | `src/embeddings/base.py` |
| **CohereEmbeddingProvider** | ✅ **Implementado** | `src/embeddings/providers/cohere.py` (lotes 96, retry/backoff, `input_type`) |
| **GeminiEmbeddingProvider** | ✅ Funcional | `src/embeddings/providers/gemini.py` (lotes 100, retry/backoff) |
| **MockEmbeddingProvider** | ✅ Funcional | `src/embeddings/providers/mock.py` |
| **EmbeddingFactory** (`EMBEDDING_PROVIDER=mock|gemini|cohere`) | ✅ Funcional | `src/embeddings/factory.py` |
| **LLMProvider** (contrato) | ✅ Definido | `src/generation/llm_provider.py` |
| **MockAdapter (LLM)** | ✅ Funcional | `src/generation/mock_adapter.py` |
| **Generación por perfil/formato/nicho** | 🔄 Implementado, pendiente tests LLM real | `src/generation/orchestrator.py` (stub), `src/generation/profiles.py` (catálogo) |
| **Validación fidelidad (claims + score)** | 🔄 En progreso | `src/validation/claims_extractor.py`, `src/validation/fidelity_checker.py` (solo heurístico, sin LLM juez) |

> **Corrección histórica (2026-10-12 → 2026-10-14):**
> - En la versión original del 12/10, la línea 38 decía `EMBEDDING_PROVIDER=mock|cohere|gemini` pero solo `mock|gemini` estaban implementados. Hoy **sí** está `cohere` implementado.
> - En la versión original, la línea 47-48 listaba `COHERE_API_KEY=` en `.env.example` pero no existía. Hoy **sí** existe en `.env.example`.

> **Variables de entorno relevantes** (`.env.example` actualizado):
> ```bash
> LLM_PROVIDER=mock           # modelo de generación AÚN NO CONFIRMADO (DT-09)
> EMBEDDING_PROVIDER=mock     # mock|gemini|cohere
> COHERE_API_KEY=             # añadido 2026-10-14
> GEMINI_API_KEY=             # legacy, mantener compatibilidad
> STORAGE_PROVIDER=mock       # cambiar a 'oci' para bucket real
> OCI_NAMESPACE=
> OCI_BUCKET_NAME=bucket-20260921-2152-nuevamente-docs-test
> ```

---

## 2. Foco de hoy (2026-10-12 → completado 2026-10-14)

### 2.1 Permisos y Roles de Agentes — Continuación
| Tarea (Backlog) | Sprint actual | Estado actual (2026-10-14) |
|-----------------|---------------|----------------------------|
| **BE-RAG-004** — Integrar embedding provider (interfaz + **Cohere**) | Sprint 3 | ✅ **Completado**: `providers/cohere.py` + `factory.py` + tests |
| **BE-RAG-005** — Generar embeddings para chunks | Sprint 3 | ✅ **Completado**: `embed_chunks.py` cableado + tests unitarios |
| **BE-RAG-006** — Crear e inicializar Vector Store (ChromaDB) | Sprint 3 | ✅ **Completado**: `VECTORSTORE_PROVIDER` + segregación por `EMBEDDING_DIMENSIONS` |
| **BE-RAG-007** — Persistir embeddings en Vector Store | Sprint 3 | ✅ **Completado**: flujo chunks → embeddings → ChromaDB + test e2e |
| **BE-RAG-008/009/010** — Retrieval + context builder + NO_CONTEXT | Sprint 3 | ✅ **Completado**: propagación `NO_CONTEXT` en `execute_job` + test |
| **VAL-001 / BE-VAL-002** — Claims + score fidelidad | Sprint 3 | 🔄 **Parcial**: claims + score heurístico listos; **pendiente LLM juez** |

> **Nota:** El modelo de generación (`LLM_PROVIDER`) **aún no está confirmado** por el equipo (DT-09 pendiente). Hoy se mantiene `mock` como default seguro; la decisión entre Gemini, Cohere u otro proveedor se tomará en la reunión de sprint. **Decisión del equipo: DT-09 queda abierto.**

> **Variables de entorno relevantes** (`.env.example` actualizado):
> ```bash
> LLM_PROVIDER=mock           # modelo de generación AÚN NO CONFIRMADO (DT-09)
> EMBEDDING_PROVIDER=mock     # mock|gemini|cohere
> COHERE_API_KEY=             # añadido 2026-10-14
> GEMINI_API_KEY=             # legacy, mantener compatibilidad
> STORAGE_PROVIDER=mock       # cambiar a 'oci' para bucket real
> OCI_NAMESPACE=
> OCI_BUCKET_NAME=bucket-20260921-2152-nuevamente-docs-test
> ```

---

## 2. Foco de hoy (2026-10-12 → completado 2026-10-14)

### 2.1 Permisos y Roles de Agentes — Continuación
| Tarea (Backlog) | Sprint actual | Estado actual (2026-10-14) |
|-----------------|---------------|----------------------------|
| **BE-RAG-004** — Integrar embedding provider (interfaz + **Cohere**) | Sprint 3 | ✅ **Completado**: `providers/cohere.py` + `factory.py` + tests |
| **BE-RAG-005** — Generar embeddings para chunks | Sprint 3 | ✅ **Completado**: `embed_chunks.py` cableado + tests unitarios |
| **BE-RAG-006** — Crear e inicializar Vector Store (ChromaDB) | Sprint 3 | ✅ **Completado**: `VECTORSTORE_PROVIDER` + segregación por `EMBEDDING_DIMENSIONS` |
| **BE-RAG-007** — Persistir embeddings en Vector Store | Sprint 3 | ✅ **Completado**: flujo chunks → embeddings → ChromaDB + test e2e |
| **BE-RAG-008/009/010** — Retrieval + context builder + NO_CONTEXT | Sprint 3 | ✅ **Completado**: propagación `NO_CONTEXT` en `execute_job` + test |
| **VAL-001 / BE-VAL-002** — Claims + score fidelidad | Sprint 3 | 🔄 **Parcial**: claims + score heurístico listos; **pendiente LLM juez** |

> **Nota:** El modelo de generación (`LLM_PROVIDER`) **aún no está confirmado** por el equipo (DT-09 pendiente). Hoy se mantiene `mock` como default seguro; la decisión entre Gemini, Cohere u otro proveedor se tomará en la reunión de sprint. **Decisión del equipo: DT-09 queda abierto.**

> **Variables de entorno relevantes** (`.env.example` actualizado):
> ```bash
> LLM_PROVIDER=mock           # modelo de generación AÚN NO CONFIRMADO (DT-09)
> EMBEDDING_PROVIDER=mock     # mock|gemini|cohere
> COHERE_API_KEY=             # añadido 2026-10-14
> GEMINI_API_KEY=             # legacy, mantener compatibilidad
> STORAGE_PROVIDER=mock       # cambiar a 'oci' para bucket real
> OCI_NAMESPACE=
> OCI_BUCKET_NAME=bucket-20260921-2152-nuevamente-docs-test
> ```

---

## 2.2 Configuración de permisos OCI (Cloud/OCI) — **COMPLETADO**
- ✅ Validar que `OCI_NAMESPACE` se resuelve correctamente (auto-descubrimiento vía `get_namespace()`).
- ✅ Probar `STORAGE_PROVIDER=oci` end-to-end: upload original → upload JSON → verificación `object_exists` (smoke test `scripts/smoke_bucket_real.py` pasa en bucket real `mx-queretaro-1`).
- ✅ Documentar en `README.md` la configuración segura sin secretos en código (sección "Almacenamiento en OCI" añadida).

### 2.3 Backlog relacionado (referencias)
| Archivo | Sección relevante |
|---------|-------------------|
| `planning/backlog/backlog.md` | EPIC-04 (líneas 59-71), EPIC-05 (72-82), EPIC-06 (83-98), EPIC-07 (99-110), EPIC-09 (123-133) |
| `planning/backlog/plan_tecnico.md` | DT-07 (naming), DT-09 (Gemini pendiente), RNF-001/004/005 |
| `planning/avances/semana2/PLAN_INTEGRACION_OCI.md` | Pasos 1-5 (porte embeddings → vectorstore → RAG → validación → generación) |
| `planning/backlog/trazabilidad.md` | Matriz requisito ↔ tarea ↔ test (para validar cobertura) |
| `planning/avances/semana4/PERMISOS_IAM_BUCKET.md` | **Nuevo**: Roles IAM, políticas, smoke test, smoke bucket real |

---

## 3. Próximos pasos inmediatos (post-hoy → actualizado 2026-10-14)

1. ✅ **Mergear PR #8 y #9** → base verde para siguientes portes.
2. ✅ **Completar Paso 1 (Embeddings Cohere)** → `providers/cohere.py` + `factory.py` + tests.
3. ✅ **Completar Paso 2 (Vectorstore)** → `InMemoryVectorStore` + factory `VECTORSTORE_PROVIDER`; segregación Chroma por `EMBEDDING_DIMENSIONS`.
4. ⏳ **Definir owner y proveedor de DT-09** (LLM de generación: **Gemini vs Cohere vs otro** — **DECISIÓN: DT-09 queda abierto**, se mantiene `mock`).
5. ⏳ **Asignar rol Orquestación/API** (hoy SIN ASIGNAR en `plan_tecnico.md:121`) para `FE-API-002` e `INT-001..003`.
6. 🔄 **Implementar LLM juez** para validación de fidelidad real (post-DT-09).

---

## 4. Bloqueantes / Riesgos activos (actualizado 2026-10-14)

| Riesgo | Impacto | Mitigación en curso |
|--------|---------|---------------------|
| **Modelo de generación no confirmado** (DT-09) | Bloqueante para generación real y validación LLM-juez | **Decidido: DT-09 queda abierto**; mock funcional como default |
| Proveedor embeddings: **Cohere implementado** | ✅ Resuelto | `providers/cohere.py` + `factory.py` + `.env.example` listos |
| CI nunca se ejecutó en `develop` | ✅ Resuelto | PR #8 verde, CI en raíz con lint + tests |
| Roles Orquestación/API y QA sin asignar | Riesgo de cuello de botella en Sprint 4 | Pendiente decisión en daily / reunión de sprint |
| `NO_CONTEXT` no se ejercita con mocks | ✅ Resuelto | Test dedicado `test_no_context_propagation.py` + propagación en `execute_job` |
| Dimensiones ChromaDB (Cohere 1024 vs mock 256 vs Gemini 768) | ✅ Resuelto | Factory `_collection_name` usa `EMBEDDING_PROVIDER` + `EMBEDDING_DIMENSIONS` |

---

## 5. Evidencias / Comandos útiles (actualizados)

```bash
# Verificar CI local
cd nuevamente/backend && ruff check --config pyproject.toml src tests ../ui
cd nuevamente/backend && pytest -q

# Probar storage mock vs oci
STORAGE_PROVIDER=mock python -m src.storage.factory
STORAGE_PROVIDER=oci  python -m src.storage.factory  # requiere ~/.oci/config y requirements-oci.txt

# Probar embeddings: mock | gemini | cohere
EMBEDDING_PROVIDER=mock python -m src.embeddings.factory
EMBEDDING_PROVIDER=gemini python -m src.embeddings.factory  # requiere GEMINI_API_KEY
EMBEDDING_PROVIDER=cohere python -m src.embeddings.factory  # requiere COHERE_API_KEY

# Ver variables cargadas
cd nuevamente/backend && python -c "from src.core.config import get_settings; s=get_settings(); print(s.STORAGE_PROVIDER, s.EMBEDDING_PROVIDER, s.LLM_PROVIDER, s.OCI_BUCKET_NAME)"

# Smoke test real bucket OCI
OCI_NAMESPACE=axkf02paerjf OCI_BUCKET_NAME=bucket-20260921-2152-nuevamente-docs-test python -m scripts.smoke_bucket_real

# Bootstrap IAM roles (idempotente, dry-run por defecto)
python -m scripts.bootstrap_iam_roles [--dry-run|--apply] [--verbose]
```