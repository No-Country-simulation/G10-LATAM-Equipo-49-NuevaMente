# Arquitectura — NuevaMente (DOC-002)

> Fuente normativa de este documento, en orden de autoridad: **Plan Técnico**
> (`NuevaMente_PlanTecnico_v2.md`) y **Backlog** (`PLAN.pdf`, `LISTbacklog.pdf`)
> definen requisitos/decisiones técnicas; **`NuevaMente-Guia-Desarrollo.md`**
> es la fuente del código real de este repositorio (autoridad Alta). Ante
> cualquier conflicto, gana esa jerarquía — nunca este resumen.

## 1. Capas (tal como están implementadas)

```
UI (Streamlit, ui/app.py)
   │ HTTP
   ▼
API (FastAPI, backend/src/api/main.py) — solo orquesta, sin lógica de IA
   │
   ▼
Orchestrator (backend/src/api/orchestrator.py)
   │
   ▼
Domain Services: ingestion, processing, rag, generation, validation, output
   │
   ▼
Infraestructura: ChromaDB, SQLite, OCI Object Storage (o mock_client.py), Gemini
```

Ver diagrama completo: [`docs/diagrams/pipeline.mmd`](diagrams/pipeline.mmd).

## 2. Principios de diseño (de la Guía de Desarrollo, autoridad Alta)

- **Inversión de dependencias en IA**: nada depende directamente de Gemini.
  Todo pasa por `LLMProvider` (`generation/llm_provider.py`) y
  `EmbeddingProvider` (`embeddings/base.py`, con `provider_gemini.py` /
  `provider_mock.py` y `embeddings/factory.py` como selector). Esto permite
  correr toda la suite de tests sin red ni API key (`LLM_PROVIDER=mock`,
  `EMBEDDING_PROVIDER=mock`).
- **`api/main.py` no tiene lógica de negocio.** Los endpoints llaman al
  `orchestrator`; el orquestador coordina el pipeline completo.
- **Trazabilidad de extremo a extremo**: `DocumentChunk` (`processing/models.py`)
  incluye `page`; el contexto que ve el LLM referencia `chunk_id`/`page`; el
  JSON de salida (`output/schema.py`) expone `sources: [{chunk_id, page}]`.
- **Regla `NO_CONTEXT`**: si el retrieval (`rag/context_builder.py`) no
  devuelve chunks relevantes, nunca se llama al LLM de generación libremente.
- **Fidelidad determinista**: el LLM-juez (`validation/fidelity_checker.py`)
  solo clasifica cada claim en `SI/NO/PARCIAL`; el score se calcula en
  Python, no lo decide el modelo.
- **Nunca se afirma "0% de alucinaciones"**: el output siempre habla de
  "fidelidad estimada" (`evaluacion_calidad.fidelity_score`).

## 3. Mapa de carpetas → responsabilidad → requisito

