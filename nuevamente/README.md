# NuevaMente

Sistema para ingestar documentación técnica y generar adaptación educativa por perfil, formato y nicho.

## Estado actual

- `POST /ingest`: implementado.
- `POST /adapt`: implementado con generación LLM + fallback automático a mock.
- Si falla el proveedor LLM o la respuesta no cumple contrato, el resultado sigue siendo válido con:
  - `status="PARTIAL"`
  - contenido no vacío
  - observación con `MOCK_NOTICE`
- `GET /adapt/{job_id}` devuelve estado asíncrono del job.

## Requisitos

- Python 3.11+

## Inicio rápido

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

API: http://127.0.0.1:8000  
Docs: http://127.0.0.1:8000/docs

## Endpoints

- `GET /health`
- `POST /ingest` (multipart `file`)
- `POST /adapt` (JSON)
- `GET /adapt/{job_id}`

## Configuración de proveedores

Se controla por variables de entorno:

- `LLM_PROVIDER`: `mock` (default) | `gemini` | `cohere`
- `EMBEDDING_PROVIDER`: `mock` (default) | `gemini` | `cohere`
- `VECTORSTORE_PROVIDER`: `chroma` (default) | `memory`
- `STORAGE_PROVIDER`: `mock` (default) | `oci`

Con `mock` no se requieren credenciales.  
Con `gemini`/`cohere` se requieren API keys válidas.

## Pruebas y calidad

Desde `nuevamente/backend`:

```bash
pytest -q -p no:cacheprovider
ruff check --config pyproject.toml src tests scripts ../ui
python -c "import importlib, pkgutil, src; [importlib.import_module(n) for _, n, _ in pkgutil.walk_packages(src.__path__, prefix='src.')]"
```

## Limitaciones actuales

- No se incluye OCR para PDFs escaneados.
- En entornos sin credenciales/API reales, la adaptación opera con fallback mock.
- Las validaciones de OCI/LLM reales dependen de credenciales y servicios externos disponibles.

## Estructura resumida

- `backend/src/api`: endpoints y orquestación
- `backend/src/ingestion`: extracción de texto
- `backend/src/processing`: limpieza y chunking
- `backend/src/embeddings`: embeddings
- `backend/src/vectorstore`: índice vectorial
- `backend/src/rag`: retrieval y armado de contexto
- `backend/src/generation`: prompts, proveedores y orquestación LLM
- `backend/src/validation`: evaluación de fidelidad
- `backend/src/output`: schema de salida
- `backend/src/storage`: almacenamiento mock/OCI
- `backend/tests`: suites unit, integration y audit
