# Estructura y estado real de la rama `OCI`

**Fecha:** 2026-10-02
**Alcance:** documentar cómo es `OCI` en la práctica —estructura de carpetas, qué está
implementado y qué es solo contrato, dónde vive el RAG y qué tan maduro es.
**Fuera de alcance:** este documento **no propone un plan de merge**. Ese análisis está en
`INTEGRACION_RAMAS.md` (rama `develop`). Este documento describe una rama, no la integración.

Todos los datos son reproducibles con los comandos indicados, verificados contra `origin/OCI`
a fecha de redacción.

> **Actualización 2026-10-08:** el conteo de §1 sigue vigente (12 commits exclusivos, 107
> archivos, merge-base `f9bd75a`). Corregido: Gemini ya no es stub en ambas ramas — `develop`
> cerró DT-09 con un proveedor real (§6.6 actualizado), y el recuento de stubs en `develop`
> bajó de 21 a 9 (§5). El análisis de madurez del RAG en `OCI` (§6 y §7) sigue vigente,
> porque `OCI` no incorporó el proveedor real.

---

## 1. Identidad de la rama

| Propiedad | Valor |
|---|---|
| Commits exclusivos vs. `develop` | **12** |
| `merge-base` con `develop` | `f9bd75a` |
| Archivos totales | **107** (78 `.py`) |
| Estructura de directorios | Raíz plana — el proyecto vive en la raíz, no en `nuevamente/` |

El ancestro común contiene **un solo archivo**:

```console
$ git ls-tree -r --name-only $(git merge-base origin/develop origin/OCI)
SpikeGemini/requirements.txt
```

Ambas ramas hicieron un drop completo e independiente del proyecto sin base común de código.
Consecuencia: **no existe un merge "correcto" por historia** — Git no tiene información para
arbitrar y cada decisión debe tomarse a mano.

> **Nota:** `INTEGRACION_RAMAS.md` registra 11 commits exclusivos y 108 archivos para `OCI`.
> Los números de aquí (12 / 107) son los vigentes a fecha de este documento; la rama avanzó
> después de redactarse aquella auditoría.

---

## 2. Mapa de carpetas

| Carpeta | Archivos | Responsabilidad |
|---|---:|---|
| `backend/src/` | 66 | Monolito con 14 paquetes (`api`, `core`, `db`, `embeddings`, `generation`, `ingestion`, `output`, `processing`, `rag`, `storage`, `validation`, `vectorstore`) |
| `backend/tests/` | 11 | Suite de pruebas — **7 archivos, 32 tests** |
| `backend/scripts/` | 1 | `list_bucket.py` — diagnóstico del bucket OCI |
| `ui/` | 7 | Streamlit (`app.py`, `api_client.py`, 5 componentes) |
| `docs/` | 7 | Arquitectura, auditoría, trazabilidad, diagramas, escenarios de demo |
| `documentacion/` | 5 | Runbooks de OCI (semana 1) y análisis de `proposal/v1` (semana 2) |
| raíz | 6 | `.env.example`, `README.md`, `CONTRIBUTING.md`, `demo.sh`, `opencode.json`, `.gitignore` |

### Por qué no hay otro documento con esto

| Candidato | Por qué no cubre este hueco |
|---|---|
| `docs/architecture.md` | Es **byte-idéntico** en `OCI` y `develop`. Describe la arquitectura *diseñada* — su título es "CONTRACT-ONLY (DOC-002)" y su sección 7 es "Lo que queda explícitamente fuera de esta fase". No dice qué implementó realmente `OCI`. |
| `docs/AUDIT.md` (164 líneas) | Clasifica archivos por estado, pero no explica la estructura ni las diferencias con `develop`. |
| `documentacion/semana2/analisis_estructura_proposal_v1.md` | Analiza `proposal/v1`, no `OCI`. |

---

## 3. Estado real por paquete

La distinction clave de `OCI` es que separa **implementación** de **contrato**. Los archivos
`base.py` de cada paquete son `Protocol` con métodos `...` — eso es intencional, no un stub.
Lo que `OCI` aporta son las implementaciones concretas detrás de esos contratos.

