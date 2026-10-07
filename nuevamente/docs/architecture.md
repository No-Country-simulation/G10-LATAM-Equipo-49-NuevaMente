# Arquitectura de NuevaMente — CONTRACT-ONLY (DOC-002)

> **Estado de este repositorio: arquitectura y contratos, NO implementación.**
> Todo el código bajo `backend/src/` y `ui/` está en estado CONTRACT-ONLY:
> estructuras de datos (Pydantic), interfaces (`Protocol`) y firmas de
> función con cuerpo `...`. Ningún componente ejecuta lógica de negocio,
> llama a un servicio externo ni corre un pipeline real. Ver
> `docs/AUDIT.md` para la clasificación archivo por archivo.

Fuente normativa: **Plan Técnico** (`NuevaMente_PlanTecnico_v2.md`) y
**Backlog** (`PLAN.pdf`, `LISTbacklog.pdf`). Este documento resume esas
fuentes; ante cualquier conflicto, ganan ellas.

## 1. Qué construye NuevaMente (resumen del Plan Técnico, Fase 1)

Una aplicación web que recibe documentación técnica (PDF/Markdown/TXT), la
indexa con RAG y la re-expresa como contenido educativo adaptado a un
perfil, formato pedagógico y nicho — validando que lo generado esté
anclado a la fuente (score de fidelidad) antes de entregarlo.

## 2. Arquitectura lógica (Fase 4)

```
Usuario → Interfaz web (Streamlit) → API (FastAPI, monolito)
    → Ingestion → Processing → Embeddings → Vector Store (ChromaDB)
    → RAG/Retrieval → Generation (LLM) → Validation (fidelidad)
    → Output (JSON Pydantic) → Storage (OCI Object Storage) → Interfaz web
```

Diagrama completo: [`docs/diagrams/pipeline.mmd`](diagrams/pipeline.mmd).

**Arquitectura física:** dos procesos (UI y API), pero el backend es un
**monolito** — toda la lógica de negocio vive en un único servicio FastAPI,
sin descomponerse en microservicios. ChromaDB corre embebido dentro del
mismo proceso del API (Fase 4.2).

## 3. Los 11 componentes (Fase 5) → carpeta → contrato

| Componente | Responsabilidad | Carpeta | Protocol / contrato principal |
| --- | --- | --- | --- |
| COMP-01 Ingestion | Recibir archivo, detectar tipo, extraer texto, validar tamaño | `backend/src/ingestion/` | `DocumentExtractor` (`base.py`) |
| COMP-02 Processing | Limpieza y chunking con metadata de posición/sección | `backend/src/processing/` | `DocumentChunk` (`models.py`) |
| COMP-03 Embeddings | Generar vectores por chunk vía proveedor configurable | `backend/src/embeddings/` | `EmbeddingProvider` (`base.py`) |
| COMP-04 Vector Store | Persistir embeddings + metadata, búsqueda semántica | `backend/src/vectorstore/` | `VectorStore` (`base.py`) |
| COMP-05 RAG/Retrieval | Construir query, recuperar top-k, ensamblar contexto | `backend/src/rag/` | `RetrievalService` (`base.py`) |
| COMP-06 Generation | Adaptar contenido por perfil/formato/nicho | `backend/src/generation/` | `LLMProvider` (`llm_provider.py`) |
| COMP-07 Validation | Extraer claims, contrastarlos, calcular fidelidad | `backend/src/validation/` | `ValidationService` (`base.py`) |
| COMP-08 Output | Ensamblar el JSON final según schema Pydantic formal | `backend/src/output/` | `NuevaMenteOutput` (`schema.py`) |
| COMP-09 Storage | Cliente de almacenamiento, upload/verificación | `backend/src/storage/` | `StorageClient` (`base.py`) |
| COMP-10 Interfaz web | Ejecutar todo el flujo sin usar la API directamente | `ui/` | consume la API REST del monolito |
| COMP-11 API pública | Exponer el monolito vía REST, orquestar COMP-01..09 en orden | `backend/src/api/` | ver Fase 6 / sección 4 de este documento |

Cada `Protocol` existe para que RNF-005 (mantenibilidad por capas) sea
real: se puede sustituir el proveedor de LLM/embeddings o el cliente de
almacenamiento sin tocar el resto del pipeline — siempre que la nueva
implementación cumpla el `Protocol` correspondiente.

## 4. Contrato de la API (Fase 6 — literal, ver `backend/src/api/schemas.py` y `backend/src/output/schema.py`)

