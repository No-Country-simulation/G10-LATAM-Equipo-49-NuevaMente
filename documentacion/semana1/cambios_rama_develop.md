# Cambios en la rama y plan de cierre de brechas — Semana 1

## 1. Objetivo

Documentar los cambios hechos para integrar OCI (listado de objetos en Object Storage)
como servicio interno del backend, verificar su compatibilidad con lo ya construido y
proponer las acciones para cerrar las brechas pendientes de la **Semana 1**
(FASE 1 + FASE 2 del `PLAN.pdf`).

## 2. Contexto de la rama

- Rama de trabajo actual: `develop`.
- Los cambios descritos están **pendientes de commit** y se preparan para el PR.
- Base del repositorio: backend FastAPI monolítico (`backend/main.py`, `backend/schemas.py`)
  y script de prueba raíz `bucket_test.py`.

## 3. Cambios realizados en la rama

| Archivo | Acción | Descripción |
| --- | --- | --- |
| `.gitignore` | Nuevo | Excluye `.env`, `.env.*` (excepto `.env.example`), `__pycache__`, `.venv`, `venv`, `*.pem`, `data/`. |
| `.env` | Nuevo (local, NO versionado) | Configuración real de OCI: bucket `bucket-20260921-2152-nuevamente-docs-test`, namespace, perfil y ruta de config. |
| `.env.example` | Nuevo (versionado) | Plantilla con variables OCI y valores placeholders. |
| `backend/requirements.txt` | Nuevo | Declara `fastapi`, `uvicorn[standard]`, `pydantic>=2`, `python-dotenv` y `oci` (antes el README apuntaba a un archivo inexistente). |
| `backend/services/__init__.py` | Nuevo | Paquete `services` del backend. |
| `backend/services/oci_storage.py` | Nuevo | `OciStorageService`: carga `.env`, crea cliente OCI **lazy** con `oci.config.from_file` y expone `list_objects(...)` con `prefix`, `limit`, `start`, paginación (`next_start_with`) y campos `size`, `etag`, `timeCreated`, `timeModified`. |
| `backend/schemas.py` | Modificado | Agrega `ObjetoOCI` y `ListadoOCI` para validar la respuesta del endpoint. |
| `backend/main.py` | Modificado | Agrega `GET /test/oci/objects` (aislado), instancia `OciStorageService` y mantiene intactos `/health` y `/adaptar`. |
| `bucket_test.py` | Modificado | Pasa de probar upload/listado a **solo listado**, importando el servicio desde `backend/services/`. |

## 4. Comportamiento con lo ya construido

- **Sin regresión verificada:** tras los cambios, compilan `backend/main.py`, `backend/schemas.py`,
  `backend/services/oci_storage.py` y `bucket_test.py`; `/health` responde `200`, `/adaptar`
  responde `200` con el contrato `PaqueteEducativo` y el nuevo `/test/oci/objects` responde `200`.
- **Reuso de patrones existentes:** el endpoint usa los Pydantic models del backend y el mismo
  esquema de errores amigables (`RespuestaError`) que `/adaptar`.
- **No se tocaron los duplicados de la raíz** (`main.py` y `schemas.py` fuera de `backend/`);
  se propone en la sección 6 declarar `backend/` como canónico y eliminar la duplicación.
- **Configuración por entorno y no por código:** el script ya no tiene hardcodeados namespace
  ni bucket; se leen de `.env`.
- **Seguridad:** no se versionan claves ni credenciales; la API key vive en `~/.oci/config`
  (ya existente) y la carga la hace el cliente OCI por perfil.

## 5. Verificación realizada

| Prueba | Resultado |
| --- | --- |
| `python3 -m py_compile` sobre archivos modificados | OK |
| `python3 bucket_test.py` (listado real) | 7 objetos listados con `name`, `size`, `etag`, `time_modified` |
| `GET /test/oci/objects?limit=2` (TestClient) | `200`, estructura `ListadoOCI` correcta |
| `GET /health` (TestClient) | `200` |
| `POST /adaptar` (TestClient) | `200` sin cambios en el contrato |
| `git check-ignore .env` | `.env` ignorado |

## 6. Brechas principales para cumplir la Semana 1

La Semana 1 pide: **repo funcional, `.env`, ingesta PDF/MD/TXT probada y `/adaptar` mockeado**.
Estado actual por tarea del backlog:

