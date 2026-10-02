# Auditoría de integración de ramas — `develop` / `OCI` / `proposal/v1`

**Fecha:** 2026-10-02
**Alcance:** diagnóstico del estado de las ramas antes de integrar `OCI` a `develop`.
**Fuera de alcance:** este documento **no propone un plan de merge**. Registra qué hay,
qué aporta cada rama y qué decisiones el equipo debe tomar primero.

Todos los datos son reproducibles con los comandos indicados. Ramas analizadas contra
`origin/` a fecha de redacción.

---

## 1. Mapa de ramas

| Rama | Commits exclusivos | `merge-base` con `develop` | Merge directo a `develop` |
|---|---|---|---|
| `develop` | — | — | base |
| `OCI` | **11** | `f9bd75a` | ⚠️ Acepta, pero duplica el proyecto (sección 4) |
| `proposal/v1` | **8** | **ninguno** | 🔴 **Rechazado** — historias sin relación |
| `RAG-Gemini` | **1** | `95f7301` | Pendiente, fuera de alcance de este documento |
| `main` | **1** | `46bbd5d` | — |
| `planning` | **29** | `e1ba2ed` | — |

```bash
git rev-list --left-right --count origin/develop...origin/<rama>
git merge-base origin/develop origin/<rama>   # vacío = sin ancestro común
```

### 1.1 El ancestro común es casi vacío

```bash
$ git ls-tree -r --name-only f9bd75a
SpikeGemini/requirements.txt
```

El merge-base entre `develop` y `OCI` contiene **un solo archivo**. Ambas ramas hicieron un
drop completo e independiente del proyecto sin una base común de código. Consecuencia:
**no existe un merge "correcto" por historia** — Git no tiene información para arbitrar
y cada decisión debe tomarse a mano.

### 1.2 `proposal/v1` no es integrable con merge

```bash
$ git merge-base origin/develop origin/proposal/v1
# (vacío)
```

Un `git merge proposal/v1` hacia `develop` sería **rechazado** por Git
(`refusing to merge unrelated histories`). Requiere `--allow-unrelated-histories`
o port manual de archivos.

---

## 2. Qué aporta `develop`

Referencia: 94 tests, 86 archivos `.py`, CI activa en `nuevamente/.github/workflows/ci.yml`.

**Ingesta end-to-end**
- `ingestion/text_decoding.py` — decodifica `utf-8-sig` y `cp1252`, rechaza binarios.
  Relevante para el equipo LATAM: un `.txt` exportado de Windows con tildes se rechaza
  sin este módulo.
- `ingestion/validators.py` — `validate_signature()` (un `.pdf` que no empieza con `%PDF-`
  no llega a `PdfReader`), `display_name()` (evita filtrar rutas del usuario al response).
- `ingestion/router.py` — `_pdf_warnings()` avisa "N de M páginas no tienen texto
  extraíble", lo que da feedback honesto en vez de truncar en silencio.
- `ingestion/pdf_extractor.py` — maneja PDF cifrados. Sin esto, un PDF protegido se
  clasifica como `SCANNED_PDF`, que es un diagnóstico falso.

**Almacenamiento y seguridad**
- `storage/naming.py` — `sanitize_filename()` previene path traversal
  (`test_storage.py:25-33` cubre `"../../etc/passwd" → "passwd"`).
- `storage/factory.py` — selección explícita por `STORAGE_PROVIDER`. Los tests fuerzan
  `mock`, lo que los hace herméticos.
- `storage/upload.py` — sube **y verifica**; mapping de content-type correcto.

**Contratos y robustez**
- `core/exceptions.py` — cada excepción trae `http_status`; elimina boilerplate en `main.py`.
- `core/logging.py` — `log_stage()` contextmanager con `duration_ms` (RNF-003).
- `core/config.py` — `PROJECT_ROOT`, `resolve_path()`, `sqlite_path`, validadores de chunking.
- `api/main.py` — CORS (sin él la UI de Streamlit en `:8501` no puede llamar la API),
  streaming acotado del upload, handler global de `Exception` como red de seguridad.

