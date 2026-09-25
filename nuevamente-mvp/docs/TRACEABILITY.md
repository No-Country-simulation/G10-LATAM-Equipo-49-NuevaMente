# Trazabilidad — Plan Técnico ↔ Backlog ↔ Guía de Desarrollo ↔ Repositorio ↔ Demo

Jerarquía de autoridad usada para resolver conflictos entre fuentes:

| Fuente | Propósito | Autoridad |
| --- | --- | --- |
| Plan Técnico (`NuevaMente_PlanTecnico_v2.md`) | Arquitectura y decisiones técnicas | Alta |
| Backlog (`PLAN.pdf`, `LISTbacklog.pdf`) | Funcionalidades y trabajo pendiente | Alta |
| `NuevaMente-Guia-Desarrollo.md` | Código real de referencia (los 11 componentes, testing, DoD, MVP, demo, checklist) | Alta |
| `CONTRIBUTING.md` | Reglas para trabajar en el repositorio | Alta |
| GitHub (Issues/PRs) | Evolución del proyecto | Alta |
| Repositorio | Implementación real | Resultado |

Todo el código bajo `backend/src/`, `backend/tests/`, `backend/scripts/` y
`ui/` de esta línea base fue extraído **tal cual** de la Guía de Desarrollo
(secciones 3 a 20); no es un stub. La única capa añadida por fuera de la
guía es esta documentación de trazabilidad, `CONTRIBUTING.md`,
`docs/architecture.md` y `.github/workflows/ci.yml`.

## Componentes (COMP-01..COMP-11) → carpeta → verificación

| Componente | Carpeta / archivo clave | Verificado por |
| --- | --- | --- |
| COMP-01 Ingestion | `backend/src/ingestion/service.py` | `audit_checklist.py`, `tests/unit/test_ingestion.py` |
| COMP-02 Processing | `backend/src/processing/chunking.py` | `audit_checklist.py`, `tests/unit/test_chunking.py` |
| COMP-03 Embeddings | `backend/src/embeddings/factory.py` | `audit_checklist.py`, `tests/unit/test_embeddings.py` |
| COMP-04 Vector Store | `backend/src/vectorstore/store.py` | `audit_checklist.py` |
| COMP-05 RAG | `backend/src/rag/retrieval_service.py` | `audit_checklist.py` |
| COMP-06 Generation | `backend/src/generation/orchestrator.py` | `audit_checklist.py` |
| COMP-07 Validation | `backend/src/validation/fidelity_checker.py` | `audit_checklist.py`, `tests/unit/test_fidelity.py` |
| COMP-08 Output | `backend/src/output/assembler.py` | `audit_checklist.py`, `tests/unit/test_output_schema.py` |
| COMP-09 Storage | `backend/src/storage/upload.py` (+ `mock_client.py` para dev) | `audit_checklist.py` |
| COMP-10 UI | `ui/app.py` | `audit_checklist.py` |
| COMP-11 API | `backend/src/api/main.py` | `audit_checklist.py`, `tests/integration/test_pipeline_e2e.py` |

`python scripts/audit_checklist.py` (desde `backend/`) verifica automáticamente
que los 11 componentes existen, que la app importa sin errores y que
`pytest tests/ -q` está en verde — antes de dar por cerrado el checklist final
(Fase 20 del Plan Técnico).

## Matriz Requisito → User Story → Feature → Tasks → Componente

| Requisito | User Story | Tasks | Componente (archivo real) |
| --- | --- | --- | --- |
| REQ-01/02/03 | US-001 Ingesta PDF/MD/TXT | BE-ING-001..004, ING-005..009 | `ingestion/service.py`, `*_extractor.py`, `validators.py` |
| REQ-05 | US-002 Chunking | TASK-001, TASK-002, PROC-003..005 | `processing/models.py`, `processing/chunking.py` |
| REQ-06 | — Embeddings | BE-RAG-004/005, OUT-004 | `embeddings/factory.py`, `embed_chunks.py` |
| REQ-07/08 | US-003 Retrieval semántico | BE-RAG-006..011 | `vectorstore/*`, `rag/*` |
| REQ-09..13 | US-004 Adaptación pedagógica | GEN-001/002/004/005/006/007, BE-GEN-003a/b/c | `generation/*` |
| REQ-14/15 | US-005 Validación de fidelidad | VAL-001, BE-VAL-002a/b/c, VAL-003/004/005 | `validation/*` |
| REQ-16 | US-006 JSON estructurado | BE-OUT-002/003 | `output/schema.py`, `output/assembler.py` |
| REQ-18..20 | US-007 Persistencia OCI | OCI-001..005 | `storage/oci_client.py`, `storage/upload.py`, `storage/mock_client.py`, `db/*` |
| REQ-17 | US-008 Interfaz funcional | FE-API-001/002, FE-UI-005, UX-001 | `api/main.py`, `api/orchestrator.py`, `ui/*` |
| REQ-21 | US-009 Escenarios de demo | DEMO-000..003 | `demo.sh`, `docs/demo-scenarios/`, `backend/scripts/verify_mvp.sh` |
| REQ-22/23 | US-010 Documentación | DOC-001, DOC-002 | `README.md`, `docs/architecture.md` |
| — | Definition of Done operativa | Fase 17 | `backend/scripts/check_definition_of_done.sh` |
| — | MVP funcional verificable | Fase 18 | `backend/scripts/verify_mvp.sh` |
| — | Checklist final auditable | Fase 20 | `backend/scripts/audit_checklist.py` |

## Errores de dominio controlados (mapeo a `core/exceptions.py`)

| Excepción | Código | Usada en |
| --- | --- | --- |
| `InvalidFileError` | `INVALID_FILE` | ingestion (tamaño, extensión, vacío, encoding) |
| `ScannedPdfError` | `SCANNED_PDF` | `pdf_extractor.py` (PDF sin texto extraíble) |
| `DocumentNotFoundError` | `DOCUMENT_NOT_FOUND` | `api/main.py` (`/adapt` sobre `document_id` inexistente) |
| `NoContextError` | `NO_CONTEXT` | `rag/context_builder.py` (retrieval sin score suficiente) |
| `LLMProviderError` | `LLM_ERROR` | `generation/llm_provider.py` |
| `StorageError` | `STORAGE_ERROR` | `storage/` |

## Orden de verificación antes de una demo (Notas finales de la guía)

```
backend/scripts/check_definition_of_done.sh
    → pytest tests/ -v
    → backend/scripts/verify_mvp.sh
    → backend/scripts/audit_checklist.py
```

Si los cuatro pasan, el MVP está listo para presentarse (DEMO-001..003).

## Requisitos aún no cerrados por esta línea base (según la propia guía, §20)

- 🔴 Proveedor de LLM/embeddings confirmado **formalmente** por el equipo
  (el código ya soporta Gemini y Mock intercambiables sin bloquear desarrollo).
- ⚠️ Reconciliar roles Scrum de la sección 10.1 del Plan Técnico antes de
  iniciar Semana 1.
- `generation/prompts/verificacion_v1.txt` no existe como archivo propio
  todavía: el prompt de verificación vive embebido en
  `validation/fidelity_checker.py::_verify_claim`.
