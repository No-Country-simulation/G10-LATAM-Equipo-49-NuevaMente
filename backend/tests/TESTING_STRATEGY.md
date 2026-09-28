# Estrategia de testing (Fase 16 del Plan Técnico)

**Esta fase es CONTRACT-ONLY: no existen funciones `def test_...()`.**
Este documento define qué se probará y cómo, para que la implementación
futura tenga una especificación clara y trazable.

## Estructura prevista

```
backend/tests/
├── unit/          # QA-001, QA-002 — sin dependencias externas
├── integration/   # QA-003, QA-004 — vertical slice vía TestClient
└── fixtures/       # documentos de prueba (incluye el golden document)
```

## Suites previstas

| Archivo (futuro) | Cubre | Tipo |
| --- | --- | --- |
| `unit/test_ingestion.py` | `ingestion.router`, extractores, validadores | unit (QA-001) |
| `unit/test_processing.py` | `processing.models.DocumentChunk`, `processing.chunking.chunk_text` | unit (QA-002) |
| `unit/test_embeddings.py` | `embeddings.providers.mock.MockEmbeddingProvider`, `embeddings.embed_chunks` | unit (QA-002) |
| `unit/test_output_schema.py` | `output.schema.NuevaMenteOutput` (instancias válidas/inválidas) | unit |
| `unit/test_fidelity.py` | `validation.fidelity_checker.aggregate_score` (determinismo) | unit |
| `integration/test_pipeline_e2e.py` | Vertical slice completo: `POST /ingest` → `POST /adapt` → `GET /adapt/{job_id}` | integration (QA-003, CU-001) |
| `integration/test_golden_fidelity.py` | Documento de referencia con fidelidad ≥ `FIDELITY_THRESHOLD` (DT-11) | integration / AI eval (QA-004) |

## Criterios de aceptación por suite (extracto — ver TASK-001/002/003 en el
Plan Técnico para el detalle completo de cada uno)

- **Chunking (TEST-UNIT-001):** un texto de 5000 caracteres nunca produce
  chunks con `text` vacío.
- **Vertical slice (TEST-INT-001):** con backend y ChromaDB inicializados,
  `POST /ingest` → `POST /adapt` → `GET /adapt/{job_id}` hasta status final
  debe terminar en `SUCCESS` con `fidelidad_score` presente y JSON válido
  contra `NuevaMenteOutput`.
- **Golden test (TEST-AI-EVAL-001, QA-004):** con un documento de
  referencia de "verdad conocida" (a preparar en DEMO-000, Semana 5),
  generar contenido para 2 perfiles distintos debe dar
  `fidelidad_score >= 0.9` en ambos, o evidencia de qué claim falló.

## Modo de ejecución previsto (una vez implementado)

```bash
cd backend
pytest tests/ -v --cov=src --cov-report=term-missing
```

Con `LLM_PROVIDER=mock` y `EMBEDDING_PROVIDER=mock` (valores por defecto de
`.env.example`), la suite completa debe poder correr sin credenciales
reales — condición necesaria para que corra en CI.

## Tipos de prueba cubiertos (Fase 16)

unit (QA-001, QA-002) · integration (QA-003) · AI evaluation (QA-004,
golden test) · end-to-end (TEST-INT-001) · smoke test (`GET /health`,
antes de cada demo).