**Interfaz y tooling**
- `ui/` completo: 372 líneas implementadas frente a stubs de 10–17 líneas en `OCI`.
- `generation/mock_adapter.py` — el nivel de detalle controla el tamaño real de la salida
  (`CHUNKS_POR_NIVEL = {"breve": 1, "estandar": 3, "profundo": 5}`).
- `generation/prompts/*.txt` — texto real de PROMPT-001/002.
- 6 scripts de arranque (`setup`, `run_api`, `run_ui` × sh/bat), `docs-git/`,
  `ejemplos/`, `tests/helpers.py` (genera PDFs reales sin dependencias externas).

**Tests**: 94, incluyendo `test_db.py`, `test_processing.py`, `test_storage.py`,
`test_api_ingest.py` (14 tests del contrato HTTP), `test_ui_api_client.py`.

---

## 3. Qué aporta `OCI`

Referencia: 33 tests, 78 archivos `.py`, **sin CI**.

### 3.1 RAG implementado

En `develop` estos módulos son stubs (cuerpo `...`); en `OCI` están implementados.

| Módulo | `develop` | `OCI` |
|---|---|---|
| `rag/retrieval_service.py` | stub | construye query con perfil+nicho+tema, embedder + vectorstore |
| `rag/context_builder.py` | stub | filtra por `RETRIEVAL_MIN_SCORE` → `NoContextError` (regla NO_CONTEXT, RF-009) |
| `validation/fidelity_checker.py` | stub | verificación por solapamiento + `aggregate_score` determinista |
| `validation/claims_extractor.py` | stub | extracción por oraciones con filtro |
| `validation/pedagogical_eval.py` | stub | metadata pedagógica vía `conceptos_clave()` |
| `embeddings/providers/mock.py` | stub | hashing determinista (`DIM=256`) — desbloquea el vectorstore |
| `output/assembler.py` | stub | arma `NuevaMenteOutput` con score de fidelidad |
| `generation/orchestrator.py` | stub | genera contenido desde los items |

Recuento de stubs (`...` en `backend/src/`): **31 en `develop` vs 21 en `OCI`**.

### 3.2 Items pedagógicos tipados

`OCI` añade a `output/schema.py` los tipos `ItemFlashcard`, `ItemQuiz`, `ItemTutorial`,
`ItemResumen`, `ItemGuion` y el union `ItemContenido`, más
`generation/builders.py` (140 líneas, un builder por formato).

