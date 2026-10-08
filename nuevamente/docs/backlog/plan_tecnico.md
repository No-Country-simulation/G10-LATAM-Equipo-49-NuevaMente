# Plan técnico · NuevaMente

## Objetivo
Product Goal: construir una aplicación funcional que transforme documentación técnica (PDF/Markdown/TXT) en contenido educativo personalizado, utilizando RAG y un LLM, manteniendo trazabilidad hacia las fuentes originales y almacenando documentos y resultados en OCI Object Storage. Usuario del MVP: instructor, especialista técnico o diseñador instruccional.

## Arquitectura
Monolito backend en FastAPI (ingestion, processing, embeddings, vector store, RAG, generation, validation, output, storage) con ChromaDB embebido y SQLite para estado de sesión. Interfaz web en Streamlit que consume la API REST por HTTP. Servicios externos: Gemini API (LLM + embeddings) y OCI Object Storage (Always Free). Flujo: Ingesta -> Extracción -> Chunking -> Embeddings -> Vector Store -> Retrieval -> Generación -> Validación de fidelidad -> JSON (Pydantic) -> Persistencia OCI.

## Stack tecnológico
| Capa | Tecnología |
|---|---|
| Lenguaje | Python |
| API | FastAPI + Pydantic v2 |
| Interfaz web | Streamlit |
| Vector store | ChromaDB embebido |
| Chunking | LangChain RecursiveCharacterTextSplitter |
| Extracción PDF | PyPDF (fallback pdfplumber) |
| LLM y embeddings | Google Gemini API free tier (PENDIENTE DE CONFIRMAR) |
| Estado de sesión | SQLite local |
| Almacenamiento | OCI Object Storage (Always Free) |
| Orquestación externa (opcional) | n8n self-hosted |

## Sprints
| Sprint | Inicio | Fin | Objetivo |
|---|---|---|---|
| Sprint 0 - Arranque | 2026-09-14 | 2026-09-18 | Organización y presentación del equipo; confirmar proveedor LLM y accesos |
| Sprint 1 - Foundation e ingesta | 2026-09-21 | 2026-09-25 | Repo funcional, .env, ingesta PDF/MD/TXT probada, /adapt mockeado, mockups UI |
| Sprint 2 - RAG y generación | 2026-09-28 | 2026-10-02 | Embeddings + retrieval + generación de contenido real por perfil/formato |
| Sprint 3 - Pruebas del backend, validación y OCI | 2026-10-05 | 2026-10-09 | Ciclo de pruebas del backend (cerrar S1-S2), score de fidelidad, OCI |
| Sprint 4 - Vertical Slice | 2026-10-12 | 2026-10-16 | UI conectada sin mocks, integración end-to-end |
| Sprint 5 - Demo | 2026-10-19 | 2026-10-23 | Pruebas finales, 3 escenarios de demo, README. Sin diferenciales salvo que sobre tiempo |

## Requisitos
| Código | Requisito | Clase |
|---|---|---|
| REQ-01 | Ingesta de PDF | Obligatorio |
| REQ-02 | Ingesta de Markdown | Obligatorio |
| REQ-03 | Ingesta de texto plano | Obligatorio |
| REQ-04 | Extracción de contenido | Obligatorio |
| REQ-05 | Chunking | Obligatorio |
| REQ-06 | Embeddings | Obligatorio |
| REQ-07 | Vector Store | Obligatorio |
| REQ-08 | Retrieval / RAG | Obligatorio |
| REQ-09 | LLM de generación | Obligatorio |
| REQ-10 | Adaptación por perfil | Obligatorio |
| REQ-11 | Adaptación por formato pedagógico | Obligatorio |
| REQ-12 | Adaptación por nicho/contexto | Obligatorio |
| REQ-13 | Nivel de detalle configurable | Obligatorio |
| REQ-14 | Validación de fidelidad | Obligatorio |
| REQ-15 | Metadatos educativos | Obligatorio |
| REQ-16 | JSON estructurado (schema formal) | Obligatorio |
| REQ-17 | Interfaz o API funcional | Obligatorio |
| REQ-18 | OCI Object Storage (Always Free) | Obligatorio |
| REQ-19 | Persistencia de documentos originales | Obligatorio |
| REQ-20 | Persistencia de contenido generado | Obligatorio |
| REQ-21 | Tres escenarios de demostración | Obligatorio |
| REQ-22 | README | Obligatorio |
| REQ-23 | Arquitectura documentada | Obligatorio |
| REQ-24 | Al menos 2 formatos pedagógicos distintos en el MVP | Obligatorio |
| DIF-01 | OCI Compute | Diferencial |
| DIF-02 | Multi-Agent con LangGraph | Diferencial |
| DIF-03 | Agente Investigador RAG | Diferencial |
| DIF-04 | Agente Redactor Pedagógico | Diferencial |
| DIF-05 | Agente Crítico/Revisor | Diferencial |
| DIF-06 | Quiz interactivo con evaluación en tiempo real | Diferencial |
| DIF-07 | Soporte multimodal | Diferencial |
| DIF-08 | Interpretación de diagramas | Diferencial |
| DIF-09 | Exportación PDF | Diferencial |
| DIF-10 | Exportación Markdown | Diferencial |
| DIF-11 | Exportación CSV/Anki | Diferencial |
| RNF-001 | Seguridad: sin secretos en el código (.env + .env.example) | No funcional |
| RNF-002 | Disponibilidad durante la ventana de demo | No funcional |
| RNF-003 | Observabilidad: logs estructurados por etapa | No funcional |
| RNF-004 | Privacidad: datos solo en el bucket OCI del equipo | No funcional |
| RNF-005 | Mantenibilidad: capas independientes y proveedor intercambiable | No funcional |
| RNF-006 | Trazabilidad: document_id, chunk_id, posición, página | No funcional |
| RNF-007 | Costos: solo capa gratuita | No funcional |
| RNF-008 | Rendimiento orientativo < 60 s por generación | No funcional |

