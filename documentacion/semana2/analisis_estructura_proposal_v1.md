# Análisis de estructura — rama `proposal/v1`

## 1. Alcance y contexto

- **Rama:** `proposal/v1` (5 commits; último: `f2c5c32` "Agregar nuevamente_v1 arquitectura carpetas basado en backlog", autora: Diana Ocaña Martínez).
- **Premisa declarada (README):** esta rama es **CONTRACT-ONLY**. No es el MVP implementado: es la arquitectura y los contratos (estructura de carpetas, `Protocol`, schemas Pydantic, firmas de función, configuración declarativa y documentación de trazabilidad). Ningún archivo contiene lógica de negocio ejecutable ni llamadas reales a Gemini, OCI, ChromaDB o SQLite.
- **Enfoque de este análisis:** `nuevamente_v1/`. El prototipo duplicado en la raíz (`nuevamente-g10/`) solo se menciona como riesgo transversal (sección 8).
- **Conteo reportado por la propia rama:** 68 archivos `.py` bajo `backend/src/` y `ui/`, todos con cuerpos `...`; `pytest` recolecta 0 tests.

## 2. Mapa de la estructura analizada

```
nuevamente_v1/
├── .env.example                # 25 variables, alineada a Fase 6, sin secretos
├── .gitignore
├── README.md                   # CONTRACT-ONLY + guía de lectura
├── CONTRIBUTING.md
├── demo.sh                     # guion de demo (placeholder, solo echo)
├── backend/
│   ├── pyproject.toml          # ruff + pytest configurados
│   ├── requirements.txt
│   ├── src/
│   │   ├── core/               # config (BaseSettings), logging, excepciones
│   │   ├── db/                 # Job, JobStatus (persistencia de sesión DT-08)
│   │   ├── api/                # FastAPI contrato: /health, /ingest, /adapt, /adapt/{id}
│   │   ├── ingestion/          # extractores PDF/MD/TXT + validadores (COMP-01)
│   │   ├── processing/         # DocumentChunk + chunking/cleaning (COMP-02)
│   │   ├── embeddings/         # EmbeddingProvider + factory (COMP-03)
│   │   ├── vectorstore/        # Chroma store/search (COMP-04)
│   │   ├── rag/                # retrieval + context_builder (COMP-05)
│   │   ├── generation/         # LLMProvider + prompts (COMP-06)
│   │   ├── validation/         # fidelidad + pedagogía (COMP-07)
│   │   ├── output/             # NuevaMenteOutput (COMP-08)
│   │   └── storage/            # StorageClient OCI/Mock (COMP-09)
│   └── tests/                  # unit/, integration/, fixtures/ — solo .gitkeep
├── ui/                         # app.py + api_client.py + 5 componentes (COMP-10)
├── docs/                       # architecture, TRACEABILITY, AUDIT, demo-scenarios, diagrams
└── n8n-workflows/              # diferencial DT-10, fuera de alcance
```

## 3. Lo que está bien y no debe tocarse

| Elemento | Por qué |
| --- | --- |
| `pyproject.toml` | Ruff (`E,F,I,UP`, line-length 100, `src=["src"]`) y pytest (`testpaths`, `pythonpath="."`) ya configurados → cumple parte de FND-005. |
| `.env.example` (25 vars) | Alineada a Fase 6 del Plan Técnico (chunk, retrieval, fidelidad, LLM, OCI, DB) con valores mock seguros por defecto. |
| Contratos por capa (`Protocol`) | `DocumentExtractor`, `EmbeddingProvider`, `VectorStore`, `RetrievalService`, `LLMProvider`, `ValidationService`, `StorageClient` → respeta RNF-005 (intercambiables sin tocar el resto del pipeline). |
| Taxonomía de excepciones (`core/exceptions.py`) | `InvalidFileError`, `ScannedPdfError`, `NoContextError`, `LLMProviderError`, `StorageError`, con código de dominio mapeado. |
| `docs/TRACEABILITY.md` | Cadena completa `PLAN → Componente → Contrato → Backlog → Implementación → Criterio` + DAG de implementación (Fase 11). |
| `docs/TESTING_STRATEGY.md` | Define QUÉ se probará por suite (unit/integration/golden) y condiciones para correr en CI sin credenciales. |
| Schemas HTTP de `api/schemas.py` | `AdaptRequest` con perfil/formato/nicho/nivel y respuestas `201/202` coherentes con el flujo asíncrono del plan. |
| Convención de nombres OCI DT-07 | `{tipo}/{doc_id}/{timestamp}_{nombre}` documentada en `storage/oci_client.py`. |

## 4. Hallazgos por severidad

### Alta

