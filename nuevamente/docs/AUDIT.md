# Auditoría de estado de implementación

Generada automáticamente a partir del código (`ast`): un archivo es **IMPLEMENTADO** si contiene
funciones con lógica real o solo modelos/constantes sin firmas vacías; es **CONTRATO (pendiente)**
si todas sus funciones tienen cuerpo `...`. Reflejo del estado actual del repositorio.

**Resumen:** 37 de 58 archivos Python implementados; el resto son contratos de Semana 2 en adelante
(RAG, embeddings, vector store, LLM, validación de fidelidad, ensamblado final).

> Este archivo debe regenerarse al cerrar cada semana; no editar a mano.

## api/
| Archivo | Estado |
| --- | --- |
| `main.py` | IMPLEMENTADO |
| `orchestrator.py` | IMPLEMENTADO |
| `schemas.py` | IMPLEMENTADO (modelos/constantes) |

## core/
| Archivo | Estado |
| --- | --- |
| `config.py` | IMPLEMENTADO |
| `exceptions.py` | IMPLEMENTADO |
| `logging.py` | IMPLEMENTADO |

## db/
| Archivo | Estado |
| --- | --- |
| `models.py` | IMPLEMENTADO (modelos/constantes) |
| `session.py` | IMPLEMENTADO |

## embeddings/
| Archivo | Estado |
| --- | --- |
| `base.py` | CONTRATO (Protocol, definitivo) |
| `embed_chunks.py` | CONTRATO (pendiente) |
| `factory.py` | CONTRATO (pendiente) |

## embeddings/providers/
| Archivo | Estado |
| --- | --- |
| `gemini.py` | CONTRATO (pendiente) |
| `mock.py` | CONTRATO (pendiente) |

## generation/
| Archivo | Estado |
| --- | --- |
| `llm_provider.py` | CONTRATO (pendiente) |
| `mock_adapter.py` | IMPLEMENTADO |
| `models.py` | IMPLEMENTADO (modelos/constantes) |
| `orchestrator.py` | CONTRATO (pendiente) |
| `profiles.py` | IMPLEMENTADO (modelos/constantes) |

## ingestion/
| Archivo | Estado |
| --- | --- |
| `base.py` | CONTRATO (Protocol, definitivo) |
| `md_extractor.py` | IMPLEMENTADO |
| `models.py` | IMPLEMENTADO (modelos/constantes) |
| `pdf_extractor.py` | IMPLEMENTADO |
| `router.py` | IMPLEMENTADO |
| `text_decoding.py` | IMPLEMENTADO |
| `txt_extractor.py` | IMPLEMENTADO |
| `validators.py` | IMPLEMENTADO |

## output/
| Archivo | Estado |
| --- | --- |
| `assembler.py` | CONTRATO (pendiente) |
| `schema.py` | IMPLEMENTADO |

## processing/
| Archivo | Estado |
| --- | --- |
| `chunking.py` | IMPLEMENTADO |
| `cleaning.py` | IMPLEMENTADO |
| `models.py` | IMPLEMENTADO |

## rag/
| Archivo | Estado |
| --- | --- |
| `base.py` | CONTRATO (Protocol, definitivo) |
| `context_builder.py` | CONTRATO (pendiente) |
| `retrieval_service.py` | CONTRATO (pendiente) |

## storage/
| Archivo | Estado |
| --- | --- |
| `base.py` | CONTRATO (Protocol, definitivo) |
| `factory.py` | IMPLEMENTADO |
| `mock_client.py` | IMPLEMENTADO |
| `naming.py` | IMPLEMENTADO |
| `oci_client.py` | IMPLEMENTADO |
| `oci_config.py` | IMPLEMENTADO |
| `upload.py` | IMPLEMENTADO |
| `verify.py` | IMPLEMENTADO |

## validation/
| Archivo | Estado |
| --- | --- |
| `base.py` | CONTRATO (Protocol, definitivo) |
| `claims_extractor.py` | CONTRATO (pendiente) |
| `fidelity_checker.py` | CONTRATO (pendiente) |
| `models.py` | IMPLEMENTADO (modelos/constantes) |
| `pedagogical_eval.py` | CONTRATO (pendiente) |

## vectorstore/
| Archivo | Estado |
| --- | --- |
| `base.py` | CONTRATO (Protocol, definitivo) |
| `client.py` | CONTRATO (pendiente) |
| `search.py` | CONTRATO (pendiente) |
| `store.py` | CONTRATO (pendiente) |

## ui/
| Archivo | Estado |
| --- | --- |
| `api_client.py` | IMPLEMENTADO |
| `app.py` | IMPLEMENTADO |

## ui/components/
| Archivo | Estado |
| --- | --- |
| `error_view.py` | IMPLEMENTADO |
| `loading_view.py` | IMPLEMENTADO |
| `result_view.py` | IMPLEMENTADO |
| `selection_view.py` | IMPLEMENTADO |
| `upload_view.py` | IMPLEMENTADO |