| Paquete | Implementación en `OCI` | Contrato / pendiente |
|---|---|---|
| `ingestion/` | `pdf_extractor`, `txt_extractor`, `md_extractor`, `router`, `validators` | `base.py` (`Protocol`) |
| `processing/` | `chunking` (94 líneas), `cleaning`, `models` | — |
| `embeddings/` | `providers/mock.py`, `factory.py`, `embed_chunks.py` | `providers/gemini.py` 🔴 stub solo en `OCI`; `develop` ya tiene Gemini real (DT-09 cerrado) |
| `vectorstore/` | **`memory.py` (72 líneas) — coseno real** | `base.py`, `client.py`, `search.py`, `store.py` |
| `rag/` | **`retrieval_service.py` (33)**, **`context_builder.py` (31)** | `base.py` (`Protocol`) |
| `generation/` | `orchestrator.py`, `builders.py` (139), `profiles.py` | `llm_provider.py` (parcial) |
| `validation/` | `fidelity_checker.py` (64), `claims_extractor.py`, `pedagogical_eval.py` | `base.py` (`Protocol`) |
| `output/` | `assembler.py` (68), `schema.py` (126) | — |
| `storage/` | `oci_client.py` (124), `mock_client.py`, `upload.py`, `verify.py` | `base.py` (`Protocol`) |
| `api/` | `main.py` (134), `orchestrator.py` (168), `schemas.py` | — |
| `core/` | `config.py`, `exceptions.py`, `logging.py` | — |
| `db/` | `session.py` (137), `models.py` | — |

---

## 4. Dónde está el RAG

El RAG de `OCI` **no es un archivo, son cuatro módulos coordinados**. Con la ruta completa
desde la raíz de `OCI`:

| Archivo | Líneas | Qué hace |
|---|---:|---|
| `backend/src/rag/retrieval_service.py` | 33 | `DefaultRetrievalService.retrieve()` — construye la query con `perfil` + `nicho` + `tema`, la embebe y consulta el vectorstore |
| `backend/src/rag/context_builder.py` | 31 | Filtra los resultados por `RETRIEVAL_MIN_SCORE` → lanza `NoContextError`; arma el contexto con la referencia `[chunk_id (p.N)]` |
| `backend/src/vectorstore/memory.py` | 72 | `InMemoryVectorStore` — similaridad coseno real, con filtro por `doc_id` |
| `backend/src/embeddings/providers/mock.py` | 41 | Embeddings deterministas por hashing de tokens, `DIM=256` |

Además están `rag/base.py` y `vectorstore/base.py` (22 y 47 líneas), que existen en **ambas**
ramas y definen los `Protocol`. Lo que cambia es que en `OCI` tienen implementación detrás.

**El flujo completo:**

1. `embeddings/embed_chunks.py` genera embeddings para cada chunk al ingerir.
2. `rag/retrieval_service.py` arma la query del usuario y busca los chunks más cercanos.
3. `rag/context_builder.py` descarta lo irrelevante y, si no queda nada, corta con `NoContextError`
   (regla NO_CONTEXT, RF-009).
4. `generation/orchestrator.py` recibe el contexto y genera la adaptación.

> Ver enlaces a los archivos en la rama `OCI` dentro del repositorio.

---

## 5. Qué implementa `OCI` que `develop` deja en stub

Comparando los archivos con cuerpo `...` en `backend/src/`: **`develop` tiene 9, `OCI` tiene 12.**

De esos 12 de `OCI`, la mayoría son `Protocol` (donde `...` es correcto) más
`embeddings/providers/gemini.py`, que sigue siendo un stub **en `OCI`** — **DT-09 permanece
cerrado solo en `develop`**, no portado a `OCI`.

Los **9 archivos** que `develop` deja en stub y `OCI` implementa:

