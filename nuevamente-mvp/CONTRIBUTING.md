# Contributing

Guía para trabajar en el repositorio de **NuevaMente** (Grupo 10). Aplica
tanto a quien se une hoy como a quien retome el proyecto dentro de seis
meses: si algo no está aquí, probablemente falta documentarlo — abre un PR
a este archivo.

Jerarquía de autoridad si hay conflicto entre fuentes: **Plan Técnico**,
**Backlog** (`PLAN.pdf`, `LISTbacklog.pdf`) y **`NuevaMente-Guia-Desarrollo.md`**
(código de referencia) > este `CONTRIBUTING.md` > estado actual del código.
Ver [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md) para el detalle completo.

## Development setup

1. Clonar el repo y crear el archivo de entorno local:

   ```bash
   git clone https://github.com/NoCountry-simulation/G10-LATAM-Equipo-49-NuevaMente.git
   cd G10-LATAM-Equipo-49-NuevaMente
   cp .env.example .env
   ```

2. Backend (los valores por defecto de `.env` ya corren en modo mock, sin
   credenciales):

   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate      # Windows: .venv\Scripts\activate
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   uvicorn src.api.main:app --reload --port 8000
   ```

3. Verificar que levantó: `curl http://localhost:8000/health` en otra terminal.

4. UI: `cd ui && streamlit run app.py`.

5. Para usar Gemini/OCI reales: editar `GEMINI_API_KEY`, `LLM_PROVIDER=gemini`,
   `EMBEDDING_PROVIDER=gemini` y las variables `OCI_*` en `.env` — **nunca**
   en `.env.example` ni hardcodeadas en el código (SEC-001, SEC-002).
   `.gitignore` ya excluye `.venv/`, `.env`, `__pycache__/`, `.pytest_cache/`,
   `.ruff_cache/`, `.coverage` y `data/{chroma,sqlite,mock_oci}/`.

## Branching

- `main` — siempre desplegable / demo-ready. Solo recibe merges vía PR desde `develop`.
- `develop` — rama de integración activa. Base de todas las ramas de feature.
- Ramas de trabajo, desde `develop`:

  ```
  feature/<epic-o-task-id>-descripcion-corta   # p. ej. feature/BE-VAL-002-fidelity-checker
  fix/<descripcion-corta>
  docs/<descripcion-corta>
  chore/<descripcion-corta>
  ```

  Usar el ID de la tarea del backlog (`FND-001`, `BE-RAG-005`, `VAL-003`, etc.)
  cuando exista, para que la rama sea trazable sin ambigüedad.
- No se trabaja directo sobre `develop` ni `main`.

## Commits