| Endpoint | Request | Response éxito | Error |
| --- | --- | --- | --- |
| `POST /ingest` | `multipart/form-data { file }` | `201 IngestResponse {document_id, file_type, status}` | `400 INVALID_FILE` |
| `POST /adapt` | `AdaptRequest {document_id, perfil, formato, nicho?}` | `202 AdaptAcceptedResponse {job_id, status=PROCESSING}` | `404 DOCUMENT_NOT_FOUND` |
| `GET /adapt/{job_id}` | — | `200 NuevaMenteOutput` (o `status=NO_CONTEXT`) | `500 INTERNAL_ERROR` |
| `GET /health` | — | `200 {status: "ok"}` | — |

`NuevaMenteOutput.metadatos.sources` es `list[{chunk_id, page}]` — esto es
lo que exige RNF-006 (trazabilidad) y es la razón por la que
`DocumentChunk` (COMP-02) y `PageText` (COMP-01) llevan un campo `page`,
aunque TASK-001 del Plan Técnico no lo menciona explícitamente (ver
sección 6, "Decisiones de diseño no explicitadas").

## 5. Flujo de datos (Fase 4.3, resumido)

```
Usuario sube archivo → POST /ingest → guarda original en OCI → document_id
Usuario elige perfil/formato → POST /adapt → retrieval top-k → prompt+contexto → LLM
    → contenido generado → verificación de claims (fidelidad) → guarda JSON en OCI
    → GET /adapt/{job_id} → JSON final (contenido + score) → interfaz muestra resultado
```

## 6. Decisiones de diseño no explicitadas en el Plan Técnico (documentadas
   explícitamente, tal como exige el encargo)

- **Campo `page` en `DocumentChunk` y `PageText`:** el Plan Técnico
  (TASK-001) no lo incluye, pero el contrato de Fase 6 exige
  `sources: [{chunk_id, page}]`. Sin este campo, ese contrato no sería
  satisfacible. Se agrega como campo opcional (`page: int | None`).
- **`ingestion/base.py`, `vectorstore/base.py`, `rag/base.py`,
  `validation/base.py`, `storage/base.py`:** el Plan Técnico (Fase 7) no
  lista un archivo `base.py` para todos estos módulos, pero el encargo de
  arquitectura exige `Protocol` explícitos para `DocumentExtractor`,
  `VectorStore`, `RetrievalService`, `ValidationService` y `StorageClient`.
  Se agregan sin romper la estructura de Fase 7 (son archivos adicionales,
  no reemplazan ninguno de los listados allí).
- **`generation/models.py`, `validation/models.py`, `db/models.py`:** el
  Plan Técnico no los lista como archivos propios, pero son necesarios
  para declarar los schemas de dominio (`AdaptationRequest`, `Claim`,
  `FidelityEvaluation`, `Job`) sin mezclarlos con la lógica de
  `orchestrator.py` / `fidelity_checker.py` / `session.py`.

## 7. Lo que queda explícitamente fuera de esta fase

- Toda implementación funcional de los 11 componentes.
- Cualquier llamada real a Gemini, OCI, ChromaDB o SQLite.
- Tests ejecutables (`def test_...`) — solo existe la estrategia (`backend/tests/TESTING_STRATEGY.md`).
- Workers, background jobs funcionales, autenticación.
- Todo lo que el Plan Técnico ya marca fuera del MVP (Fase 1.1): app
  móvil, fine-tuning, multi-LLM simultáneo, LMS, dashboard admin,
  multiagente autónomo complejo, más de 3 perfiles/formatos,
  multimodalidad, exportaciones, quiz en tiempo real, n8n en producción.

## 8. Decisiones técnicas aún abiertas (heredadas del Plan Técnico, Fase 20)

- ✅ **Resuelto:** proveedor de LLM/embeddings (Gemini, DT-09) — implementado con `GeminiEmbeddingProvider`, `GeminiLLMProvider`, factory `get_llm_provider()`, y `MockLLMProvider` como fallback. Configurable vía `LLM_PROVIDER`/`EMBEDDING_PROVIDER` en `.env`.
- ⚠️ Roles Scrum de la sección 10.1 del Plan Técnico sin reconciliar
  (quién cubre Data/RAG Engineer y AI/LLM Engineer).
- 🟠 Documentos de referencia para los 3 escenarios de demo (DEMO-000)
  aún no seleccionados.

Ninguna de estas decisiones bloquea la arquitectura ni los contratos de
este repositorio — solo bloquean el inicio de la implementación funcional.