| Archivo | Qué aporta `OCI` |
|---|---|
| `rag/retrieval_service.py` | Consulta, embedding y búsqueda vectorial |
| `rag/context_builder.py` | Regla NO_CONTEXT y armado de contexto con referencias |
| `embeddings/providers/mock.py` | Hashing determinista — desbloquea el vectorstore |
| `embeddings/factory.py` | Selección de proveedor de embeddings |
| `generation/orchestrator.py` | Genera contenido desde los items |
| `output/assembler.py` | Arma `NuevaMenteOutput` con score de fidelidad |
| `validation/claims_extractor.py` | Extracción por oraciones con filtro |
| `validation/fidelity_checker.py` | Verificación por solapamiento + `aggregate_score` |
| `validation/pedagogical_eval.py` | Metadata pedagógica vía `conceptos_clave()` |

```console
# Reproducir la comparación
git grep -l '^\s*\.\.\.$' origin/develop -- 'nuevamente/backend/src/*.py'   # 21
git grep -l '^\s*\.\.\.$' origin/OCI      -- 'backend/src/*.py'             # 12
```

---

## 6. Advertencias de madurez del RAG

**Esta sección es la más importante del documento.** El RAG de `OCI` corre de punta a punta sin
red, pero **no demuestra que la recuperación funcione**. Es preciso saber esto antes de
presentarlo o integrarlo.

**6.1 — En modo mock, la regla NO_CONTEXT casi nunca se dispara.** El propio docstring de
`context_builder.py` lo admite:

> *"En el modo mock determinista (sin embeddings reales) los scores de similaridad coseno son
> siempre positivos, por lo que la regla NO_CONTEXT solo se dispara si `matches` está vacío."*

Es decir: el corte por score —la regla de negocio RF-009— **no se está ejercitando en las
pruebas**. Pasa por el camino correcto por construcción, no por comportamiento.

**6.2 — Los embeddings no son semánticos.** `mock.py` mapea tokens a índices por hashing
(`DIM=256`). Dos textos con palabras distintas pero significado parecido no se aproximan. Con
`LLM_PROVIDER=mock` el pipeline completo aparenta funcionar sin que nadie note que el retrieval
es una ruleta.

**6.3 — El determinismo del mock es frágil.** `mock.py:19-23` mantiene un `_VOCAB` mutable y,
al llegar a `DIM`, lo **vacía con `_VOCAB.clear()`**. Como los índices se asignan por orden de
aparición, el vector de un token **depende de qué documentos seHaven procesado antes**. Con dos
documentos distintos en el mismo proceso, los vectores no son comparables.

**6.4 — El vectorstore es volátil por proceso.** `memory.py` guarda los chunks en un `dict` en
memoria (`self._chunks`). Con Uvicorn multi-worker o tras un reinicio **se pierde el índice**.
Los chunks siguen en SQLite, pero no hay re-indexado: el siguiente retrieval devuelve vacío.

**6.5 — No hay switch de proveedor para el vectorstore.** La dependencia está cableada en dos
puntos:

- `rag/retrieval_service.py:19-20` — `store or InMemoryVectorStore()`
- `api/orchestrator.py:31-36` — singleton `_VECTORSTORE`

Contraste con el storage de objetos, que sí decide por entorno
(`api/orchestrator.py:52-59`): si `OCI_NAMESPACE` y `OCI_BUCKET_NAME` están definidos usa
`OCIStorageClient`, si no `MockStorageClient`. El vectorstore no tiene equivalente, así que
**no hay forma de plugar una implementación persistente sin tocar código**.

*(Efecto lateral del mismo patrón en storage: la selección es implícita. Tener las variables de
entorno cargadas basta para activar el bucket real — no hay un `STORAGE_PROVIDER` explícito que
lo haga visible.)*

**6.6 — El proveedor real ya no es el bloqueante en `develop`, pero sí en `OCI`.**
`embeddings/providers/gemini.py` sigue siendo un stub en `OCI`. En `develop`, en cambio, DT-09
ya está cerrado: Gemini es real y usado por el pipeline. Mientras no se porte, el único path
ejecutable en `OCI` es el mock.

**Consecuencia práctica:** con la configuración por defecto `OCI` demuestra que la
plomería está conectada, no que recupere bien. Una evaluación honesta del retrieval en `OCI`
necesita `EMBEDDING_PROVIDER=gemini` con credenciales reales, lo cual requiere portar DT-09.

