# Trazabilidad — Plan Técnico → Arquitectura → Contrato → Backlog → Implementación futura → Criterio de aceptación

Cada fila es rastreable hasta una fuente concreta del Plan Técnico o del
Backlog (`PLAN.pdf` / `LISTbacklog.pdf`). Formato de la cadena exigida por
el encargo:

```
Technical Plan → Architecture Component → Contract → Backlog Item → Future Implementation → Acceptance Criteria
```

## Matriz completa

| Technical Plan (Requisito) | Architecture Component | Contract (archivo) | Backlog Item(s) | Future Implementation (qué falta) | Acceptance Criteria |
| --- | --- | --- | --- | --- | --- |
| REQ-01/02/03 (RF-001..004) | COMP-01 Ingestion | `ingestion/base.py::DocumentExtractor`, `ingestion/router.py::IngestionRouter` | BE-ING-001..004, ING-005..009 | Implementar `extract()` en `pdf_extractor.py`/`md_extractor.py`/`txt_extractor.py`, `validators.py` y `router.py::ingest()` | PDF/MD/TXT se ingieren correctamente; `document_id` único y recuperable; todos los errores tienen mensaje explícito (RF-001) |
| REQ-05 (RF-005) | COMP-02 Processing | `processing/models.py::DocumentChunk`, `processing/chunking.py::chunk_text` | TASK-001, TASK-002, PROC-003..005 | Implementar `clean_text()` y `chunk_text()`; implementar validadores de `DocumentChunk` | Ningún chunk vacío; overlap configurable respetado; documento >2M chars rechazado (PROC-005) |
| REQ-06 | COMP-03 Embeddings | `embeddings/base.py::EmbeddingProvider`, `embeddings/factory.py` | BE-RAG-004, BE-RAG-005, OUT-004 | Implementar `GeminiEmbeddingProvider`, `MockEmbeddingProvider`, `get_embedding_provider()`, `embed_chunks()` | Intercambiable Gemini↔Mock por `.env`, sin tocar el resto del pipeline (RNF-005) |
| REQ-07 | COMP-04 Vector Store | `vectorstore/base.py::VectorStore` | BE-RAG-006, BE-RAG-007 | Implementar `ChromaVectorStore`, `get_chroma_client()`, `persist_chunks()` | Colección persistente en `CHROMA_PERSIST_DIR`; error controlado si no está inicializada (OUT-005) |
| REQ-08 | COMP-05 RAG/Retrieval | `rag/base.py::RetrievalService`, `rag/context_builder.py` | BE-RAG-008..011 | Implementar `similarity_search()`, `DefaultRetrievalService.retrieve()`, `build_context()` | Top-k relevante retornado para cualquier perfil/nicho; `NoContextError` si no hay contexto suficiente (regla NO_CONTEXT, RF-009) |
| REQ-09..13 | COMP-06 Generation | `generation/llm_provider.py::LLMProvider`, `generation/orchestrator.py` | GEN-001/002/004/005/006/007, BE-GEN-003a/b/c | Implementar `GeminiLLMProvider`, `MockLLMProvider`, `GenerationOrchestrator.generate_content()`, prompts reales (`generacion_v1.txt`) | Mismo documento + distinto perfil → salidas distintas; mismo documento + distinto formato → estructuras distintas; nunca se genera sin contexto (RF-009) |
| REQ-14, REQ-15 | COMP-07 Validation | `validation/base.py::ValidationService`, `validation/fidelity_checker.py` | VAL-001, BE-VAL-002a/b/c, VAL-003/004/005 | Implementar `extract_claims()`, `verify_claim()`, `aggregate_score()`, `evaluate_pedagogical_metadata()`, prompt `verificacion_v1.txt` | Score siempre en [0,1] cuando se calcula; claims no sustentados listados; nunca se afirma "0% de alucinaciones" (RF-014) |
| REQ-16 | COMP-08 Output | `output/schema.py::NuevaMenteOutput` | BE-OUT-002 (TASK-003), BE-OUT-003 | Implementar validadores de `EvaluacionCalidad`/`DocumentChunk`; implementar `assemble_output()` | Todo output del sistema valida contra `NuevaMenteOutput`; contrato congelado tras implementarse (nota de TASK-003) |
| REQ-18..20 | COMP-09 Storage | `storage/base.py::StorageClient` | OCI-001..005 | Implementar `load_oci_config()`, `OCIStorageClient`, `MockStorageClient`, `build_object_name()`, `upload_original()`, `upload_result_json()`, `verify_upload()` | Original y JSON recuperables desde OCI tras upload; naming convention `{tipo}/{doc_id}/{timestamp}_{nombre}` (DT-07) |
| REQ-17 | COMP-10 UI + COMP-11 API | `api/main.py`, `api/orchestrator.py`, `ui/app.py`, `ui/api_client.py` | FE-API-001/002, FE-UI-005, UX-001 | Implementar los 3 handlers de `main.py`, `PipelineOrchestrator.run_adaptation()`, las 5 vistas de `ui/components/`, `ui/api_client.py` | Usuario completa el vertical slice desde la UI sin usar la API directamente (CU-001) |
| REQ-21 | Demo | `docs/demo-scenarios/`, `demo.sh` | DEMO-000..003 | Seleccionar los 3 documentos de referencia (DEMO-000); completar los pasos de cada escenario | 3 escenarios reproducibles end-to-end por cualquier integrante del equipo |
| REQ-22/23 | Documentación | `README.md`, `docs/architecture.md` | DOC-001, DOC-002 | Actualizar `README.md` una vez exista implementación real (instalación, uso) | README y arquitectura permiten a un tercero levantar el proyecto |
| DT-08 | Persistencia de sesión | `db/models.py::Job`, `db/session.py` | (implícito en FE-API-002) | Implementar `create_job()`, `update_job_status()`, `get_job()` sobre SQLite | Estado de jobs consultable sin ir a OCI |
| DT-10 (diferencial) | Orquestación externa | `n8n-workflows/` | INT-004 (COULD_HAVE) | Definir `nuevamente-v1.json` — no se inicia hasta agotar todo MUST_HAVE | Webhook n8n → `/adapt` real + nodo IF con umbral DT-11 |

