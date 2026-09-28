# Auditoría de salida (regla de cierre del encargo)

Clasificación de **todos** los archivos de este repositorio en una de
cuatro categorías: `CONTRACT`, `PLACEHOLDER`, `DOCUMENTATION`,
`CONFIGURATION`. Ninguno está clasificado como `IMPLEMENTATION`, `REAL
INTEGRATION`, `FUNCTIONAL MOCK` ni `EXECUTABLE BUSINESS LOGIC`.

- **CONTRACT** — define una interfaz, un schema de datos o una firma de
  función (`Protocol`, `BaseModel`, función con cuerpo `...`).
- **PLACEHOLDER** — archivo vacío o con un único comentario `# TODO:
  implementación futura`, sin contenido de contrato.
- **DOCUMENTATION** — explica arquitectura, trazabilidad, convenciones o
  estrategia, sin código.
- **CONFIGURATION** — configuración declarativa (dependencias, entorno, CI, lint).

## backend/src/core/
| Archivo | Clasificación |
| --- | --- |
| `config.py` | CONTRACT (schema `Settings` + firma `get_settings()`) |
| `logging.py` | CONTRACT (firmas `configure_logging()`, `get_logger()`) |
| `exceptions.py` | CONTRACT (taxonomía de excepciones, sin lógica) |

## backend/src/ingestion/
| Archivo | Clasificación |
| --- | --- |
| `models.py` | CONTRACT (`PageText`, `IngestResult`) |
| `base.py` | CONTRACT (`Protocol DocumentExtractor`) |
| `validators.py` | CONTRACT (firmas `validate_size`, `detect_type`) |
| `pdf_extractor.py` | CONTRACT (firma `extract_pdf_text`) |
| `md_extractor.py` | CONTRACT (firma `extract_markdown_text`) |
| `txt_extractor.py` | CONTRACT (firma `extract_txt_text`) |
| `router.py` | CONTRACT (clase `IngestionRouter`, firma `ingest`) |

## backend/src/processing/
| Archivo | Clasificación |
| --- | --- |
| `models.py` | CONTRACT (`DocumentChunk`, validadores como firma) |
| `cleaning.py` | CONTRACT (firma `clean_text`) |
| `chunking.py` | CONTRACT (firma `chunk_text`) |

## backend/src/embeddings/
| Archivo | Clasificación |
| --- | --- |
| `base.py` | CONTRACT (`Protocol EmbeddingProvider`) |
| `providers/gemini.py` | PLACEHOLDER (clase declarada, métodos `...`, comentario TODO explícito) |
| `providers/mock.py` | PLACEHOLDER (ídem, modo mock) |
| `factory.py` | CONTRACT (firma `get_embedding_provider`) |
| `embed_chunks.py` | CONTRACT (firma `embed_chunks`) |

## backend/src/vectorstore/
| Archivo | Clasificación |
| --- | --- |
| `base.py` | CONTRACT (`Protocol VectorStore`, `VectorStoreMatch`) |
| `client.py` | CONTRACT (firma `get_chroma_client`) |
| `store.py` | CONTRACT (clase `ChromaVectorStore`, firma `persist_chunks`) |
| `search.py` | CONTRACT (firma `similarity_search`) |

## backend/src/rag/
| Archivo | Clasificación |
| --- | --- |
| `base.py` | CONTRACT (`Protocol RetrievalService`) |
| `retrieval_service.py` | CONTRACT (clase `DefaultRetrievalService`) |
| `context_builder.py` | CONTRACT (firma `build_context`) |

## backend/src/generation/
| Archivo | Clasificación |
| --- | --- |
| `models.py` | CONTRACT (`AdaptationRequest`, `ContenidoAdaptado`) |
| `profiles.py` | CONFIGURATION (catálogo declarativo de perfiles/formatos) |
| `prompts/README.md` | DOCUMENTATION |
| `prompts/generacion_v1.txt` | PLACEHOLDER (comentario TODO, sin contenido real del prompt) |
| `prompts/verificacion_v1.txt` | PLACEHOLDER (ídem) |
| `llm_provider.py` | CONTRACT (`Protocol LLMProvider` + clases placeholder) |
| `orchestrator.py` | CONTRACT (clase `GenerationOrchestrator`) |