Convención [Conventional Commits](https://www.conventionalcommits.org/),
incluyendo el ID de tarea cuando aplique:

```
<tipo>(<alcance opcional>): <resumen en imperativo> [<ID-tarea>]

feat(validation): calcular fidelity_score con LLM-juez determinista [BE-VAL-002]
fix(rag): no llamar al LLM de generación sin contexto suficiente [BE-RAG-011]
test(processing): cubrir chunking con page desde pages [QA-002]
docs: actualizar matriz de trazabilidad
chore: fijar versión de ruff
```

Tipos válidos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `ci`.
Commits pequeños y enfocados en un solo cambio lógico.

## Pull Requests

Antes de abrir un PR:

- [ ] La rama está actualizada contra `develop`.
- [ ] `ruff check src tests` (desde `backend/`) pasa sin errores.
- [ ] `pytest tests/ -v --cov=src` pasa en local, en modo mock.
- [ ] Se agregaron o actualizaron tests para el cambio (ver Testing).
- [ ] Si se agregó una variable de entorno nueva, está en `.env.example` sin valor real.
- [ ] Si el cambio toca `output/schema.py` (`NuevaMenteOutput`), se avisó al
      equipo y se revisó contra sus consumidores (`api/main.py`,
      `ui/components/result_view.py`, tests de integración) — el contrato
      **no se congela a mitad de proyecto en silencio**.
- [ ] La descripción del PR referencia el/los ID(s) de tarea del backlog que cierra.
- [ ] CI (`.github/workflows/ci.yml`) está en verde.

Requiere al menos 1 revisión aprobada antes de mergear a `develop`. Mergear
a `main` solo desde `develop`, al cierre de una semana/fase, cuando las
tareas `CRIT` de esa fase están en `DONE` (regla de control del Plan
Técnico: no se absorbe trabajo `COULD_HAVE` nuevo si hay atraso en `CRIT`).

## Testing

- Framework: `pytest` + `pytest-cov` (+ `pytest-asyncio` disponible),
  configurado en `backend/pyproject.toml`.
- Estructura (ver `backend/tests/README.md`):
  - `unit/` — ingestion (QA-001), chunking + embeddings (QA-002), output schema, fidelidad.
  - `integration/` — vertical slice vía `TestClient` (QA-003) y golden test de fidelidad (QA-004).
  - `fixtures/conftest.py` fuerza `LLM_PROVIDER=mock` / `EMBEDDING_PROVIDER=mock`
    automáticamente — la suite completa corre sin credenciales.
- Comando:

  ```bash
  cd backend
  pytest tests/ -v --cov=src --cov-report=term-missing
  ```

- Todo módulo nuevo bajo `src/` que implemente un requisito `MUST_HAVE` del
  backlog necesita al menos un test unitario antes de pasar a `DONE`.

## Code quality

- Linter: [`ruff`](https://docs.astral.sh/ruff/) (`backend/pyproject.toml`,
  `line-length = 100`, reglas `E, F, I, UP, B`).

  ```bash
  cd backend
  ruff check src tests
  ```

- No leer variables de entorno con `os.environ` fuera de `src/core/config.py`
  — todo pasa por `Settings`/`settings` (pydantic-settings).
- No hardcodear el umbral de fidelidad (`FIDELITY_THRESHOLD`) ni ningún otro
  valor de configuración sensible: van en `.env` / `.env.example`, nunca con
  valor real en `.env.example` ni en el código
  (`backend/scripts/check_definition_of_done.sh` lo audita automáticamente,
  buscando `GEMINI_API_KEY=<algo>` o claves tipo `AIzaSy...` / `BEGIN
  PRIVATE KEY`).
- CI ejecuta lint, tests con cobertura, un smoke import de la app y
  `scripts/audit_checklist.py` en cada push/PR a `develop` o `main`. Un PR
  con CI en rojo no se mergea.

## Architecture

- La estructura de carpetas sigue las capas del pipeline (Ingestion →
  Processing → Embeddings → Vector Store → RAG → Generation → Validation →
  Output → Storage → Interface). Detalle completo y tabla de "dónde va cada
  tipo de cambio nuevo": [`docs/architecture.md`](docs/architecture.md).
- `backend/src/` es la única fuente de verdad del backend; `api/main.py` no
  contiene lógica de negocio, solo orquesta vía `api/orchestrator.py`.
- Cambiar de proveedor de LLM o de embeddings implica implementar la
  interfaz existente y registrarla en `embeddings/factory.py` /
  `generation/llm_provider.py`, nunca modificar el código que los consume.
- Todo componente de IA (embeddings, generación, validación) debe tener
  fallback/mock funcional, para que dev y tests nunca dependan de red.

## Definition of Done

Una tarea del backlog se marca `DONE` solo cuando:

- [ ] Código implementado.
- [ ] `backend/scripts/check_definition_of_done.sh` pasa completo (import
      sin errores, `ruff check`, `pytest -q`, `.env.example` sin secretos,
      sin claves hardcodeadas).
- [ ] Tests creados y ejecutados en verde para el criterio de aceptación de
      la tarea (local y en CI).
- [ ] Documentación actualizada si aplica (docstring, `README.md`,
      `docs/architecture.md`).
- [ ] Variables de entorno nuevas documentadas en `.env.example` (sin valor real).
- [ ] Evidencia entregada en el PR (output de `pytest -v`, o de
      `verify_mvp.sh` / `audit_checklist.py` cuando aplica, o captura de la UI).
- [ ] Criterios de aceptación de la tarea (Plan Técnico / backlog) cumplidos.
- [ ] Integrado a `develop` sin romper `pytest tests/ -q` de ningún otro módulo.

Referencia completa y script ejecutable: `backend/scripts/check_definition_of_done.sh`
(Fase 17 de la Guía de Desarrollo). Antes de una demo, correr en orden:
`check_definition_of_done.sh` → `pytest -v` → `verify_mvp.sh` →
`audit_checklist.py`.
