# Plan de integración de `OCI` a `develop` — y qué ya se hizo

**Fecha:** 2026-10-03
**Para:** equipo `develop` / responsables técnicos
**Estado:** 2 PRs abiertos y verificados. Pendiente decisión de merge.

Documentos relacionados:
- `EstructuraRamaOCI.md` — cómo es la rama `OCI` en la práctica (mismo directorio).
- `INTEGRACION_RAMAS.md` (rama `develop`) — auditoría comparativa de ramas.

---

## 1. Resumen para quien tenga 2 minutos

`OCI` tiene el RAG implementado; `develop` tiene el RAG en stubs. **No vamos a mergear `OCI`
como rama** — vamos a **portar los módulos uno por uno**, con un PR por módulo y CI verde.

**Lo que ya está listo:**

| PR | Qué hace | Estado |
|---|---|---|
| [#8](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/pull/8) | Activa la CI (estaba rota) |verde |
| [#9](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/pull/9) | Trae el contenido de demo de `OCI` a `develop` | verde |

**Lo que sigue:** 4 pasos más (embeddings → vectorstore → RAG → validación), luego generación.

**El hallazgo más importante:** la CI de `develop` **nunca se ejecutó**. Eso enmascaraba dos
problemas reales que descubrimos al arreglarla. Está en la sección 3.

---

## 2. Por qué NO hacemos merge de `OCI`

Lo simulamos con `git merge-tree`. Resultado: **cero conflictos**. Y ese es exactamente el
problema — un merge "limpio" que no sirve.

```console
$ git merge-tree --write-tree origin/develop origin/OCI
193024e6a7c4895b7dad73edc6f3c6836d200019

$ git ls-tree -r --name-only 193024e | wc -l
228
```

El merge produce **dos backends completos** conviviendo:

```
228 archivos
├── nuevamente/    122   ← el proyecto real de develop
├── backend/        80   ← proyecto completo de OCI, ignorado por todos
├── ui/              8
├── docs/            7
└── documentacion/   4
```

Git no reporta conflicto porque las rutas son distintas (`nuevamente/backend/src/rag/` vs
`backend/src/rag/`). El conflicto es **semántico**, no textual.

Verificado: tras el merge, `develop` queda **exactamente igual**.

```
nuevamente/backend/src/rag/retrieval_service.py    SIGUE STUB
nuevamente/backend/src/rag/context_builder.py      SIGUE STUB
backend/src/rag/retrieval_service.py               33 líneas (el real, huérfano)
```

Todo el valor de `OCI` aterriza en un directorio que nadie ejecuta. Peor: la CI no lo
detecta, porque testeaba `nuevamente/backend` y seguiría testeándolo.

**Por eso portamos código, no ramas.**

---

## 3. PR #8 — La CI estaba apagada

### Qué pasaba

GitHub Actions solo lee `.github/workflows/` en la **raíz** del repositorio. Nuestro archivo
estaba en `nuevamente/.github/workflows/ci.yml`, así que **nunca se ejecutó**.

```console
$ gh workflow list          # antes
CI (contract-only)	active	371721237
```

GitHub solo veía un workflow viejo, "CI (contract-only)", cuyos últimos 4 runs fueron
`failure`. El `ci.yml` nuevo era invisible.

Además `working-directory: backend` apuntaba a `<raíz>/backend`, que **no existe** en
`develop` (el proyecto está en `nuevamente/`). Estaba mal por partida doble.

### Qué hace el PR

1. Mueve el archivo a la raíz (con `git mv`, queda como rename).
2. Corrige `working-directory` → `nuevamente/backend` y `cache-dependency-path`.

### Los dos fallos que aparecieron al encenderla

Al correr la CI por primera vez, afloraron problemas que estaban ocultos **precisamente
porque nunca se ejecutaba**.

#### 3.1 `develop` no importaba — faltaba el contrato `LLMProvider`

`src/generation/llm_provider.py` definía **`EmbeddingProvider`** en lugar de `LLMProvider`.
Un copy-paste del contrato equivocado; el propio docstring lo delata:

```python
"""Contrato del proveedor de embeddings (COMP-03)."""   # debería decir LLM
class EmbeddingProvider(Protocol):                     # debería ser LLMProvider
```

**`class LLMProvider` no existía en ningún módulo del proyecto**, pero dos archivos lo
importaban:

- `src/generation/orchestrator.py:8`
- `src/validation/fidelity_checker.py:14`

```console
$ python -c "import src.generation.orchestrator"
ImportError: cannot import name 'LLMProvider' from 'src.generation.llm_provider'
```

El PR define el contrato correcto (`generate(prompt, temperature=0.3) -> str`, el mismo que
usa `OCI`). `EmbeddingProvider` no se toca: ya vive bien en `src/embeddings/base.py`.

> **Para el equipo:** esto no agregaba funcionalidad. Repara la importación de módulos que ya
> estaban escritos. Por eso los 115 tests pasaban igual: los tests no cubrían ese módulo.

#### 3.2 Nueve errores de lint

7 auto-corregibles (imports sin usar por duck typing, orden de imports) y 2 líneas de más de
100 caracteres, corregidas a mano.

### Verificación

Ejecutado con Python 3.11 (misma versión que la CI):

| Paso | Resultado |
|---|---|
| `ruff check --config pyproject.toml src tests ../ui` | `All checks passed!` |
| Verificación de imports de `src/` | Todos los módulos importan |
| `pytest -q` | **115 passed** |

Y en GitHub, por primera vez: run `success`, 43 s.

---

## 4. PR #9 — Contenido de demo de `OCI`

### Qué se copió

| De `OCI` | Para qué sirve |
|---|---|
| `INTROS` | Apertura contextualizadora por perfil (demo Fase 1) |
| `TITULOS` | Título por formato (demo Fase 1) |
| `STOPWORDS` | Palabras vacías, para no contarlas como conceptos |
| `conceptos_clave()` | Extrae los `n` términos más frecuentes de un texto |

`conceptos_clave()` la usará `validation/pedagogical_eval.py` en el paso 4 — por eso se trae
antes de tiempo.

### La decisión que se tomó: `develop` conserva sus perfiles

`OCI` usaba slugs ASCII:

```python
INTROS = {"principiante": "Imagina este concepto como una caja de herramientas...", ...}
TITULOS = {"tutorial": "Guía práctica paso a paso", ...}
```

`develop` usa valores legibles, ya fijados en tipos `Literal`:

```python
PerfilDestinatario = Literal["Principiante / Transición de Carrera", ...]
FormatoSalida = Literal["Guía Práctica Paso a Paso (Tutorial)", ...]
```

**Se reescribieron las claves** con los valores exactos de `develop`. Copiar los slugs tal
cual habría dejado dos diccionarios muertos: la generación indexaría por un valor que nunca
llega desde la API.

**Por qué gana `develop`:** los tests existentes y la UI ya dependen de esos valores
(`tests/integration/test_pipeline_e2e.py:17-18` y `:69-71`), y son legibles para el usuario
final.

### Los 7 tests nuevos

Verifican lo que a mano no se sostiene en el tiempo:

- **Cobertura**: todo perfil tiene `INTROS`, todo formato tiene `TITULOS`.
- **Sin claves huérfanas**: `INTROS`/`TITULOS` no tienen entradas que ya no existan en el
  catálogo. *Esto es lo que habría detectado el desalineo entre las dos ramas.*
- **Determinismo**: `conceptos_clave()` devuelve lo mismo para el mismo texto.

### Verificación

| Paso | Resultado |
|---|---|
| `ruff check` | `All checks passed!` |
| Imports | OK |
| `pytest -q` | **122 passed** (115 + 7 nuevos) |

Ningún test existente se modificó ni se rompió.

### Depende de #8

Este PR está **apilado** sobre `ci/fix-workflow-path`. Al mergear #8 primero, el diff de #9
queda reducido a exactamente dos archivos: `src/generation/profiles.py` y
`tests/unit/test_profiles.py`.

---

## 5. Lo que falta: el orden del porte

Cada paso es un PR independiente, **CI verde antes de pasar al siguiente**.

| # | Paso | Módulos | Depende de |
|---|---|---|---|
| 0 | Activar CI | `ci.yml`, `llm_provider.py` | — (hecho, #8) |
| 1 | Embeddings | `providers/mock.py`, `factory.py` | #8 |
| 2 | Vectorstore | `memory.py` + `factory.py` nuevo | 1 |
| 3 | RAG | `retrieval_service.py`, `context_builder.py` | 2 |
| 4 | Validación | `claims_extractor.py`, `fidelity_checker.py`, `pedagogical_eval.py` | 3 |
| 5 | Generación | `builders.py`, `orchestrator.py`, `assembler.py`, tipos `Item*` | 4 |
| — | Contenido de perfiles | `INTROS`/`TITULOS`/`conceptos_clave()` | #8 (hecho, #9) |

### Qué aporta cada paso

**Paso 1 — Embeddings.** No dependen de nada. Desbloquean los tests sin red. Se corrige un
bug: `mock.py` mantiene un `_VOCAB` mutable que se vacía al llegar a `DIM`, así que **el
vector de un token depende del orden en que se procesaron los documentos**. Se reemplaza por
un hash determinista, y el test que lo fija es parte de este paso.

**Paso 2 — Vectorstore.** `InMemoryVectorStore` (72 líneas, coseno real). Además se agrega un
`factory.py` con `VECTORSTORE_PROVIDER`, siguiendo el patrón de `storage/factory.py` que
`develop` ya tiene. **Hoy no hay forma de plugar algo persistente sin editar código.**

**Paso 3 — RAG.** El núcleo: por fin se ejercita la regla NO_CONTEXT (RF-009), que hoy nunca
corre. Incluye el test que hoy **no existe en ninguna rama**: que la regla se **dispare de
verdad** con un documento sin coincidencias.

**Paso 4 — Validación.** Los tres módulos de fidelidad. Reutiliza `conceptos_clave()`, que
ya llegó en el PR #9.

**Paso 5 — Generación.** El de mayor valor funcional: extiende `output/schema.py` con los
tipos `ItemFlashcard`, `ItemQuiz`, `ItemTutorial`, `ItemResumen`, `ItemGuion` y el union
`ItemContenido`. Eso **habilita RF-011/RF-012** ("mismo documento + distinto formato →
estructuras distintas"), que hoy `develop` no puede cumplir: su `output/schema.py` tiene 73
líneas y 5 clases, sin ningún tipo de contenido.

---

## 6. Bugs de `OCI` que se corrigen al portar

| Bug | Dónde | Qué pasa | Qué hacemos |
|---|---|---|---|
| Precedencia | `generation/orchestrator.py:31` | `provider or M() if ... else provider` parsea como `(provider or M()) if ... else provider`. Con `gemini` y `provider=None` queda `None` y **pega el contexto crudo sin llamar al LLM**. Falla en silencio. | Corregir al portar; es de una línea |
| Determinismo | `embeddings/providers/mock.py:22` | `_VOCAB.clear()` al llegar a `DIM` rompe el determinismo entre documentos | Hash determinista en vez de índice secuencial |
| Selección implícita | `api/orchestrator.py:52-59` | Tener `OCI_NAMESPACE`/`OCI_BUCKET_NAME` definidos basta para escribir contra el bucket real, sin un flag explícito | `develop` ya lo resolvió con `STORAGE_PROVIDER`; no se arrastra |
| Ruta absoluta | `tests/conftest.py` | `sqlite:////tmp/opencode/nuevamente_test.db` — ruta de una máquina concreta | `develop` ya usa `tmp_path`; no se arrastra |

---

## 7. Lo que NO se hace

- **No** se mergea la rama `OCI`.
- **No** se borra `nuevamente/` ni se aplana la estructura del proyecto.
- **No** se cambia la estructura de perfiles de `develop`.
- **No** se toca `embeddings/providers/gemini.py` — sigue stub. DT-09 no se cierra aquí.
- **No** se implementa el proveedor real de Gemini (requiere credenciales y confirmación).

## 8. Una advertencia que conviene no perder de vista

El RAG de `OCI` corre de punta a punta sin red, pero **no demuestra que la recuperación
funcione**. Tres razones, detalladas en `EstructuraRamaOCI.md` sección 6:

1. En modo mock los scores de similitud son **siempre positivos**, así que la regla
   NO_CONTEXT **solo se dispara si no hay coincidencias**. La regla de negocio RF-009 **no se
   está ejercitando**.
2. Los embeddings son **hashing de tokens**, no semánticos. Dos textos distintos en significado
   no se aproximan.
3. El vectorstore es **volátil por proceso**: con Uvicorn multi-worker o un reinicio se pierde
   el índice.

Una evaluación honesta del retrieval necesita el proveedor Gemini real con credenciales
(DT-09). Mientras tanto, conviene presentar el RAG como **plomería conectada**, no como
recuperación validada.

---

## 9. Qué se pide al equipo

1. **Mergear #8 primero.** Es bloqueante: sin CI no hay forma de verificar el resto del porte.
2. **Confirmar el enfoque de portar módulos en vez de mergear la rama.** Es la decisión de
   fondo de este plan.
3. **Revisar #9**, que ya puede mergearse después de #8 sin cambios.
4. **Definir quién toma DT-09** (proveedor Gemini real). Es lo único que bloquea una
   demostración honesta del retrieval.