| Carpeta | Responsabilidad | Archivos clave | Requisitos |
| --- | --- | --- | --- |
| `backend/src/core/` | Config centralizada (pydantic-settings), logging estructurado, excepciones de dominio | `config.py`, `logging.py`, `exceptions.py` | FND-003, FND-004 |
| `backend/src/ingestion/` | Validar y extraer texto de PDF/MD/TXT | `validators.py`, `pdf_extractor.py`, `md_extractor.py`, `txt_extractor.py`, `service.py` | REQ-01..03, RF-001 |
| `backend/src/processing/` | Modelo `DocumentChunk`, limpieza, chunking con overlap y página | `models.py`, `cleaning.py`, `chunking.py` | REQ-05, PROC-003..005 |
| `backend/src/embeddings/` | `EmbeddingProvider` (interfaz + Gemini + Mock) y embebido de chunks | `base.py`, `provider_gemini.py`, `provider_mock.py`, `factory.py`, `embed_chunks.py` | REQ-06, DT-09 |
| `backend/src/vectorstore/` | ChromaDB: cliente, persistencia, búsqueda por similitud | `client.py`, `store.py`, `search.py` | REQ-07, DT-02 |
| `backend/src/rag/` | Retrieval service + construcción de contexto (regla NO_CONTEXT) | `retrieval_service.py`, `context_builder.py` | REQ-08 |
| `backend/src/generation/` | Modelos de dominio, perfiles, prompts versionados, `LLMProvider`, orquestador de generación | `models.py`, `profiles.py`, `prompts/generacion_v1.txt`, `llm_provider.py`, `orchestrator.py` | REQ-09..13, DT-09 |
| `backend/src/validation/` | Extracción de claims + verificación de fidelidad + evaluación pedagógica | `models.py`, `claims_extractor.py`, `fidelity_checker.py`, `pedagogical_eval.py` | REQ-14, REQ-15, DT-05, DT-11 |
| `backend/src/output/` | Contrato de salida `NuevaMenteOutput` (Pydantic v2) y ensamblador | `schema.py`, `assembler.py` | REQ-16, DT-06 |
| `backend/src/storage/` | Cliente OCI real y `mock_client.py` para dev/tests sin cuenta OCI | `oci_client.py`, `upload.py`, `mock_client.py` | REQ-18..20, DT-07 |
| `backend/src/db/` | Persistencia de jobs en SQLite | `models.py`, `session.py` | DT-08 |
| `backend/src/api/` | FastAPI: schemas de entrada/salida HTTP, orquestador del pipeline, endpoints | `schemas.py`, `orchestrator.py`, `main.py` | REQ-17, DT-01 |
| `ui/` | Streamlit: cliente HTTP + 5 pantallas | `api_client.py`, `app.py`, `components/*` | REQ-17, UX-001 |
| `backend/scripts/` | Automatización de DoD, verificación end-to-end del MVP y auditoría del checklist final | `check_definition_of_done.sh`, `verify_mvp.sh`, `audit_checklist.py` | FASE 17-20 del Plan Técnico |

## 4. Dónde va cada tipo de cambio nuevo

- **Nuevo formato de extracción de archivo** → `ingestion/`, nuevo
  `*_extractor.py` + registrarlo en `ingestion/service.py` (`IngestionService.ingest`).
- **Cambio en cómo se dividen los documentos** → `processing/chunking.py`.
- **Nuevo proveedor de LLM/embeddings** → implementar la interfaz de
  `embeddings/base.py` o el protocolo usado por `generation/llm_provider.py`,
  y registrarlo en `embeddings/factory.py` — sin tocar el resto del pipeline.
- **Nuevo perfil o formato pedagógico** → `generation/profiles.py` y/o
  `generation/prompts/` (versionado `*_v<n>.txt`).
- **Cambio en el contrato de salida** → `backend/src/output/schema.py`
  (`NuevaMenteOutput`, Pydantic v2). Nota de la guía: **nunca se congela a
  mitad de proyecto una vez que `TASK-003` está en `DONE`** sin revisar
  contra todos los consumidores (`api/main.py`, `ui/components/result_view.py`,
  tests de integración).
- **Cambio de infraestructura OCI** → `storage/` (mantener `mock_client.py`
  funcionando para dev/tests sin cuenta real).
- **Nueva pantalla o estado de la UI** → `ui/components/`.
- **Nuevo script de verificación/auditoría** → `backend/scripts/`.

## 5. Contrato (resumen — ver `backend/src/output/schema.py` para el detalle exacto)

Salida `NuevaMenteOutput`: `status` (`SUCCESS` | `PARTIAL` | `NO_CONTEXT` | `ERROR`),
`metadatos` (incluye `sources: [{chunk_id, page}]`), `contenido_adaptado`,
`evaluacion_calidad` (incluye `fidelity_score`, leído contra
`settings.FIDELITY_THRESHOLD = 0.90`, DT-11).

## 6. Modo mock por defecto

Con `LLM_PROVIDER=mock` y `EMBEDDING_PROVIDER=mock` (valores por defecto de
`.env.example`) todo el pipeline, la UI y la suite de tests corren sin
ninguna credencial real. Cambiar a `gemini` es solo una variable de entorno.

## 7. Lo que queda fuera del MVP

Autenticación/usuarios, app móvil, fine-tuning, múltiples proveedores LLM
simultáneos, LMS, dashboard admin, video/voz, editor avanzado, sistema
multiagente autónomo, más de 3 perfiles/formatos, multimodalidad,
interpretación de diagramas, exportaciones, quiz en tiempo real, n8n en
producción (Plan Técnico, sección 1.1).