Esto es lo que habilita **RF-011/RF-012** ("mismo documento + distinto formato → estructuras
distintas") con salida estructurada real. En `develop` no existe ninguna referencia a `items`
en todo `backend/src/`.

`OCI` también amplía `FORMATOS_MVP` con `flashcards`, `quiz`, `guion`
(cubre GEN-006/GEN-007) y agrega `INTROS` + `conceptos_clave()` a `generation/profiles.py`.

### 3.3 Integración OCI Object Storage

- `storage/base.py` — agrega `StorageObject`, `StorageListing` y extiende el `Protocol`
  con `get_namespace()` y `list_objects(prefix, limit, start)` con paginación.
- `storage/oci_client.py` — implementa `list_objects` requesting
  `fields="size,etag,timeCreated,timeModified"` (evita los `null` que documenta la runbook).
- `storage/mock_client.py` — implementa `list_objects` y `get_namespace` en el mock.
- `backend/scripts/list_bucket.py` — CLI de diagnóstico, **única herramienta de
  inspección del bucket en el repo**.

Verificado contra un bucket real (ver `documentacion/semana1/cambios_rama_develop.md` §5:
7 objetos listados).

### 3.4 Vectorstore en memoria

`vectorstore/memory.py` implementa el `Protocol` `VectorStore` en RAM, con coseno real y
filtro por `doc_id`. Desbloquea el flujo RAG completo sin ChromaDB ni credenciales.

### 3.5 `python-multipart`

`OCI` lo declara en `requirements.txt:6`. **`develop` no lo tiene** y lo necesita:
`UploadFile = File(...)` en `api/main.py` falla en runtime sin él.

### 3.6 Corrección de un bug de `develop`

`develop:backend/src/generation/llm_provider.py` define `EmbeddingProvider` (Protocol),
**no `LLMProvider`**. Es una copia de `embeddings/base.py`. Pero dos módulos lo importan:

```bash
$ git grep -n "from src.generation.llm_provider import LLMProvider" origin/develop
nuevamente/backend/src/generation/orchestrator.py:8
nuevamente/backend/src/validation/fidelity_checker.py:14
```

Ambos fallan con `ImportError`. `docs/AUDIT.md` clasifica el archivo como
"CONTRATO (pendiente)", así que la auditoría AST no detectó la regresión: un `Protocol`
con cuerpos `...` *parece* un contrato válido.

`OCI` define correctamente `LLMProvider` + `GeminiLLMProvider` + `MockLLMProvider`.

---

## 4. El problema estructural: el merge no falla, produce un repo roto

```bash
$ git merge-tree --write-tree origin/develop origin/OCI
$ echo $?
0
```

**Cero conflictos.** Pero no porque las ramas sean compatibles, sino porque **viven en
rutas distintas**: `develop` usa `nuevamente/` como carpeta raíz y `OCI` la eliminó
(commit `db0b3f2`, "refactor: adoptar y aplanar la estructura"). Git no detecta choques
entre `backend/src/api/main.py` y `nuevamente/backend/src/api/main.py` porque son
archivos diferentes.

Resultado del merge:

| Ubicación | Archivos | Origen |
|---|---|---|
| `backend/`, `ui/`, `docs/`, `n8n-workflows/` (raíz) | **96** | `OCI` |
| `nuevamente/backend/`, `nuevamente/ui/`, `nuevamente/docs/` | **121** | `develop` |

Además quedan **duplicados los archivos de control**:

```
.env.example        +  nuevamente/.env.example
.gitignore          +  nuevamente/.gitignore
README.md           +  nuevamente/README.md
```

Consecuencias concretas:

1. **El CI sigue corriendo sobre la copia de `develop`.** El workflow vive en
   `nuevamente/.github/workflows/ci.yml` y usa `working-directory: backend`, relativo a
   la raíz de ese workflow. El código de `OCI` queda sin lintear y sin testear.
2. **`OCI` no tiene CI**, así que su contribution no tiene ninguna red de seguridad
   automática.
3. Hay dos `.env.example` con valores distintos, y solo uno es el que la app realmente lee
   (depende de dónde se lance).
4. `main` recibe el doble de archivos del proyecto y `git log`/
   `docs/AUDIT.md` dejan de reflejar la realidad.

**Este es el punto que conviene decidir antes de ejecutar cualquier `git merge`.**

---

## 5. `proposal/v1` — los 3 commits que nunca llegaron a `develop`

`proposal/v1` comparte historia con `OCI` (merge-base `f2c5c32`) pero **no** con `develop`.
Tiene 8 commits, de los cuales 5 son ancestros de `OCI`. Los 3 restantes nunca se
integraron a ninguna rama.

| Commit | Qué hace | Veredicto |
|---|---|---|
| `574a066` "Actualiza propuesta v1" | Agrega `ci.yml`, los prompts de PROMPT-001/002 y `docs-git/GIT_GITHUB_GUIDE.md` a `nuevamente_v1/` | **Superado.** Los prompts y la guía son byte-idénticos a los de `develop`; `ci.yml` y `.gitignore` ya están más avanzados. No hay nada que recuperar. |
| `322fac4` "Remove team roles from README" | Quita la tabla de roles del README de `nuevamente_v1/` | **Decisión abierta** → sección 6, punto 5. |
| `39e0770` "Eliminación del nivel_detalle de SolicitudAdaptacion" | Elimina `nivel_detalle` y el `Literal NivelDetalle` de `nuevamente-g10/backend/schemas.py` | **No portar.** Contradice los tres documentos oficiales → sección 5.1. |

### 5.1 `nivel_detalle`: el Plan Técnico lo exige, el commit lo elimina

El commit `39e0770` (30/09) borra:

```diff
-  NivelDetalle = Literal["Didactico", "Tecnico", "Estrategico"]

   class SolicitudAdaptacion(BaseModel):
       ...
-      nivel_detalle: NivelDetalle = "Didactico"
```

Los tres documentos oficiales del proyecto lo exigen:

| Documento | Referencia | Prioridad |
|---|---|---|
| `Nuevamente_PlanTecnico_v1.pdf` | REQ-13 "Nivel de detalle configurable" | — |
| `Nuevamente_PlanTecnico_v1.pdf` | RF-013 "Selección de nivel de detalle" | — |
| `Nuevamente_PlanTecnico_v1.pdf` | GEN-005 "Control de nivel de detalle (breve/estándar/profundo)" | — |
| `Nuevamente_PlanTecnico_v1.pdf` | Historia de usuario: *"Elige perfil, formato y nivel de detalle"* | — |
| `LISTbacklog.pdf` | "Control de nivel de detalle (breve/estándar/profundo)" | — |
| `PLAN.pdf` | "Nivel de detalle configurable" | — |
| `planning/planeacion/Nuevamente_PlanTecnico_v2.md:72` | REQ-13 | **OBLIGATORIO** |
| `planning/planeacion/NuevaMente_PlanTecnico_v2.md:176` | RF-013 | **P0** |
| `planning/planeacion/NuevaMente_PlanTecnico_v2.md:767,821` | GEN-005 | **MUST** |

```bash
git show origin/planning:planning/planeacion/NuevaMente_PlanTecnico_v2.md | grep -n "REQ-13"
pdftotext Nuevamente_PlanTecnico_v1.pdf - | grep -n "REQ-13\|RF-013\|GEN-005"
```

`develop` y `OCI` implementan correctamente los tres niveles:

| Ubicación | Contenido |
|---|---|
| `develop:backend/src/api/schemas.py:40` | `nivel_detalle: str = "estandar"` |
| `develop:backend/src/api/orchestrator.py:52` | `NIVELES_DETALLE = ("breve", "estandar", "profundo")` |
| `develop:backend/src/api/orchestrator.py:129` | validación contra esa tupla |
| `develop:backend/src/generation/models.py:13` | `NivelDetalle = Literal["breve","estandar","profundo"]` |
| `develop:ui/components/selection_view.py` | `select_slider` de nivel de detalle |
| `OCI:backend/src/api/schemas.py:29` | `nivel_detalle: str = "estandar"` |

**Conclusión:** el commit `39e0770` se aplicó sobre el artefacto equivocado y no debe
portarse. Las tres ramas activas están alineadas con el Plan Técnico; `proposal/v1` no.

#### Por qué se aplicó sobre el archivo equivocado

El acta de la junta del 28/09 (`planning/avances/semana2/ResumenJunta2909.md`) registra:

> *"Se subió el proyecto de Rodrigo a la rama Proposal/v1, proyecto nuevamente-g10."*
> *"Razón Rodrigo y Diana están actualizando la rama develop. eliminando piezas sueltas y
> subiendo a rama proposal/v1"*

El acta **no registra ninguna decisión sobre quitar `nivel_detalle`**. Y `nuevamente-g10/`
se subió como referencia, no para integrarse.

El prototipo además usa un vocabulario incompatible con el contrato real:

| `nuevamente-g10/backend/schemas.py` | `develop` / `OCI` |
|---|---|
| `PerfilDestinatario = ["Principiante","Junior","Arquitecto","Ejecutivo"]` | `PERFILES_MVP = ["principiante","developer","lider_tecnico","ejecutivo"]` |
| `FormatoSalida = ["Tutorial","Flashcards","Quiz","TLDR","Guion"]` | `FORMATOS_MVP = ["tutorial","resumen_ejecutivo"(,"flashcards","quiz","guion")]` |
| `NichoSector = ["Fintech","Salud","E-commerce","General"]` | no existe en `AdaptRequest` |
| — | `NIVELES_DETALLE = ("breve","estandar","profundo")` |

PascalCase en español vs `snake_case` en inglés, y `"TLDR"` vs `"resumen_ejecutivo"`.
Portar esa carpeta exigiría un mapeo de vocabulario completo, no un cherry-pick.

### 5.2 `nuevamente-g10/` está huérfana

```bash
git ls-tree -r --name-only origin/<rama> | grep -c '^nuevamente-g10/'
```

| Rama | `nuevamente-g10/` | `nuevamente_v1/` |
|---|---|---|
| `main` | 0 | 0 |
| `develop` | 0 | 0 |
| `OCI` | 0 | 0 |
| `RAG-Gemini` | 0 | 0 |
| `planning` | 0 | 0 |
| **`proposal/v1`** | **8 archivos** | 93 archivos |

Sus 8 archivos (238 líneas: `main.py` + `schemas.py`, más `.env.example`, `README.md`,
`demo.sh`, un `.docx` de arquitectura y un workflow de n8n) están superados: su chunker
por oraciones, su RAG por frecuencia de tokens y su `STOP` de palabras están
reimplementados mejor en `backend/src/` de `OCI` (`chunking.py` con offsets reales,
`retrieval_service.py`, `profiles.py::conceptos_clave()`).

**Recomendación: no portar el código.** Se deja constancia aquí para que la decisión sea
explícita. Los dos artefactos documentales (`Arquitectura Bakend nuevamente G 10.docx` y
`n8n-workflows/NuevaMente v1.json`) son referencias del encargo y pueden rescatarse si el
equipo lo considera útil.

---

## 6. Decisiones pendientes

Ninguna de estas cinco está resuelta. Bloquean la integración.

### 1. Estructura de directorios canónica

`develop` usa `nuevamente/` como carpeta raíz (commit `57e1335`, "Reorganizar proyecto
dentro de nuevamente"). `OCI` la eliminó (commit `db0b3f2`, "adoptar y aplanar la
estructura en la raíz"). Ambas decisiones son recientes y deliberadas.

Pregunta: ¿raíz plana (como `OCI`) o `nuevamente/` (como `develop`)?

#### Consecuencia de seguridad concreta

La decisión no es solo estética. En `develop`, el `.gitignore` está en
`nuevamente/.gitignore`, **no en la raíz del repositorio**:

```bash
$ git ls-tree -r --name-only origin/develop | grep gitignore
nuevamente/.gitignore

$ git check-ignore -v .env
# (sin salida: no ignorado)
```

Las reglas de un `.gitignore` solo aplican a su propio directorio y subdirectorios. Por
tanto, en `develop` **nada de la raíz del repositorio está protegido**. Verificado sobre un
working tree con `develop` checkout:

```bash
$ git add -n .env __pycache__ backend
add '.env'
add '__pycache__/bucket_test.cpython-314.pyc'
add 'backend/data/mock_oci/resultados/.../20260928210942_.json'
...
```

Un `.env` con credenciales, `__pycache__/` y datos de pruebas locales **serían commiteados**
en `develop`. `OCI` no tiene el problema: su `.gitignore` está en la raíz y cubre
`.env`, `.env.*`, `!.env.example`, `*.pem`, `__pycache__/` y `data/`.

Si se elige conservar `nuevamente/`, hay que agregar un `.gitignore` en la raíz del
repositorio. Si se elige la raíz plana, el de `OCI` ya sirve.

### 2. Método de integración

Dado que el merge es conflict-free pero duplicante (sección 4), las opciones son:

- **Port manual selectivo**: rama nueva desde `develop`, cherry-pick de los commits de `OCI`
  resolviendo archivo por archivo. Historial limpio y auditable. Requiere trabajo.
- **Merge + limpieza**: `git merge OCI` y luego un commit que elimine la copia huérfana.
  Preserva el historial literal de `OCI`, pero deja un merge commit con 121 archivos
  duplicados que luego se borran.

### 3. `OCI_BUCKET_NAME` commiteado

`OCI:backend/src/core/config.py:58` usa el **bucket real del equipo** como valor por
defecto en código. `develop:core/config.py:66` usa `"nuevamente-g10"`, que según la
auditoría de `OCI` no es el bucket real.

```bash
$ grep -rn "OCI_BUCKET_NAME" --include=*.py --include=.env.example .
```

Consecuencia: con `OCI` + un `OCI_NAMESPACE` en el entorno, cualquier ejecución escribe en
un bucket compartido. Además `.env.example:62` (en ambas ramas) tiene el bucket real
versionado.

**Recomendación:** dejar el default vacío y forzar que `OCIStorageClient` falle con
`StorageError` si falta — la guarda ya existe en `OCI:oci_client.py:31-32`.

### 4. Contratos de nombres en conflicto

| Concepto | `develop` | `OCI` | Nota |
|---|---|---|---|
| Prefijo de resultados | `generated/` | `resultados/` | `upload.py:50` vs `upload.py:18`; hay tests que assertan cada valor |
| `document_id` | `doc_{hex12}` | `{hex24}` | el prefijo evita confundir doc con job |
| `job_id` | `job_{hex12}` | `{hex16}` | |
| Chunk ID | `{doc_id}-chunk-{n}` | `{doc_id}_{n:04d}` | |
| Timestamp DT-07 | `%Y%m%dT%H%M%SZ` | `%Y%m%d%H%M%S` | |

### 5. Tabla de roles en el README

Tres ramas, tres estados distintos:

| Rama | Tabla de equipo |
|---|---|
| `develop` | no existe |
| `OCI` | **agregada** (`README.md:87-98`) |
| `proposal/v1` | **eliminada** por `322fac4` |

Además `develop` y `OCI` discrepan en el destino del README: `develop` lo orienta a
arquitectura y contratos; `OCI` declara explícitamente *"Este repositorio NO es el MVP
implementado"*, lo cual dejó de ser cierto en `develop`.

---

## 7. Hallazgos técnicos puntuales

Aparecieron durante el análisis. No bloquean la integración pero conviene registrarlos.

### En `develop`

| # | Ubicación | Hallazgo |
|---|---|---|
| 1 | `generation/llm_provider.py` | Define `EmbeddingProvider` en vez de `LLMProvider`; 2 módulos lo importan → `ImportError` (sección 3.6) |
| 2 | `requirements.txt` | Falta `python-multipart`, requerido por `UploadFile = File(...)` (sección 3.5) |
| 3 | `.env.example:45` | `GEMINI_GENERATION_MODEL` no corresponde a ningún campo de `Settings`, que espera `GEMINI_MODEL` y `GEMINI_EMBEDDING_MODEL`. Con `extra="ignore"` se descarta en silencio |
| 4 | `.env.example:63` | `OCI_PREFIX=OCI-001` — un ID de backlog usado como prefijo de almacenamiento, y `Settings` ya no tiene el campo |
| 5 | `.env.example:42-43` | `LLM_PROVIDER=gemini` sin `GEMINI_API_KEY` |
| 6 | `.gitignore:5` | Solo ignora `.env` exacto; `.env.local`, `.env.production` se commitearían. Falta `.env.*` + `!.env.example` |
| 7 | `tests/conftest.py` | No fuerza `LLM_PROVIDER`/`EMBEDDING_PROVIDER=mock`; un `.env` de dev con `gemini` romperá los tests al integrar RAG |
| 8 | `setup.sh` / `setup.bat` | Instalan `requirements.txt`, sin pytest ni ruff → un dev nuevo no puede testear ni lintear |
| 9 | `ui/api_client.py:5` | El docstring dice puerto `8011`; el código usa `8000` |

### En `OCI`

| # | Ubicación | Hallazgo |
|---|---|---|
| 1 | `api/orchestrator.py:139` | Pasa `job_id=""` hardcodeado a `_persistir_resultado` aunque el método recibe `job_id` en L84 → el objeto queda como `resultados/{doc_id}/{stamp}_.json`, perdiendo el `job_id` |
| 2 | `generation/orchestrator.py:31` | `provider = provider or MockLLMProvider() if settings.LLM_PROVIDER == "mock" else provider` — por precedencia, con `LLM_PROVIDER=gemini` y `provider=None` queda `None` y el pipeline pega el contexto crudo como contenido, sin llamar al LLM. Falla en silencio |
| 3 | `embeddings/providers/mock.py` | `_VOCAB` es global mutable y se limpia al llegar a `DIM=256` → embeddings no deterministas entre ejecuciones |
| 4 | `core/config.py:66` | `env_file="../.env"` es relativo al CWD, no a la raíz del proyecto |
| 5 | `storage/oci_client.py:122` | `build_object_name` inline sin sanitizar: preserva `../` (anti path-traversal) |
| 6 | `tests/conftest.py:13` | `DATABASE_URL = "sqlite:////tmp/opencode/nuevamente_test.db"` — ruta absoluta de una máquina concreta, **compartida por todos los tests**. En otra máquina puede fallar con `unable to open database file` |
| 7 | `db/session.py` | `set_job_result()` no actualiza el status; `api/main.py` lo hace en un segundo UPDATE → 2 transacciones con ventana de inconsistencia |
| 8 | `storage/upload.py:22-30` | Content-type por cadena de `endswith`: una extensión desconocida cae a `text/plain` |
| 9 | `api/orchestrator.py:44-52` | Selecciona OCI implícitamente si hay `OCI_NAMESPACE` → por eso `conftest` tiene que blanquear esas variables. Frágil |

### Artefactos que conviene no integrar

| Artefacto | Motivo |
|---|---|
| `opencode.json` | Configuración de tooling personal. Referencia `~/.config/opencode/github_token` y expone un MCP de GitHub en la raíz del repo |
| `SpikeGemini/requirements.txt` | Eliminado a propósito en `develop` (`a0b9e37`); sus 2 líneas ya están cubiertas por `requirements.txt` |
| `documentacion/**/*.pdf` (2 archivos, 153 KB c/u) | Duplicados byte-idénticos entre `semana1/` y `semana2/`; el `.md` tiene el mismo contenido |

### Secretos

**No se encontró ninguna clave privada, API key, OCID ni fingerprint commiteado** en
ninguna de las tres ramas. Verificado:

```bash
git grep -nEi "BEGIN .*PRIVATE KEY|ocid1\.user\.oc1\.[a-z0-9]{20}|fingerprint=[a-f0-9]{2}:" origin/develop origin/OCI origin/proposal/v1
```

El único valor environment-specific real es `OCI_NAMESPACE=axkf02paerjf` en
`documentacion/semana1/guia_entorno_oci_equipo.md` (3 veces). No es un secreto —va en las
URLs públicas del bucket— pero identifica la tenancy. Conviene reemplazarlo por un
placeholder en la runbook.

`*.pem` y `.oci/` están en `.gitignore` de ambas ramas.

---

## 8. Cómo reproducir este análisis

```bash
git fetch --all --prune

# 1. Conteo de commits por rama
for r in develop OCI proposal/v1 RAG-Gemini main planning; do
  printf "%-14s ahead=%s behind=%s\n" "$r" \
    "$(git rev-list --count origin/develop..origin/$r)" \
    "$(git rev-list --count origin/$r..origin/develop)"
done

# 2. Ancestros comunes
for r in OCI proposal/v1 RAG-Gemini main planning; do
  echo "$r -> $(git merge-base origin/develop origin/$r)"
done

# 3. Contenido del merge-base develop<->OCI
git ls-tree -r --name-only $(git merge-base origin/develop origin/OCI)

# 4. Simular el merge SIN aplicarlo
git merge-tree --write-tree origin/develop origin/OCI

# 5. Ver la duplicación resultante
T=$(git merge-tree --write-tree origin/develop origin/OCI)
git ls-tree -r --name-only $T | grep -cE "^(backend|ui|docs|n8n-workflows)/"
git ls-tree -r --name-only $T | grep -c '^nuevamente/'
git ls-tree -r --name-only $T | grep -E '^\.env\.example$|^\.gitignore$|^README\.md$'

# 6. Commits de proposal/v1 no integrados
git log --oneline origin/develop..origin/proposal/v1

# 7. Stubs por rama
git grep -c '^\s*\.\.\.$' origin/develop -- 'nuevamente/backend/src/*'
git grep -c '^\s*\.\.\.$' origin/OCI -- 'backend/src/*'
```

`git merge-tree --write-tree` **no modifica el repositorio**: escribe el árbol resultado
en el object store y devuelve su hash.

---

## Referencias

- `nuevamente/docs-git/GIT_GITHUB_GUIDE.md` — convenciones de ramas, commits y PRs.
- `nuevamente/docs/AUDIT.md` — estado de implementación por archivo.
- `nuevamente/docs/TRACEABILITY.md` — matriz de trazabilidad al backlog.
- `planning/avances/semana2/ResumenJunta2909.md` — acta de la junta del 28/09.
- `planning/planeacion/NuevaMente_PlanTecnico_v2.md` — Plan Técnico v2.
- `OCI:documentacion/semana1/cambios_rama_develop.md` — bitácora de la integración OCI.
- `OCI:documentacion/semana1/guia_entorno_oci_equipo.md` — runbook de configuración OCI.
- `OCI:documentacion/semana2/analisis_estructura_proposal_v1.md` — auditoría de `proposal/v1`.