---

## 7. Bugs conocidos en `OCI`

Detectados al leer el código. Ninguno bloquea la ejecución, pero tres afectan el comportamiento
observable.

| # | Ubicación | Problema |
|---|---|---|
| 1 | `api/orchestrator.py:139` | `run_adaptation` recibe `job_id: str = ""` (línea 84) pero la llamada a `_persistir_resultado` pasa `job_id=""` hardcodeado. El `job_id` real se descarta y los objetos quedan como `{stamp}_.json` sin identificador de job. |
| 2 | `generation/orchestrator.py:31` | Precedencia: `provider or MockLLMProvider() if settings.LLM_PROVIDER == "mock" else provider` parsea como `(provider or MockLLMProvider()) if ... else provider`. Con `LLM_PROVIDER=gemini` y `provider=None`, queda `None`, cae el `elif provider is not None` (línea 36) y **pega el contexto crudo sin llamar al LLM**. Falla en silencio. |
| 3 | `backend/tests/conftest.py:13` | `DATABASE_URL = "sqlite:////tmp/opencode/nuevamente_test.db"` — ruta absoluta de una máquina concreta, compartida por todos los tests. anyone que no tenga `/tmp/opencode` falla. |
| 4 | `embeddings/providers/mock.py:22` | `_VOCAB.clear()` al alcanzar `DIM` rompe el determinismo entre documentos. Ver 6.3. |
| 5 | `api/orchestrator.py:52-59` | La selección de storage es implícita: basta con tener `OCI_NAMESPACE`/`OCI_BUCKET_NAME` definidos para escribir contra el bucket real. Ver 6.5. |

### Dónde `develop` está mejor que `OCI`

No todo gana `OCI`. Estos casos resolved a favor de `develop`:

- **Prompts reales.** `OCI` tiene `generation/prompts/generacion_v1.txt` y `verificacion_v1.txt`
  con **1 línea cada uno** (marcadores TODO). `develop` tiene **25 y 26 líneas** de prompt real.
- **Menos superficie duplicada.** `OCI` arrastra `documentacion/` con runbooks que `develop`
  eliminó a propósito, y sus `docs/` están oriented a la fase OCI, no al producto final.

---

## 8. Qué haría falta para que el RAG sea demostrable

En orden de esfuerzo, sin tocar la arquitectura:

1. **Portar el proveedor Gemini real a `OCI`** (cerrado en `develop`, pendiente en `OCI`) → habilita evaluar si el retrieval recupera algo.
2. **Un test que verifique que NO_CONTEXT se dispara** con un documento sin coincidencias.
3. **Provider por entorno para el vectorstore**, como el de storage — sin esto, cualquier
   implementación persistente exige editar código.
4. **Corregir los bugs 1 y 2**, que son de una línea cada uno y el #2 afecta la ruta de demo.

Los puntos 2 y 4 no dependen de ninguna decisión de integración y podrían hacerse en `develop`
sin conflicto.

---

## Reproducibilidad

```console
# Identidad de la rama
git rev-list --count origin/develop..origin/OCI                    # 12
git merge-base origin/develop origin/OCI                           # f9bd75a
git ls-tree -r --name-only origin/OCI | wc -l                      # 107

# Estructura
git ls-tree -r --name-only origin/OCI | awk -F/ 'NF>1{print $1"/"$2} NF==1{print "(raiz)"}' \
  | sort | uniq -c | sort -rn

# Stubs
git grep -l '^\s*\.\.\.$' origin/OCI -- 'backend/src/*.py' | wc -l   # 12

# Bugs citados
git show origin/OCI:backend/src/api/orchestrator.py | grep -n 'job_id'
git show origin/OCI:backend/src/generation/orchestrator.py | grep -n 'provider ='
git show origin/OCI:backend/tests/conftest.py | grep -n sqlite
```

Todos los comandos son de lectura. Ninguna modificación a `OCI` o `develop` es necesaria para
mantener este documento al día: se lee `origin/OCI` y se compara.