## backend/src/validation/
| Archivo | Clasificación |
| --- | --- |
| `models.py` | CONTRACT (`Claim`, `ClaimEvaluation`, `FidelityEvaluation`) |
| `base.py` | CONTRACT (`Protocol ValidationService`) |
| `claims_extractor.py` | CONTRACT (firma `extract_claims`) |
| `fidelity_checker.py` | CONTRACT (firmas `verify_claim`, `aggregate_score`, clase `DefaultValidationService`) |
| `pedagogical_eval.py` | CONTRACT (firma `evaluate_pedagogical_metadata`) |

## backend/src/output/
| Archivo | Clasificación |
| --- | --- |
| `schema.py` | CONTRACT (`NuevaMenteOutput` y submodelos — el contrato de Fase 6) |
| `assembler.py` | CONTRACT (firma `assemble_output`) |

## backend/src/storage/
| Archivo | Clasificación |
| --- | --- |
| `base.py` | CONTRACT (`Protocol StorageClient`, `StorageResult`) |
| `oci_config.py` | CONTRACT (firma `load_oci_config`) |
| `oci_client.py` | PLACEHOLDER (clase declarada, métodos `...`, comentario TODO explícito) |
| `mock_client.py` | PLACEHOLDER (ídem, modo mock) |
| `upload.py` | CONTRACT (firmas `upload_original`, `upload_result_json`) |
| `verify.py` | CONTRACT (firma `verify_upload`) |

## backend/src/db/
| Archivo | Clasificación |
| --- | --- |
| `models.py` | CONTRACT (`Job`, `JobStatus`) |
| `session.py` | CONTRACT (firmas `create_job`, `update_job_status`, `get_job`) |

## backend/src/api/
| Archivo | Clasificación |
| --- | --- |
| `schemas.py` | CONTRACT (schemas HTTP de Fase 6) |
| `orchestrator.py` | CONTRACT (clase `PipelineOrchestrator`) |
| `main.py` | CONTRACT (declaración de rutas FastAPI, handlers con cuerpo `...`) |

## ui/
| Archivo | Clasificación |
| --- | --- |
| `app.py` | CONTRACT (firma `main`) |
| `api_client.py` | CONTRACT (firmas `ingest`, `request_adapt`, `poll_adapt_result`) |
| `components/*.py` (5 archivos) | CONTRACT (firma `render` por pantalla) |

## backend/tests/
| Archivo | Clasificación |
| --- | --- |
| `TESTING_STRATEGY.md` | DOCUMENTATION |
| `unit/.gitkeep`, `integration/.gitkeep`, `fixtures/.gitkeep` | PLACEHOLDER (directorio vacío, sin `def test_...`) |

## Configuración

| Archivo | Clasificación |
| --- | --- |
| `.env.example` | CONFIGURATION |
| `.gitignore` | CONFIGURATION |
| `backend/requirements.txt` | CONFIGURATION |
| `backend/pyproject.toml` | CONFIGURATION |
| `.github/workflows/ci.yml` | CONFIGURATION (valida forma del contrato, no ejecuta lógica de negocio) |
| `demo.sh` | PLACEHOLDER (solo `echo` de pasos previstos, ninguna llamada real) |

## Documentación

| Archivo | Clasificación |
| --- | --- |
| `README.md` | DOCUMENTATION |
| `CONTRIBUTING.md` | DOCUMENTATION |
| `docs/architecture.md` | DOCUMENTATION |
| `docs/TRACEABILITY.md` | DOCUMENTATION |
| `docs/AUDIT.md` (este archivo) | DOCUMENTATION |
| `docs/diagrams/pipeline.mmd` | DOCUMENTATION |
| `docs/demo-scenarios/*.md` (3 archivos) | DOCUMENTATION |
| `docs-git/GIT_GITHUB_GUIDE.md` | DOCUMENTATION |
| `n8n-workflows/README.md` | DOCUMENTATION |
| `backend/src/generation/prompts/README.md` | DOCUMENTATION |

## Verificación de la regla fundamental

- **68 archivos `.py`** bajo `backend/src/` y `ui/` (ver conteo en la raíz
  del repositorio) — todos compilan (`py_compile`, sin errores de
  sintaxis) y ninguno contiene una llamada real a un SDK externo, una
  consulta SQL, un `fetch`/`requests` de red, ni un cuerpo de función con
  más de una declaración de tipo `Protocol`/`BaseModel` o un `...`.
- Los únicos archivos con contenido "ejecutable" en sentido estricto son
  `demo.sh` (solo `echo`) y `.github/workflows/ci.yml` (lint + import
  check + `pytest --collect-only`, que recolecta 0 tests por diseño).
- No se creó ningún commit ni se ejecutó ningún comando Git durante la
  construcción de este repositorio.
