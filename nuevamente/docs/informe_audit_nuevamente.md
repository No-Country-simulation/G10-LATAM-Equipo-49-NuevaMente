# Informe mejora — NuevaMente

**Fecha:** 2026-10-15
**Resultado de la verificación:** `ruff check` limpio y **290 passed** en `pytest -q`
(existentes + suite de auditoría integrada; sin `xfail`).

---

## 1. Objetivo y método

Se aplicaron las correcciones recomendadas por la auditoría  del
proyecto. Cada cambio de código lleva un **bloque de comentario fechado `2026-10-15`** enmarcado
con asteriscos y etiquetado con el ID del hallazgo (`MEJORA AUD-XXX — 2026-10-15`).

Además se:

- integró la **suite de auditoría** dentro del proyecto (`backend/tests/audit/`, `repro/`);
- **retiró el marcador `xfail(strict=True)`** de las 24 pruebas que ya pasan (convención de la
  suite: un defecto corregido deja de ser “fallo esperado” y pasa a ser regresión permanente);
- ajustó la **suite existente** allí donde el cambio de contrato la invalidaba;
- actualizó **dependencias, configuración y documentación** .

No se implementó nada que contradijera el Plan Técnico: los cambios cierran defectos y
mantienen los contratos (por ejemplo, `NO_CONTEXT` sigue siendo un resultado de negocio).

---

## 2. Resumen ejecutivo

| Hallazgo | Tema | Estado 2026-10-15 | Prueba que lo respalda |
|---|---|---|---|
| AUD-001 | La consulta de retrieval ignora el tema pedido | **Corregido** | `test_aud_001`, `test_query_*` |
| AUD-002 | `NO_CONTEXT` se devuelve como HTTP 500 | **Corregido** | `test_aud_002` (+ capa HTTP) |
| AUD-003 | Modelos Gemini por defecto dados de baja | **Corregido** | `test_aud_003` |
| AUD-004 | Ingesta no atómica (deja estado parcial) | **Corregido** | `test_aud_004` |
| AUD-005 | `reportlab` sin declarar | **Corregido** | `test_aud_005` |
| AUD-006 | `python-multipart` sin declarar | **Corregido** | `test_aud_006` |
| AUD-007 | Índice en memoria por defecto (pérdida silenciosa) | **Corregido** | `test_aud_007` |
| AUD-008 | Condición de carrera en `InMemoryVectorStore` | **Corregido** | `test_aud_008` |
| AUD-009 | Fidelidad circular/ruidosa y `FIDELITY_THRESHOLD` sin uso | **Corregido** | `test_aud_009` |
| AUD-010 | Mock de embeddings no discrimina | **Corregido** | `test_aud_010` |
| AUD-011 | Gemini embeddings: sin timeout, reintentos ciegos, sin `task_type` | **Corregido** | `test_aud_011` ×3 |
| AUD-012 | Colección inconsistente con los vectores | **Corregido** | `test_aud_012` ×2 |
| AUD-013 | El índice pierde metadatos y no había `delete` | **Corregido** | `test_aud_013` |
| AUD-014 | No se valida la correspondencia chunks↔vectores | **Corregido** | `test_aud_014` ×2 |
| AUD-015 | UI ofrece DOCX que el backend rechaza | **Corregido** | `test_aud_015` |
| AUD-016 | CI inexistente / lint sucio | **Corregido** | `test_aud_016` |
| AUD-017 | Calidad de la suite existente | Mejorada (ver §5) | — |
| AUD-018 | Jobs huérfanos tras reinicio | **Corregido** | `reconcile_stale_jobs` |
| AUD-019 | Log injection (saltos de línea) | **Corregido** | `test_aud_019` |
| AUD-020 | `assemble_output` y `generate_content` eran *stubs* | **Corregido** | suite completa |
| AUD-021 | Deriva de configuración/documentación | **Corregido** | — |
| AUD-022 | Errores de embeddings/store mal tipados | **Corregido** | `test_aud_022` ×2 |

---

## 3. Detalle de los cambios

### AUD-001 — La solicitud debe orientar la recuperación

- **Problema:** la consulta de retrieval se armaba con `perfil` + inicio del documento
  (`chunks[0].text[:200]`), de modo que el `tema` pedido no influía en las fuentes.
- **Cambio:**
  - `api/schemas.py::AdaptRequest` gana el campo opcional `tema`.
  - `rag/retrieval_service.py::DefaultRetrievalService.retrieve` construye la consulta como
    `tema + nicho` cuando hay tema; si no, `perfil + nicho`.
  - `api/orchestrator.py::PipelineOrchestrator._overview_query` resume el documento con sus
    primeros fragmentos cuando no se indica tema (antes: recorte arbitrario del inicio).