| ID (PLAN) | Entregable | Estado en la rama |
| --- | --- | --- |
| FND-001 | Estructura `src/`, `tests/`, `docs/` | Pendiente |
| FND-002 | `requirements.txt` / `pyproject.toml` | Parcial (solo `requirements.txt`) |
| FND-003 | `.env.example` + loader de settings (pydantic-settings) | Parcial (`.env.example` hecho, loader manual en servicio) |
| FND-004 | Logging estructurado | Pendiente |
| FND-005 | Linter/formatter (ruff) + pre-commit | Pendiente |
| BE-ING-001…004 / ING-005…009 | Ingesta PDF/MD/TXT y manejo de errores (corrupto, escaneado, vacío, tamaño) | Pendiente |
| PROC-003…005 | Limpieza de texto, metadata de chunk, doc demasiado grande | Pendiente |
| BE-PROC-001/002, TASK-001/002 | Modelo `DocumentChunk` + chunking con overlap | Pendiente |
| FE-API-001 | Contrato `/adaptar` mockeado | Parcial (existe `/adaptar` síncrono; el plan define `/ingest` + `/adapt/{job_id}` asíncrono) |
| OCI-001 | Configuración/credenciales OCI | Completado (listado) |
| Definición de Done | Tests ejecutados y evidencia | Pendiente (no hay suite de tests) |

### Brechas principales detectadas

1. **No hay estructura `src/`, `tests/` ni config central.**
   `backend/main.py` y `backend/schemas.py` en la raíz duplican los de `backend/`.
2. **No existe ingesta real.** No hay módulo que lea PDF/MD/TXT ni manejos de error
   (archivo corrupto, PDF escaneado sin texto, MD vacío, límite de tamaño).
3. **No hay chunking.** Falta `DocumentChunk` (trazabilidad RNF-006) y el splitter con
   `CHUNK_SIZE`/`CHUNK_OVERLAP` configurables; el `chunk_text` actual de `main.py` no produce metadata.
4. **Falta suite de pruebas.** No hay `pytest` ni tests unitarios/integración ni evidencia (DoD).
5. **Config sin pydantic-settings.** `oci_storage.py` lee `.env` con `dotenv`; el plan pide un
   loader central de settings.
6. **Autenticación OCI acoplada a claves locales.** Reutiliza `~/.oci/config` (solo listado);
   para FASE 6 (persistencia real) se debe definir Instance Principal y políticas IAM del equipo.
7. **Contrato `/adaptar` no alineado al plan** (`/ingest`, `/adapt/{job_id}`), lo que impacta
   a FE-API-001 y a QA desde Semana 2.
8. **README desactualizado** respecto a comandos, estructura y dependencias.

## 7. Propuestas de mejora para eliminar las brechas

| Prioridad | Acción | Detalle |
| --- | --- | --- |
| Alta | Migrar a empaquetado `src/` | Crear `backend/src/{api,core,ingestion,processing,output,services}` y mover Schemas; declarar `backend/` canónico y eliminar duplicados de la raíz. |
| Alta | Centralizar settings | `backend/src/core/config.py` con `BaseSettings` (pydantic-settings) leyendo `.env`; el servicio OCI consume `settings.oci_*`. |
| Alta | Implementar ingesta PDF/MD/TXT | Módulo con `pdfplumber`/`PyMuPDF`, lectura de `.md`/`.txt`, validaciones de ING-005…009 (tamaño máx., corrupto, escaneado, vacío). |
| Alta | Implementar chunking | `DocumentChunk` (id, doc_id, text, position, section, char_start/char_end) + `RecursiveCharacterTextSplitter` con overlap configurable. |
| Alta | Crear suite de pruebas | `pytest` unitario (chunking, ingesta, service OCI con cliente mock) e integración (endpoints); CI básica; evidencia en el PR. |
| Media | Logging estructurado | `logging`/`structlog` en `core`, con nivel y contexto por request/tarea. |
| Media | Ruff + pre-commit | Añadir `pyproject.toml` con `[tool.ruff]`, hook de pre-commit y sane las reglas del checklist. |
| Media | Alinear contrato API | Definir FE-API-001: `POST /ingest`, `POST /adapt`, `GET /adapt/{job_id}`, manteniendo `/adaptar` como compatibilidad temporal. |
| Media | Autenticación OCI de equipo | Crear grupo IAM de pruebas con política de mínimo privilegio (`read objects`) sobre el bucket; cada integrante con usuario/API key propio; **nunca compartir claves**; en OCI/VM usar Instance Principal. |
| Media | Robustez del endpoint OCI | Tests de casos sin permiso, prefix inexistente, paginación > 1000 y validación de errores `OCI_LIST_FAIL`. |
| Baja | Actualizar README | Comandos (uvicorn, pytest), estructura `src/`, setup de `.env` y rol de OCI. |
| Baja | Mover `bucket_test.py` a pruebas | Convertirlo en smoke test de `tests/integration` (skip si no hay credenciales). |

## 8. Recomendaciones para el PR

- Incluir esta documentación y el output de verificación de la sección 5 como evidencia.
- Mantener `.env` fuera del PR; versionar solo `.env.example`.
- Declarar explícitamente si otros integrantes deben replicar pruebas OCI: cada uno
  necesitará credenciales en su `~/.oci/config`, no un "rol" de código.
- Priorizar las acciones **Alta** antes de cerrar Semana 1; la regla de control del plan
  exige cerrar atrasos CRIT antes de absorber trabajo COULD_HAVE.