## Decisiones técnicas
| Código | Decisión | Relacionado |
|---|---|---|
| DT-01 | Stack: Python + FastAPI (API) + Streamlit (UI de demo) | REQ-17 |
| DT-02 | Vector Store: ChromaDB embebido (sin servidor externo) | REQ-07 |
| DT-03 | Chunking: RecursiveCharacterTextSplitter con overlap configurable | REQ-05 |
| DT-04 | Extracción PDF: PyPDF (fallback pdfplumber) | REQ-01 |
| DT-05 | Fidelidad: LLM como juez + scoring heurístico de solapamiento léxico | REQ-14 |
| DT-06 | Esquema de salida: Pydantic v2 | REQ-16 |
| DT-07 | Naming en OCI: {tipo}/{doc_id}/{timestamp}_{nombre} | REQ-18 |
| DT-08 | Estado de sesión en SQLite local (documentos/jobs) | REQ-19, REQ-20 |
| DT-09 | LLM + embeddings: Google Gemini API free tier (PENDIENTE DE CONFIRMAR) | REQ-06, REQ-09 |
| DT-10 | n8n self-hosted como wrapper opcional sobre /adapt | REQ-17 |
| DT-11 | Umbral de fidelidad score >= 0.9, configurable por .env | REQ-14 |
| DT-12 | Tamaño máximo de archivo 10 MB, configurable (SUPUESTO: no estaba en la tabla de DT) | REQ-01 |

## Criterios de éxito del MVP
| Prueba | Acción | Resultado esperado |
|---|---|---|
| 1 - Ingesta | Cargar un documento PDF, Markdown o TXT | Queda almacenado en OCI y recibe un document_id |
| 2 - Recuperación | Consulta relacionada con el documento | Recupera fragmentos relevantes y genera respuesta fundamentada |
| 3 - Personalización | Principiante / Fintech / Tutorial | Tutorial adaptado a ese perfil y contexto |
| 4 - Cambio de audiencia | Mismo documento, Ejecutivo / Fintech / Resumen | Resultado diferente, adaptado a la nueva audiencia |
| 5 - Trazabilidad | - | El resultado identifica las fuentes (sources: chunk_id, page) |
| 6 - JSON | - | El usuario puede descargar el resultado como JSON |
| 7 - Persistencia | - | El resultado queda almacenado en OCI Object Storage |
| 8 - Fidelidad | - | El JSON muestra fidelidad_score y claims_no_soportados |

## Equipo
| Rol | Persona | GitHub | Nota |
|---|---|---|---|
| Scrum Lead | Diana Ocaña Martínez | @didiocma | Asume 2 roles: Scrum Lead + todo el backend |
| Foundation | Osvaldo Acosta | @teamdev202594-spec | Alinea el backend y app ui terminado a los requisitos de Alura |
| Backend Ingesta | Diana Ocaña Martínez | @didiocma |  |
| Backend Processing | Diana Ocaña Martínez | @didiocma |  |
| Backend RAG | Pedro Orozco | @PedrOroz | Antes Miguel Ángel |
| Backend Generación | Pedro Orozco | @PedrOroz | Antes Fernando |
| Backend Validación | Pedro Orozco | @PedrOroz |  |
| Backend Output | Diana Ocaña Martínez | @didiocma |  |
| Cloud/OCI | Pedro Orozco | @PedrOroz |  |
| n8n | Rodrigo Reyes | @Roro0404 | Orquestador n8n (INT-004) |
| Orquestación/API | SIN ASIGNAR | - | Endpoints reales e integración (FE-API-002, INT-001..003). Decidir en la reunión |
| UX/UI | Viviana Hurtado y Santiago | @vivihv013, @sagp3 | Prototipo aprobado; aplicando el diseño a Streamlit |
| QA | SIN ASIGNAR | - | Decidir en la reunión quién prueba o como se reparten las pruebas |

## Definición de hecho
- [ ] Código implementado
- [ ] Código compila / se ejecuta sin errores
- [ ] No existen errores críticos conocidos
- [ ] Tests creados
- [ ] Tests ejecutados y en verde
- [ ] Documentación actualizada (docstring o README, si aplica)
- [ ] Variables de entorno nuevas documentadas en .env.example
- [ ] Evidencia entregada (output de pytest o captura de la interfaz)
- [ ] Criterios de aceptación de la tarea cumplidos
- [ ] Integrado a la rama principal sin romper otros módulos

## Riesgos
| Riesgo | Impacto | Mitigación |
|---|---|---|
| Proveedor de LLM/embeddings no confirmado | Bloqueante | Interfaz LLMProvider/EmbeddingProvider con mock intercambiable por flag; tarea PREP-001 |
| PDFs escaneados sin texto | Medio | Advertencia explícita, sin crash (ING-007) |
| Ausencia de contexto relevante provoca alucinaciones | Alto | Retornar NO_CONTEXT en vez de generar (BE-RAG-011) |
| Fallo del LLM-juez en la validación | Medio | score=null + advertencia, sin bloquear la entrega (VAL-005) |
| Fallo de red hacia OCI | Medio | Verificación post-upload y status PARTIAL (OCI-005) |
| Latencia del LLM en la demo en vivo | Medio | Guía de diseño < 60 s; timeout 30 s y 1 reintento |
| Roles Data/RAG y AI/LLM por confirmar | Importante | Supuesto provisional en equipo.yaml; tarea PREP-002 |