- **Unidades tocadas:** `AdaptRequest`, `DefaultRetrievalService.retrieve`,
  `PipelineOrchestrator._overview_query`, `PipelineOrchestrator.run_adaptation`.
- **Explicación e impacto:** el `perfil` describe el estilo del destinatario, no el contenido a
  recuperar; usarlo como consulta “contaminaba” la similitud. Ahora dos temas distintos producen
  fuentes distintas y el `tema` sólo aporta contenido. Impacto: calidad del RAG directamente
  gobernada por la solicitud del usuario.

### AUD-002 — `NO_CONTEXT` es resultado de negocio, no error 500

- **Problema:** al no haber contexto, `NoContextError` se propagaba y el job terminaba en
  `ERROR` (HTTP 500), incumpliendo la Fase 6.
- **Cambio:**
  - `output/assembler.py::assemble_output` deja de ser *stub*: compone el `NuevaMenteOutput` y
    decide `status` (`NO_CONTEXT` si no hay contenido; `PARTIAL` si es mock o score bajo/nulo;
    `SUCCESS` si hay contenido real con `score >= FIDELITY_THRESHOLD`).
  - `api/orchestrator.py::run_adaptation` captura `NoContextError` de `build_context` y devuelve
    el output con `status="NO_CONTEXT"` (HTTP 200).
- **Unidades tocadas:** `assemble_output`, `run_adaptation`, `execute_job`.
- **Explicación e impacto:** se usa por fin `FIDELITY_THRESHOLD` y la decisión de estado queda
  centralizada. Impacto: el cliente distingue “no hay contexto” de “fallo técnico”.

### AUD-003 — Modelos Gemini vigentes

- **Problema:** `gemini-2.5-flash` y `text-embedding-004` están dados de baja.
- **Cambio:** en `core/config.py`, por defecto `GEMINI_MODEL="gemini-3.8-flash"` y
  `GEMINI_EMBEDDING_MODEL="gemini-embedding-2"` (según la página oficial de deprecaciones,
  consultada 2026‑10).
- **Unidades tocadas:** `Settings.GEMINI_MODEL`, `Settings.GEMINI_EMBEDDING_MODEL`; `.env.example`.
- **Impacto:** `EMBEDDING_PROVIDER=gemini` / `LLM_PROVIDER=gemini` funcionan “out of the box”.

### AUD-004 — Ingesta atómica con compensación

- **Problema:** se subía el original y se persistía en SQLite **antes** de generar embeddings e
  indexar; un fallo dejaba documento + chunks + objeto sin vectores (estado parcial silencioso).
- **Cambio:**
  - `api/orchestrator.py::ingest` calcula los **embeddings primero** (sin efectos) y sólo después
    sube, persiste e indexa; ante cualquier fallo llama a `_compensate_ingest`.
  - `_compensate_ingest` borra índice, filas y objeto.
  - Nuevas primitivas: `db/session.py::delete_document`, `StorageClient.delete_object` (Protocol +
    `MockStorageClient` + `OCIStorageClient`), y `VectorStore.delete` (Protocol + memoria + chroma).
- **Unidades tocadas:** `PipelineOrchestrator.ingest`, `_compensate_ingest`, `delete_document`,
  `MockStorageClient.delete_object`, `OCIStorageClient.delete_object`, `StorageClient.delete_object`,
  `VectorStore.delete`, `InMemoryVectorStore.delete`, `ChromaVectorStore.delete`.
- **Explicación e impacto:** política “cero estado parcial”: tras un fallo, **0 filas y 0 objetos**.
  Impacto: no quedan documentos fantasma adaptables en silencio.

### AUD-005 / AUD-006 — Dependencias declaradas

- **Cambio:** `backend/requirements.txt` declara `reportlab>=4.0,<6.0` (UI) y
  `python-multipart>=0.0.18,<1.0` (FastAPI `UploadFile`).
- **Impacto:** la API y la UI arrancan en un entorno limpio; el paso de lint/test del CI instala
  todo lo necesario vía `requirements-dev.txt`.

### AUD-007 — Índice vectorial persistente y reindexado explícito

- **Problema:** por defecto `VECTORSTORE_PROVIDER="memory"`; al reiniciar, SQLite persistía pero
  los vectores no, y `/adapt` respondía contenido mock **sin avisar**.
- **Cambio:**
  - `core/config.py`: por defecto `VECTORSTORE_PROVIDER="chroma"` (`memory` reservado a tests).
  - `api/orchestrator.py::_ensure_indexed`: si el índice de un documento está vacío, se reindexa
    desde los chunks persistidos; si la reindexación falla, el error se propaga (no hay degradación
    silenciosa).
