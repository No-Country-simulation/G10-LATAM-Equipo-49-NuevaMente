# Contributing

Este repositorio contiene **arquitectura y contratos**, no una
implementación funcional (ver `docs/architecture.md`). Esta guía explica
cómo implementar sobre esa base sin romperla. Para convenciones de Git y
GitHub (branches, commits, PRs, Issues), ver el archivo dedicado
[`docs-git/GIT_GITHUB_GUIDE.md`](docs-git/GIT_GITHUB_GUIDE.md) — no se
repiten aquí.

## Development setup

Este repositorio, tal como está, no se "instala" ni se "ejecuta" — es
CONTRACT-ONLY. Cuando comience la implementación real:

```bash
cd backend
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp ../.env.example ../.env       # completar valores reales, nunca commitear .env
```

Los comandos de `uvicorn`/`streamlit` (ver Fase 12 del Plan Técnico) solo
tendrán sentido una vez que `api/main.py` y `ui/app.py` dejen de ser
firmas con cuerpo `...`.

## Branching

Ver [`docs-git/GIT_GITHUB_GUIDE.md`](docs-git/GIT_GITHUB_GUIDE.md).

## Commits

Ver [`docs-git/GIT_GITHUB_GUIDE.md`](docs-git/GIT_GITHUB_GUIDE.md).

## Pull Requests

Ver [`docs-git/GIT_GITHUB_GUIDE.md`](docs-git/GIT_GITHUB_GUIDE.md) para
requisitos generales. Regla específica de este repositorio: un PR que
implementa una función previamente marcada `...` debe:

1. Reemplazar únicamente el cuerpo de esa función (no cambiar su firma
   sin actualizar también `docs/TRACEABILITY.md`).
2. Agregar los tests correspondientes bajo `backend/tests/` (ver
   `backend/tests/TESTING_STRATEGY.md` para qué suite le corresponde).
3. Si la función implementada es parte de un `Protocol` (`EmbeddingProvider`,
   `LLMProvider`, `StorageClient`, `VectorStore`, `DocumentExtractor`,
   `RetrievalService`, `ValidationService`), verificar que la clase
   concreta siga cumpliendo la interfaz — no relajarla para simplificar
   la implementación.

## Testing

No existen tests ejecutables todavía (`def test_...`) — solo la
estrategia en [`backend/tests/TESTING_STRATEGY.md`](backend/tests/TESTING_STRATEGY.md),
con la suite prevista para cada componente y sus criterios de aceptación.
Al implementar una función:

1. Ubicar en `TESTING_STRATEGY.md` qué archivo de test le corresponde.
2. Crear ese archivo (`backend/tests/unit/test_*.py` o
   `backend/tests/integration/test_*.py`) con los casos ahí descritos.
3. Ejecutar (una vez que exista implementación real):

   ```bash
   cd backend
   pytest tests/ -v --cov=src --cov-report=term-missing
   ```

   Con `LLM_PROVIDER=mock` / `EMBEDDING_PROVIDER=mock` (valores por
   defecto de `.env.example`), la suite debe poder correr sin
   credenciales reales.

## Code quality

- Linter: `ruff` (`backend/pyproject.toml`). Mientras el código siga
  siendo CONTRACT-ONLY, la regla `B` (flake8-bugbear) está deliberadamente
  excluida porque señalaría los cuerpos `...` como sospechosos; debe
  reactivarse (`select = ["E", "F", "I", "UP", "B"]`) en el primer PR que
  empiece a implementar lógica real.
- No hardcodear secretos ni credenciales en ningún archivo — ni siquiera
  como ejemplo (RNF-001, SEC-001). `.env.example` nunca lleva valores
  reales.
- No leer variables de entorno con `os.environ` fuera de `core/config.py`
  una vez implementado — todo pasa por `Settings`/`get_settings()`.
- CI (`.github/workflows/ci.yml`) valida en cada PR: lint, que todos los
  módulos de `src/` importen sin error, y que `pytest --collect-only` no
  falle (aunque recolecte 0 tests mientras no exista implementación).

## Architecture

Ver [`docs/architecture.md`](docs/architecture.md) para el detalle
completo. Regla general: cada carpeta de `backend/src/` corresponde a
exactamente un componente (COMP-01..COMP-11, Fase 5 del Plan Técnico) y
solo debe depender de las carpetas que ese componente declara como
dependencia en esa fase. Ejemplos:

- Un nuevo formato de extracción de archivo → nuevo `*_extractor.py` en
  `ingestion/`, registrado en `ingestion/router.py`. No debe tocar
  `processing/`.
- Un nuevo proveedor de LLM o de embeddings → nueva clase en
  `generation/llm_provider.py` o `embeddings/providers/`, que cumpla el
  `Protocol` existente. No debe cambiar la firma de
  `GenerationOrchestrator.generate_content()` ni de `embed_chunks()`.
- Un cambio en el contrato de salida → `output/schema.py`
  (`NuevaMenteOutput`). Cualquier cambio de campos requiere actualizar
  `docs/TRACEABILITY.md` y revisar contra todos los consumidores
  documentados ahí (regla heredada de TASK-003 del Plan Técnico: el
  contrato "no se congela a mitad de proyecto en silencio").
- Un cambio de infraestructura de almacenamiento → `storage/`, cumpliendo
  `StorageClient`. Mantener `mock_client.py` funcional (una vez
  implementado) para que dev/tests no dependan de una cuenta OCI real.

## Definition of Done

Adaptado de la Fase 17 del Plan Técnico a este repositorio en dos etapas:

**Para un PR que solo toca arquitectura/contratos (como este repositorio):**
- [ ] La estructura de carpetas sigue `docs/architecture.md` / Fase 7 del Plan Técnico.
- [ ] Todo archivo nuevo está clasificado en `docs/AUDIT.md` (CONTRACT / PLACEHOLDER / DOCUMENTATION / CONFIGURATION).
- [ ] `docs/TRACEABILITY.md` referencia el nuevo contrato desde algún requisito o tarea del backlog.
- [ ] Ningún archivo nuevo contiene lógica funcional, llamadas externas o tests ejecutables.
- [ ] CI en verde (lint + import-check + collect-only).

**Para un PR que implementa una función marcada `...` (implementación futura):**
- [ ] Código implementado, respetando la firma documentada.
- [ ] Código compila / se ejecuta sin errores.
- [ ] Tests creados según `backend/tests/TESTING_STRATEGY.md` y en verde.
- [ ] Documentación actualizada (`docs/TRACEABILITY.md` pasa esa fila de
      "pendiente" a "implementado", con el PR como evidencia).
- [ ] Variables de entorno nuevas documentadas en `.env.example`.
- [ ] Evidencia entregada en el PR (output de `pytest -v`).
- [ ] Criterios de aceptación de la tarea (Plan Técnico / backlog) cumplidos.
- [ ] Integrado a `develop` sin romper `pytest tests/ -q` de ningún otro módulo.