| # | Hallazgo | Evidencia | Criterio / impacto |
| --- | --- | --- | --- |
| A1 | Documentación que cita archivos inexistentes. `docs/AUDIT.md` clasifica `.github/workflows/ci.yml` como CONFIGURATION y `docs-git/GIT_GITHUB_GUIDE.md` como DOCUMENTATION, y `README.md` enlaza `docs-git/GIT_GITHUB_GUIDE.md`. **Ninguna de las dos rutas existe** en la rama. | `ls-tree` de `nuevamente_v1`: no hay `.github/` ni `docs-git/`. | La auditoría de salida —la regla de cierre del encargo— está viciada: certifica un CI y una guía de Git que no están. Rompe la confianza en `AUDIT.md`. |
| A2 | Ningún `.gitignore` (ni de `nuevamente_v1/` ni de `nuevamente-g10/`) ignora `*.pem`, justo cuando la guía de OCI del equipo instruye crear claves privadas. | `.gitignore` de v1 (18 líneas) no incluye `*.pem`; el de g10 tiene solo 4 líneas. | Riesgo real de versionar claves privadas de OCI en un commit futuro. |
| A3 | 0 tests y ningún CI que los impida. `tests/unit`, `tests/integration` y `tests/fixtures` contienen únicamente `.gitkeep`; no hay `conftest.py`; `pytest` recolecta 0 tests. El CI que lo ejecutaría no existe (A1). | `ls-tree` de los 3 directorios de tests; `TESTING_STRATEGY.md` lo declara explícitamente. | La rama se puede "avanzar" desde la semana 1 hasta la 5 sin que ninguna prueba falle (porque no hay ninguna). Permite presentar arquitectura como progreso. |

### Media

| # | Hallazgo | Evidencia | Criterio / impacto |
| --- | --- | --- | --- |
| M1 | Prompts de IA vacíos. `generation/prompts/generacion_v1.txt` y `verificacion_v1.txt` son PLACEHOLDER con comentario TODO, aunque el texto completo de PROMPT-001 y PROMPT-002 ya está en `PLAN.pdf` (Fase 15). | `AUDIT.md` clasifica ambos como PLACEHOLDER. | Gestión de prompts versionados (BE-GEN) sin contenido real. Ganancia inmediata con copy-paste. |
| M2 | Config OCI desalineada con el bucket real. `.env.example` define `OCI_BUCKET_NAME=nuevamente-g10`, que no es el bucket del equipo (`bucket-20260921-2152-nuevamente-docs-test`), y no declara `OCI_PREFIX`. | `.env.example` v1. | OCI-001 quedará mal configurado el día que el SDK se instancie. |
| M3 | El `Protocol StorageClient` no expone lectura. `storage/base.py::StorageClient` solo define `upload_bytes` y `object_exists`. No hay `list_objects` ni `get_namespace`. | `storage/base.py`. | OCI-001..005 cubren subir/verificar, pero no listar documentos — el caso de lectura que el rol cloud ya resolvió y probó. |
| M4 | Constante hardcodeada. `processing/chunking.py::MAX_DOCUMENT_CHARS = 2_000_000` en vez de venir de `settings` (PROC-005). | `chunking.py`. | Inconsistencia con el patrón declarado en el repo (config centralizada). |
| M5 | FND-001..005 sin trazabilidad. `docs/TRACEABILITY.md` salta de REQ-01 a componentes; las tareas de foundation (estructura, requirements, env loader, logging, lint, tests) no tienen fila propia. | `TRACEABILITY.md`. | El rastro exige "Plan → Backlog → Contrato", pero el backbone de la semana 1 no está rastreable. |

### Baja

| # | Hallazgo | Clasificación |
| --- | --- | --- |
| B1 | `docs/diagrams/pipeline.mmd` con extensión de 3 letras contra el resto del repo (snake_case). | Higiene |
| B2 | `demo.sh` con `set -e` y solo `echo` de los pasos previstos. No rompe nada, pero conviene marcar "placeholder" en el propio archivo para que nadie lo ejecute esperando una demo. | Higiene |
| B3 | Falta `data/` como directorio gitignored de estado local futuro (el `.gitignore` ignora `data/chroma/`, `data/sqlite/`, `data/mock_oci/`, pero el árbol no crea `data/`). | Higiene |

## 5. Matriz de brechas de Semana 1 (`PLAN` → `proposal/v1` → estado)

| Entregable Semana 1 (PLAN) | En `proposal/v1` | Estado real |
| --- | --- | --- |
| FND-001 estructura `src/`/`tests`/`docs` | ✅ estructura completa | Contrato listo |
| FND-002 requirements / pyproject | ✅ `pyproject.toml` + `requirements.txt` | Contrato listo |
| FND-003 `.env.example` + settings loader | ✅ schema `Settings`; ⚠️ `get_settings()` sin implementar | Contrato ✅ / impl. pendiente |
| FND-004 logging estructurado | ✅ firma de `configure_logging()`/`get_logger()` | Contrato ✅ / impl. pendiente |
| FND-005 linter + pre-commit | ⚠️ ruff configurado; sin pre-commit ni CI | Parcial |
| Ingesta PDF/MD/TXT (BE-ING-001..004, ING-005..009) | ✅ contratos de extractores/validadores | 0% implementación |
| Chunking (TASK-001/002, PROC-003..005) | ✅ `DocumentChunk` + firma `chunk_text` | 0% implementación |
| Contrato `/adaptar` mockeado (FE-API-001) | ✅ rutas contratadas en `api/main.py` | Contrato ✅ / sin handler real |
| OCI-001 (config/credenciales) | ✅ `oci_config.py` + settings | Contrato ✅ / impl. pendiente |
| DoD / tests y evidencia | ⚠️ `TESTING_STRATEGY.md` documentado | 0 tests, sin CI |