- **Unidades tocadas:** `Settings.VECTORSTORE_PROVIDER`, `_ensure_indexed`, `run_adaptation`.
- **Impacto:** el índice sobrevive a reinicios y, si se pierde, se reconstruye de forma reproducible.

### AUD-008 — Concurrencia segura en el store en memoria

- **Cambio:** `vectorstore/memory.py::InMemoryVectorStore` usa `threading.RLock` en
  `add/query/count/delete` y `query` itera sobre una copia.
- **Explicación e impacto:** los *endpoints* síncronos y las `BackgroundTasks` corren en un pool
  de hilos; antes, la mutación concurrente del diccionario producía
  `RuntimeError: dictionary changed size during iteration` (196 errores/4 s). Ahora es seguro.

### AUD-009 — Fidelidad menos circular y declarada como heurística

- **Cambio:**
  - `validation/claims_extractor.py::extract_claims`: se excluyen encabezados Markdown, líneas
    `**…**`, el rótulo `Nicho…` y el aviso `⚠️` (eran “afirmaciones no soportadas” de plantilla).
  - `validation/fidelity_checker.py::DefaultValidationService.HEURISTIC_NOTICE`: el score se
    etiqueta explícitamente como heurística (no un juez LLM) en `observaciones`.
- **Impacto:** `claims_no_soportados` deja de recoger líneas de plantilla y el número no se
  presenta como métrica con más rigor del que tiene (RF-014).

### AUD-010 — El mock de embeddings discrimina

- **Cambio:** `embeddings/providers/mock.py` normaliza acentos (NFKD) y descarta `STOPWORDS`
  (importadas de `generation.profiles`); el vector sigue siendo TF normalizado a L2 (`DIM=256`).
- **Explicación e impacto:** antes, consultas ajenas (“receta de paella…”) compartían stopwords y
  superaban el umbral 0.25, haciendo NO_CONTEXT inverificable. Ahora las consultas ajenas caen por
  debajo del umbral y se rechazan (`repro_02_threshold.py`).

### AUD-011 — Proveedor Gemini (embeddings y generación)

- **Cambio:**
  - `embeddings/providers/gemini.py`: `http_options={"api_version":"v1","timeout": timeout*1000}`,
    `config={"task_type":…, "output_dimensionality":…}`, y reintentos **solo** para 429/5xx/timeout
    (`_is_retryable`).
  - `generation/providers/gemini.py`: mismo tratamiento (timeout, `_is_retryable`, API v1) y una
    respuesta vacía ya no se devuelve como `""` en silencio, sino que falla.
- **Unidades tocadas:** `GeminiEmbeddingProvider._get_client/_is_retryable/_embed_with_retry`,
  `GeminiLLMProvider._get_client/_is_retryable/generate`.
- **Impacto:** no se bloquean hilos por timeouts, no se pierde tiempo reintentando errores de
  credenciales, y los vectores se generan con la tarea/dimensión correctas.

### AUD-012 — Nombre de colección consistente con los vectores

- **Cambio:** `vectorstore/client.py::_collection_name` → `nuevamente_{proveedor}_{modelo}_{dims_reales}`.
  En `core/config.py` se añaden `MOCK_EMBEDDING_DIMENSIONS=256`, y las propiedades
  `Settings.active_embedding_dimensions` / `active_embedding_model`.
- **Explicación e impacto:** antes el mock se indexaba en una colección rotulada `768` con vectores
  de 256, y cambiar de **modelo** de embeddings no cambiaba la colección → mezcla de espacios
  vectoriales incompatibles. Ahora no pueden compartir colección.

### AUD-013 — El índice conserva metadatos

- **Cambio:** `vectorstore/store.py::persist_chunks` guarda `page`, `position`, `section`,
  `char_start`, `char_end` (antes solo `{"page"}`); `InMemoryVectorStore.add` conserva la metadata
  completa. Se añade `delete(doc_id)` al Protocol y a ambas implementaciones.
- **Impacto:** se puede reconstruir orden/sección desde el índice y limpiar huérfanos.

### AUD-014 — Validación de correspondencias

- **Cambio:**
  - `vectorstore/memory.py::InMemoryVectorStore.add` valida longitudes y usa `zip(..., strict=True)`.
  - `embeddings/embed_chunks.py::embed_chunks` exige **exactamente un vector por chunk**.
- **Impacto:** se elimina la pérdida silenciosa de chunks (antes `zip` truncaba al mínimo).

### AUD-015 — Contrato UI ↔ backend alineado

- **Cambio:** `ui/components/upload_view.py::render` ofrece sólo `pdf`, `md`, `markdown`, `txt` y el
  texto dice “PDF, MD o TXT” (antes ofrecía DOCX e “imágenes”, que el backend rechaza con
  `INVALID_FILE`).
