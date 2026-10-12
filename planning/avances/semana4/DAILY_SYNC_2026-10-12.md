# Daily Sync — 2026-10-12

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
| **OCI-003** — Naming convention y subida de documento original | 🔄 **En progreso** | Convención `{tipo}/{doc_id}/{timestamp}_{nombre}` implementada en `src/storage/naming.py` |
| **OCI-005** — Subir JSON generado y verificar upload | 🔄 **En progreso** | Cliente `OCIStorageClient` listo en `src/storage/oci_client.py`; pendiente integración real |

> **Archivos clave:** `src/storage/oci_config.py`, `src/storage/oci_client.py`, `src/storage/naming.py`, `src/storage/factory.py`

### 1.2 Configuración del Repositorio y CI/CD
| Acción | Estado |
|--------|--------|
| Fix CI workflow (`.github/workflows/ci.yml` movido a raíz, `working-directory: nuevamente/backend`) | ✅ **Hecho** (PR #8) |
| Portar contenido de demo de rama `OCI` a `develop` (perfiles, `conceptos_clave()`) | ✅ **Hecho** (PR #9) |
| Corregir contrato `LLMProvider` (faltaba en `develop`) | ✅ **Hecho** |
| Lint (ruff) + tests (115 → 122 passed) | ✅ **Verde** |

> **Decisión:** No se mergea la rama `OCI`; se portan módulos uno a uno con PRs independientes (ver `PLAN_INTEGRACION_OCI.md`).

### 1.3 Permisos y Roles para Agentes (Embeddings + Generación)
| Componente | Estado | Archivos involucrados |
|------------|--------|----------------------|
| **EmbeddingProvider** (contrato) | ✅ Definido | `src/embeddings/base.py` |
| **CohereEmbeddingProvider** (planeado) | 🔄 **Pendiente implementación** | `src/embeddings/providers/cohere.py` (por crear) |
| **GeminiEmbeddingProvider** (stub legado) | 🔄 Stub listo | `src/embeddings/providers/gemini.py` |
| **MockEmbeddingProvider** | ✅ Funcional | `src/embeddings/providers/mock.py` |
| **EmbeddingFactory** (`EMBEDDING_PROVIDER=mock|cohere|gemini`) | ✅ Funcional | `src/embeddings/factory.py` |
| **LLMProvider** (contrato) | ✅ Definido | `src/generation/llm_provider.py` |
| **MockAdapter (LLM)** | ✅ Funcional | `src/generation/mock_adapter.py` |
| **Generación por perfil/formato/nicho** | 🔄 Implementado, pendiente tests | `src/generation/orchestrator.py`, `src/generation/profiles.py` |
| **Validación fidelidad (claims + score)** | 🔄 En progreso | `src/validation/claims_extractor.py`, `src/validation/fidelity_checker.py` |

> **Variables de entorno relevantes** (`.env.example`):
> ```bash
> LLM_PROVIDER=mock           # modelo de generación AÚN NO CONFIRMADO
> EMBEDDING_PROVIDER=cohere   # Cohere para embeddings (definido en revisión equipo)
> COHERE_API_KEY=
> GEMINI_API_KEY=             # legacy, mantener compatibilidad
> STORAGE_PROVIDER=mock       # cambiar a 'oci' para bucket real
> OCI_NAMESPACE=
> OCI_BUCKET_NAME=bucket-20260921-2152-nuevamente-docs-test
> ```

---

## 2. Foco de hoy (2026-10-12)

### 2.1 Permisos y Roles de Agentes — Continuación
| Tarea (Backlog) | Sprint actual | Qué se hará hoy |
|-----------------|---------------|-----------------|
| **BE-RAG-004** — Integrar embedding provider (interfaz + **Cohere**) | Sprint 3 | Implementar `CohereEmbeddingProvider`; validar factory + migración desde stub Gemini; confirmar `EMBEDDING_PROVIDER=cohere` no rompe tests |
| **BE-RAG-005** — Generar embeddings para chunks | Sprint 3 | Conectar `embed_chunks.py` al proveedor Cohere activo; test de integración mock + real |
| **BE-RAG-006** — Crear e inicializar Vector Store (ChromaDB) | Sprint 3 | Verificar `CHROMA_PERSIST_DIR` y persistencia real; segregar colecciones por dimensión (Cohere 1024 vs mock 256) |
| **BE-RAG-007** — Persistir embeddings en Vector Store | Sprint 3 | Flujo completo: chunks → embeddings Cohere → ChromaDB |
| **BE-RAG-008/009/010** — Retrieval service + context builder | Sprint 3 | Ejercitar `NO_CONTEXT` (RF-009) con documentos sin coincidencias |
| **VAL-001 / BE-VAL-002** — Extracción claims + score fidelidad | Sprint 3 | Integrar `conceptos_clave()` (ya en PR #9) y LLM juez |

> **Nota:** El modelo de generación (`LLM_PROVIDER`) **aún no está confirmado** por el equipo (DT-09 pendiente). Hoy se mantiene `mock` como default seguro; la decisión entre Gemini, Cohere u otro proveedor se tomará en la reunión de sprint.

### 2.2 Configuración de permisos OCI (Cloud/OCI)
- Validar que `OCI_NAMESPACE` se resuelve correctamente (hoy es `None` hasta primera llamada).
- Probar `STORAGE_PROVIDER=oci` end-to-end: upload original → upload JSON → verificación `object_exists`.
- Documentar en `SEC-002` (README) la configuración segura sin secretos en código.

### 2.3 Backlog relacionado (referencias)
| Archivo | Sección relevante |
|---------|-------------------|
| `planning/backlog/backlog.md` | EPIC-04 (líneas 59-71), EPIC-05 (72-82), EPIC-06 (83-98), EPIC-07 (99-110), EPIC-09 (123-133) |
| `planning/backlog/plan_tecnico.md` | DT-07 (naming), DT-09 (Gemini pendiente), RNF-001/004/005 |
| `planning/avances/semana2/PLAN_INTEGRACION_OCI.md` | Pasos 1-5 (porte embeddings → vectorstore → RAG → validación → generación) |
| `planning/backlog/trazabilidad.md` | Matriz requisito ↔ tarea ↔ test (para validar cobertura hoy) |

---

## 3. Próximos pasos inmediatos (post-hoy)

1. **Mergear PR #8 y #9** → base verde para siguientes portes.
2. **Completar Paso 1 (Embeddings Cohere)** → PR con `providers/cohere.py` (lotes, retry, backoff) + `factory.py` actualizado.
3. **Completar Paso 2 (Vectorstore)** → `InMemoryVectorStore` + factory `VECTORSTORE_PROVIDER`; segregación Chroma por `EMBEDDING_DIMENSIONS`.
4. **Definir owner y proveedor de DT-09** (LLM de generación: **Gemini vs Cohere vs otro** — bloquea demo honesta de generación y validación).
5. **Asignar rol Orquestación/API** (hoy SIN ASIGNAR en `plan_tecnico.md:121`) para `FE-API-002` e `INT-001..003`.

---

## 4. Bloqueantes / Riesgos activos

| Riesgo | Impacto | Mitigación en curso |
|--------|---------|---------------------|
| **Modelo de generación no confirmado** (DT-09) | Bloqueante para generación real y validación LLM-juez | Mock funcional; decisión **Gemini vs Cohere vs otro** pendiente en reunión de sprint |
| Proveedor embeddings: **Cohere definido**, implementación pendiente | Retrasa Paso 1 porte | Interfaz `EmbeddingProvider` lista; factory soporta múltiples; solo falta `cohere.py` |
| CI nunca se ejecutó en `develop` | Enmascaraba bugs (LLMProvider, lint) | Ya corregido; PR #8 verde |
| Roles Orquestación/API y QA sin asignar | Riesgo de cuello de botella en Sprint 4 | Decidir en daily / reunión de sprint |
| `NO_CONTEXT` no se ejercita con mocks | Falso positivo de retrieval | Test dedicado en Paso 3 (RAG) |
| Dimensiones ChromaDB (Cohere 1024 vs mock 256 vs Gemini 768) | Conflicto colecciones si no se segregan | Factory `get_chroma_collection()` ya usa `EMBEDDING_PROVIDER` + `EMBEDDING_DIMENSIONS` |

---

## 5. Evidencias / Comandos útiles

```bash
# Verificar CI local
cd nuevamente/backend && ruff check --config pyproject.toml src tests ../ui
cd nuevamente/backend && pytest -q

# Probar storage mock vs oci
STORAGE_PROVIDER=mock python -m src.storage.factory
STORAGE_PROVIDER=oci  python -m src.storage.factory  # requiere ~/.oci/config y requirements-oci.txt

# Probar embeddings: mock vs cohere
EMBEDDING_PROVIDER=mock python -m src.embeddings.factory
EMBEDDING_PROVIDER=cohere python -m src.embeddings.factory  # requiere COHERE_API_KEY

# Ver variables cargadas
cd nuevamente/backend && python -c "from src.core.config import get_settings; s=get_settings(); print(s.STORAGE_PROVIDER, s.EMBEDDING_PROVIDER, s.LLM_PROVIDER, s.OCI_BUCKET_NAME)"
```