**Conclusión de la matriz:** la rama está impecable como **contrato**, pero no representa avance en las tareas de implementación críticas de la semana 1. Cualquier reporte de progreso debe distinguir "contrato listo" de "tarea implementada".

## 6. Recomendaciones priorizadas

### P0 — Esta semana
1. **Corregir la documentación auto-referencial (A1).** Opciones: crear de verdad `.github/workflows/ci.yml` y `docs-git/GIT_GITHUB_GUIDE.md`, o eliminar sus menciones de `AUDIT.md`/`README.md`. Recomendado: **crear el CI** (lint + `pytest` aunque recojan 0 tests + import check), porque convierte A1 en valor.
2. **Añadir `*.pem` y `data/` al `.gitignore` (A2).** Prevenir el incidente antes de que ocurra; alinear con el `.gitignore` que ya existe en la rama `OCI`.
3. **Definir la fuente de verdad (riesgo transversal).** Elegir entre `nuevamente_v1/` (recomendado) y `nuevamente-g10/`, moverlo a la raíz y eliminar el otro, con un README raíz. Dejar esto abierto mantiene la ambigüedad del PR/merge.

### P1 — Antes de cerrar Semana 2
4. **Portar la integración OCI real desde la rama `OCI` (M3).** Completar `storage/oci_client.py` con `list_objects`/`get_namespace` (ya probados contra el bucket real), extender `StorageClient` y añadir tests con `MockStorageClient`. Esto convierte COMP-09 en la primera implementación real de la rama y cierra parcialmente OCI-001/002.
5. **Poblar los prompts (M1).** Copiar PROMPT-001/002 de `PLAN.pdf` a `generacion_v1.txt`/`verificacion_v1.txt`.
6. **Alinear configuración OCI (M2).** Renombrar `OCI_BUCKET_NAME` al bucket real en `.env.example` y añadir `OCI_PREFIX`.
7. **Sembrar la primera suite de tests.** Implementar 2-3 tests unitarios reales (p. ej. `DocumentChunk`, `aggregate_score`, `chunk_text` con MockProvider) para que el CI tenga al menos algo que verificar.

### P2 — Higiene
8. **Mover `MAX_DOCUMENT_CHARS` a `settings` (M4).**
9. **Renombrar `pipeline.mmd` → `pipeline.mermaid.md` (B1).**
10. **Marcar `demo.sh` como placeholder en el encabezado (B2).**
11. **Añadir filas FND-001..005 en `TRACEABILITY.md` (M5).**

## 7. Oportunidad concreta para el rol Cloud

Los puntos de integración exactos en `proposal/v1` para el trabajo ya hecho en la rama `OCI`:

| En la rama `OCI` | En `proposal/v1` |
| --- | --- |
| `backend/services/oci_storage.py::OciStorageService.list_objects` (probado: 7 objetos, `size`/`etag`/`time_modified`) | `src/storage/oci_client.py::OCIStorageClient` (placeholder) |
| Carga de config vía `oci.config.from_file` + `.env` | `src/storage/oci_config.py::load_oci_config()` (placeholder) |
| Endpoint `GET /test/oci/objects` | Falta en `api/main.py` (contrato actual solo tiene `/ingest`, `/adapt`, `/adapt/{id}`) |

**Plan sugerido de integración:** portar `OciStorageService` respetando el `Protocol StorageClient` (extendiéndolo con `list_objects`/`get_namespace`), exponer un endpoint de lectura bajo el contrato de `api/main.py`, y cubrirlo con tests usando `MockStorageClient`. Resultado: COMP-09 con implementación real y verificada, sin romper la arquitectura CONTRACT-ONLY del resto.

## 8. Riesgo transversal (breve)

La raíz de `proposal/v1` contiene **dos proyectos** sin README raíz que indique cuál manda: `nuevamente_v1/` (arquitectura nueva) y `nuevamente-g10/` (prototipo antiguo de Rodrigo con `README.md` que promete `docs/arquitectura.md`, `docs/contrato-api.md` y `docs/glosario.md`, que no existen, y marca "✅ Operativo" en fidelidad y JSON con códigos placeholder). Debe resolverse antes del merge (recomendación P0 #3). No se analiza en detalle aquí por alcance solicitado.