- **Impacto:** el usuario ya no puede elegir un formato “permitido” que la API rechace.

### AUD-016 — CI y lint

- **Estado real:** el workflow existe en la **raíz del repositorio** (`.github/workflows/ci.yml`) y
  aplica `ruff` + `pytest` sobre `nuevamente/backend`. El `I001` citado en `loading_view.py` **no
  era reproducible** con el `ruff` instalado; los errores reales de lint estaban en otros archivos.
- **Cambio:** se limpió `ruff check --config pyproject.toml src tests scripts ../ui` (0 errores):
  `E501` en `core/config.py` y en la suite; `F841` en `result_view.py`,
  `test_chunks_to_chroma.py`, `test_no_context_propagation.py`; y un `invalid-syntax` en
  `result_view.py` (barra invertida dentro de un f-string, inválido en Python 3.11 — versión del
  CI): se precomputa el escapado.
- **Impacto:** `test_aud_016` deja de estar pendiente y el CI puede exigir lint limpio.

### AUD-017 — Calidad de la suite existente

- Se actualizaron los tests que dependían de contratos corregidos (ver §5). También se partieron
  líneas largas y se eliminaron variables/imports sin uso.

### AUD-018 — Jobs huérfanos tras reinicio

- **Cambio:** `db/session.py::reconcile_stale_jobs` marca `ERROR` los jobs `QUEUED`/`PROCESSING`
  pendientes; `api/main.py` lo invoca en el `lifespan` de la app (al arrancar).
- **Explicación e impacto:** las `BackgroundTasks` mueren con el proceso; antes el cliente
  consultaba indefinidamente (la UI corta por timeout a los 60 s). Ahora recibe respuesta inmediata.
  No afecta a los tests porque el `TestClient` no entra en el ciclo de vida.

### AUD-019 — Logging en una línea

- **Cambio:** `core/logging.py::_format_value` escapa `\n`, `\r`, `\t` (JSON) cuando el valor los
  contiene.
- **Impacto:** un nombre de archivo malicioso ya no puede inyectar líneas falsas en el log.

### AUD-020 — `assemble_output` y `generate_content` implementados

- **Cambio:**
  - `generation/orchestrator.py::GenerationOrchestrator.generate_content` arma el prompt, invoca al
    `LLMProvider` y mapea a `ContenidoAdaptado`.
  - `output/assembler.py::assemble_output` compone el output final (ver AUD-002).
  - `api/orchestrator.py` deja de armar el JSON a mano y **reutiliza los `DocumentChunk` reales**
    (se eliminó `_MockChunk`).
- **Impacto:** se elimina código declarado sin usar; el flujo de generación/ensamblado es único.

### AUD-021 — Configuración y documentación sin deriva

- `backend/requirements.txt`: `chromadb>=0.5,<2.0` (rango único); `requirements-rag.txt` deja de
  duplicarlo con `<1.0`.
- `.env.example`: se declaran `APP_VERSION`, `EMBEDDING_DIMENSIONS`, `VECTORSTORE_PROVIDER`, y
  modelos Gemini vigentes.
- Raíz del repositorio `requirements.txt`: delega en `nuevamente/backend/requirements.txt` (fuente
  única).
- `ui/api_client.py`: docstring puerto `8011` → `8000`.
- `README.md`: eliminada la sección `## Estructura` duplicada; se añaden los códigos de error
  nuevos; la referencia a `docs/AUDIT.md` deja de afirmar que “ningún archivo” está implementado.
- `docs/AUDIT.md`: nota de que es una **instantánea histórica** y que RAG/embeddings/vector store ya
  están implementados.
- `core/config.py`: `OCI_BUCKET_NAME` por defecto `nuevamente-docs` (antes un bucket concreto y
  obsoleto).
- **Impacto:** una sola fuente de verdad y documentación consistente con el código.

### AUD-022 — Errores de embeddings y vector store bien tipados

- **Cambio:**
  - `core/exceptions.py`: nuevas excepciones `EmbeddingError` (`EMBEDDING_ERROR`, 502) y
    `VectorStoreError` (`VECTORSTORE_ERROR`, 502).
  - `embeddings/embed_chunks.py`: propaga sin re‑envolver los `NuevaMenteError` del proveedor
    (p. ej. `LLMProviderError`) y envuelve el resto en `EmbeddingError`.
  - `vectorstore/search.py` y `vectorstore/store.py`: lanzan `VectorStoreError` (ya no
    `StorageError` ni `NuevaMenteError` genérico).
- **Impacto:** el cliente recibe el código preciso (`EMBEDDING_ERROR` / `VECTORSTORE_ERROR`) y no se
  filtra el texto crudo del SDK como error de servidor.
