# Tests

- `unit/` — QA-001 (`test_ingestion.py`), QA-002 (`test_chunking.py`, `test_embeddings.py`) y
  `test_output_schema.py`, `test_fidelity.py`. No dependen de servicios externos.
- `integration/` — QA-003 (`test_pipeline_e2e.py`, vertical slice completo vía `TestClient`) y
  QA-004 (`test_golden_fidelity.py`, golden test).
- `fixtures/` — `conftest.py` (fuerza `LLM_PROVIDER=mock` / `EMBEDDING_PROVIDER=mock` y limpia
  `data/chroma_test`, `data/sqlite/test.db` y `data/mock_oci` tras cada test) y
  `golden_document.txt` (documento de referencia del golden test, QA-004).

`conftest.py` fija el modo mock automáticamente: no se necesitan credenciales de Gemini ni de
OCI para correr la suite completa.

Ejecutar (cobertura mínima esperada antes de marcar QA-001..QA-004 como DONE: ver guía §16.7):

```bash
cd backend
pytest tests/ -v --cov=src --cov-report=term-missing
```