## Errores de dominio (`core/exceptions.py`) → dónde se usan

| Excepción | Código | Componente que la lanza (implementación futura) |
| --- | --- | --- |
| `InvalidFileError` | `INVALID_FILE` | COMP-01 (tamaño, extensión, vacío, encoding) |
| `ScannedPdfError` | `SCANNED_PDF` | COMP-01 (`pdf_extractor.py`) |
| `DocumentNotFoundError` | `DOCUMENT_NOT_FOUND` | COMP-11 (`POST /adapt` sobre `document_id` inexistente) |
| `NoContextError` | `NO_CONTEXT` | COMP-05 (`rag/context_builder.py`) |
| `LLMProviderError` | `LLM_ERROR` | COMP-06 (`generation/llm_provider.py`) |
| `StorageError` | `STORAGE_ERROR` | COMP-09 (`storage/`) |

## DAG de dependencias (Fase 11 del Plan Técnico — orden de implementación previsto)

```
TASK-001 ─┐
TASK-003 ─┼─→ TASK-002 → BE-RAG-004..011
          │                    ↓
          │            GEN-001/002 → BE-GEN-003 → VAL-001 → BE-VAL-002
          │                                                    ↓
          └──────────────────────────────────────────→ BE-OUT-003
                                                                ↓
OCI-001 → OCI-002 → OCI-003 ──────────────────────────→ OCI-005
                                                                ↓
FE-API-001 (mock) ──────────────────────────→ FE-API-002 ──→ FE-UI-005
                                                                ↓
                                                         QA-003 → DEMO-001/002/003 → DOC-001
```

Ninguna dependencia de este DAG se implementa en esta fase; se documenta
para que la implementación futura respete el orden (p. ej. no se puede
implementar `BE-GEN-003` antes que `BE-RAG-010`).
