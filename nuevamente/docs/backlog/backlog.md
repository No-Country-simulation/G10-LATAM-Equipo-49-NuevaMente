# Backlog

## Resumen de avance por sprint

| Sprint | Tareas | Hecho | Implementada, pendiente de pruebas | En progreso | Pendiente | Críticas abiertas |
|---|---|---|---|---|---|---|
| Sprint 0 - Arranque | 1 | 1 | 0 | 0 | 0 | 0 |
| Sprint 1 - Foundation e ingesta | 2 | 2 | 0 | 0 | 0 | 0 |
| Sprint 2 - RAG y generación | 1 | 1 | 0 | 0 | 0 | 0 |
| Sprint 3 - Pruebas del backend, validación y OCI | 49 | 0 | 25 | 19 | 5 | 28 |
| Sprint 4 - Vertical Slice | 10 | 0 | 0 | 0 | 10 | 7 |
| Sprint 5 - Demo | 7 | 0 | 0 | 0 | 7 | 4 |
| Sin planificar | 9 | 0 | 0 | 0 | 9 | 0 |

## [EPIC-01](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/18) · Foundation y seguridad

Setup del repositorio, configuración, logging, calidad de código y seguridad de secretos.

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| - | [PREP-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/19) Confirmar proveedor de LLM/embeddings (Gemini) | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 0 - Arranque) | Scrum Lead | ✔ | - |
| - | [PREP-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/20) Confirmar responsables de Data/RAG, AI/LLM y Validación/Output | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 0 - Arranque) | Scrum Lead |  | - |
| - | [PREP-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/21) Obtener accesos OCI (Always Free) y API key de Gemini | Hecho | MUST | XS | Sprint 0 - Arranque | Cloud/OCI | ✔ | - |
| - | [FND-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/22) Crear estructura de carpetas src/, tests/, docs/ | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Foundation | ✔ | - |
| - | [FND-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/23) Configurar pyproject.toml/requirements.txt | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Foundation | ✔ | FND-001 |
| - | [FND-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/24) Configurar .env.example y loader de settings (pydantic-settings) | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Foundation | ✔ | FND-001 |
| - | [FND-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/25) Configurar logging estructurado (structlog/logging) | Pendiente | SHOULD | XS | Sin planificar (planificada en Sprint 1 - Foundation e ingesta) | Foundation |  | FND-001 |
| - | [FND-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/26) Configurar linter/formatter (ruff/black) + pre-commit | Pendiente | SHOULD | XS | Sin planificar (planificada en Sprint 1 - Foundation e ingesta) | Foundation |  | FND-002 |
| - | [SEC-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/27) Auditar repo: sin API keys/secrets hardcodeados | Pendiente | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Foundation |  | FND-003 |

## [EPIC-02](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/28) · Ingesta de documentos

Recepción, validación y extracción de texto de PDF, Markdown y TXT (COMP-01).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [BE-ING-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/30) Detectar tipo de archivo y enrutar a extractor | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta | ✔ | FND-001 |
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [BE-ING-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/31) Extraer texto de PDF | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta | ✔ | BE-ING-001 |
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [BE-ING-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/32) Extraer/normalizar texto de Markdown | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta | ✔ | BE-ING-001 |
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [BE-ING-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/33) Extraer/normalizar texto plano | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta | ✔ | BE-ING-001 |
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [ING-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/34) Validar tamaño máximo de archivo (DT-12: 10 MB) | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta |  | BE-ING-001 |
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [ING-006](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/35) Manejo de error: archivo inválido/corrupto | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta |  | BE-ING-002 |
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [ING-007](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/36) Manejo de error: PDF sin texto (escaneado) | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta |  | BE-ING-002 |
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [ING-008](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/37) Manejo de error: Markdown vacío | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta |  | BE-ING-003 |
| [US-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/29) | [ING-009](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/38) Manejo de error: texto vacío | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Ingesta |  | BE-ING-004 |

## [EPIC-03](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/39) · Procesamiento y chunking

Limpieza de texto y división en chunks con metadata de posición/sección (COMP-02).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| [US-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/40) | [BE-PROC-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/41) Definir estructura DocumentChunk | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Processing | ✔ | FND-001 |
| [US-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/40) | [PROC-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/42) Limpieza de texto (espacios, caracteres de control, encabezados repetidos) | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Processing | ✔ | BE-ING-002, BE-ING-003, BE-ING-004 |
| [US-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/40) | [BE-PROC-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/43) Implementar chunking | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Processing | ✔ | BE-PROC-001, PROC-003 |
| [US-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/40) | [PROC-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/44) Metadata de sección/posición en chunk | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Processing |  | BE-PROC-002 |
| [US-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/40) | [PROC-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/45) Manejo de error: documento demasiado grande | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Processing |  | PROC-003 |

## [EPIC-04](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/46) · Embeddings y Vector Store

Generación de embeddings vía proveedor configurable y persistencia en ChromaDB (COMP-03, COMP-04).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| - | [BE-RAG-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/47) Integrar embedding provider (interfaz + Gemini) | En progreso | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG | ✔ | FND-001, PREP-001 |
| - | [BE-RAG-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/48) Generar embeddings para chunks | En progreso | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG | ✔ | BE-PROC-002, BE-RAG-004 |
| - | [OUT-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/49) Manejo de error: fallo de generación de embeddings | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG |  | BE-RAG-005 |
| - | [BE-RAG-006](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/50) Crear e inicializar Vector Store (ChromaDB) | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG | ✔ | FND-001 |
| - | [OUT-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/51) Manejo de error: Vector Store no disponible | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG |  | BE-RAG-006 |
| - | [BE-RAG-007](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/52) Persistir embeddings en Vector Store | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG | ✔ | BE-RAG-005, BE-RAG-006 |

## [EPIC-05](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/53) · RAG / Retrieval

Búsqueda semántica y construcción del contexto para el LLM (COMP-05).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| [US-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/54) | [BE-RAG-008](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/55) Implementar similarity search | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG | ✔ | BE-RAG-007 |
| [US-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/54) | [BE-RAG-009](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/56) Construir retrieval service | En progreso | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG | ✔ | BE-RAG-008, BE-RAG-004 |
| [US-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/54) | [BE-RAG-010](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/57) Construir contexto para el LLM | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG | ✔ | BE-RAG-009 |
| [US-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/54) | [BE-RAG-011](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/58) Manejo de ausencia de contexto relevante (NO_CONTEXT) | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend RAG | ✔ | BE-RAG-009 |

## [EPIC-06](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/59) · Generación adaptada

Generación de contenido educativo por perfil, formato, nicho y nivel de detalle (COMP-06).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| [US-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/60) | [GEN-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/61) Prompt templates por perfil (4 perfiles) | Implementada, pendiente de pruebas | MUST | M | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend Generación | ✔ | BE-RAG-010 |
| [US-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/60) | [GEN-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/62) Prompt templates por formato (>=2 formatos MVP) | Implementada, pendiente de pruebas | MUST | M | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend Generación | ✔ | BE-RAG-010 |
| [US-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/60) | [BE-GEN-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/63) Orquestar generación adaptada | Implementada, pendiente de pruebas | MUST | M | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend Generación | ✔ | BE-RAG-010, BE-RAG-011, GEN-001, GEN-002 |
| [US-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/60) | [GEN-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/64) Adaptación por nicho/contexto | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend Generación |  | BE-GEN-003 |
| [US-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/60) | [GEN-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/65) Control de nivel de detalle (breve/estándar/profundo) | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 2 - RAG y generación) | Backend Generación |  | BE-GEN-003 |
| [US-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/60) | [GEN-006](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/66) Prompt templates de los 3 formatos restantes | Pendiente | SHOULD | M | Sin planificar (planificada en Sprint 2 - RAG y generación) | Backend Generación |  | GEN-002 |
| [US-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/60) | [GEN-007](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/67) Prompt templates de los perfiles restantes (si no cubiertos) | Pendiente | SHOULD | S | Sin planificar (planificada en Sprint 2 - RAG y generación) | Backend Generación |  | GEN-001 |
| - | [DIF-Q-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/68) Quiz interactivo con corrección en tiempo real | Pendiente | COULD | L | Sin planificar | - |  | GEN-002 |
| - | [DIF-AGT-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/69) Migrar orquestación a LangGraph multi-agente (Investigador/Redactor/Crítico) | Pendiente | COULD | XL | Sin planificar | - |  | BE-GEN-003 |

## [EPIC-07](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/70) · Validación de fidelidad y evaluación pedagógica

Extracción de claims, verificación contra la fuente, score de fidelidad y metadatos educativos (COMP-07).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| [US-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/71) | [VAL-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/72) Extracción de claims generados (formato JSON) | En progreso | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI | Backend Validación | ✔ | BE-GEN-003 |
| [US-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/71) | [BE-VAL-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/73) Verificar claims contra fuente (score de fidelidad) | En progreso | MUST | M | Sprint 3 - Pruebas del backend, validación y OCI | Backend Validación | ✔ | BE-GEN-003, VAL-001 |
| [US-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/71) | [VAL-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/74) Manejo de error: fallo del LLM-juez en validación | Pendiente | MUST | XS | Sprint 4 - Vertical Slice (planificada en Sprint 3 - Pruebas del backend, validación y OCI) | Backend Validación |  | BE-VAL-002 |
| - | [VAL-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/75) Evaluación pedagógica: conceptos clave, prerrequisitos | Pendiente | MUST | S | Sprint 4 - Vertical Slice (planificada en Sprint 3 - Pruebas del backend, validación y OCI) | Backend Validación |  | BE-GEN-003 |
| - | [VAL-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/76) Evaluación pedagógica: tiempo estimado, dificultad, claridad | Pendiente | MUST | S | Sprint 4 - Vertical Slice (planificada en Sprint 3 - Pruebas del backend, validación y OCI) | Backend Validación |  | VAL-003 |

## [EPIC-08](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/77) · Salida JSON estructurada

Schema Pydantic formal y ensamblado del JSON final (COMP-08).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| [US-006](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/78) | [BE-OUT-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/79) Definir schema Pydantic de salida (NuevaMenteOutput) | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Backend Output |  | FND-001 |
| [US-006](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/78) | [BE-OUT-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/80) Ensamblar JSON final del pipeline | Pendiente | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI | Backend Output | ✔ | BE-OUT-002, BE-VAL-002, BE-GEN-003 |
| - | [DIF-EXP-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/81) Exportación a Markdown | Pendiente | COULD | S | Sin planificar | - |  | BE-OUT-003 |
| - | [DIF-EXP-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/82) Exportación a PDF | Pendiente | COULD | M | Sin planificar | - |  | BE-OUT-003 |
| - | [DIF-EXP-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/83) Exportación a CSV/Anki (flashcards) | Pendiente | COULD | S | Sin planificar | - |  | BE-OUT-003 |

## [EPIC-09](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/84) · Persistencia en OCI Object Storage

Cliente OCI, subida de originales y resultados, naming convention y verificación (COMP-09).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| [US-007](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/85) | [OCI-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/86) Configurar credenciales OCI de forma segura | Hecho | MUST | S | Sprint 1 - Foundation e ingesta | Cloud/OCI |  | FND-001, PREP-003 |
| [US-007](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/85) | [OCI-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/87) Crear cliente OCI y bucket (Always Free) | Hecho | MUST | S | Sprint 2 - RAG y generación | Cloud/OCI |  | OCI-001 |
| [US-007](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/85) | [OCI-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/88) Naming convention y subida de documento original | En progreso | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI | Cloud/OCI |  | OCI-002 |
| [US-007](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/85) | [OCI-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/89) Subir JSON generado y verificar upload | En progreso | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI | Cloud/OCI |  | OCI-002, BE-OUT-003 |

## [EPIC-10](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/90) · Interfaz web y API

Contrato REST, endpoints reales y UI Streamlit (COMP-10, COMP-11).

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| [US-008](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/91) | [FE-API-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/92) Contrato REST mockeado (/ingest, /adapt) | Implementada, pendiente de pruebas | MUST | XS | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 1 - Foundation e ingesta) | Orquestación/API | ✔ | FND-001 |
| [US-008](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/91) | [UX-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/93) Prototipo/mockups de las 5 pantallas de Streamlit (upload, selección, loading, resultado, error) | Hecho | MUST | S | Sprint 1 - Foundation e ingesta | UX/UI |  | FND-001 |
| [US-008](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/91) | [FE-UI-003](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/94) Versión ligera de la app Streamlit (sin estilos) | Implementada, pendiente de pruebas | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI | UX/UI |  | FE-API-001 |
| [US-008](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/91) | [FE-UI-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/95) Aplicar a Streamlit el diseño del prototipo aprobado | En progreso | MUST | M | Sprint 3 - Pruebas del backend, validación y OCI | UX/UI |  | UX-001, FE-UI-003 |
| [US-008](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/91) | FE-API-002 Conectar endpoints reales al pipeline completo | Pendiente | MUST | M | Sprint 4 - Vertical Slice | Orquestación/API | ✔ | FE-API-001, BE-OUT-003, OCI-005 |
| [US-008](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/91) | [FE-UI-005](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/96) UI Streamlit: flujo completo conectado | Pendiente | MUST | M | Sprint 4 - Vertical Slice | UX/UI | ✔ | FE-API-002, FE-UI-004 |

## [EPIC-11](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/97) · Testing y calidad

Tests unitarios, de integración, golden test de fidelidad y alineación a los requisitos del challenge.

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| - | QA-005 Tests unitarios de retrieval y generación (con LLM mock) | Pendiente | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI | QA | ✔ | BE-RAG-011, BE-GEN-003 |
| - | [QA-006](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/98) Alinear el backend terminado a los requisitos del challenge Alura | En progreso | MUST | M | Sprint 3 - Pruebas del backend, validación y OCI | Foundation | ✔ | BE-GEN-003, BE-OUT-002 |
| - | QA-001 Tests unitarios de ingestion (PDF/MD/TXT) | Pendiente | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 5 - Demo) | QA |  | BE-ING-002, BE-ING-003, BE-ING-004 |
| - | QA-002 Tests unitarios chunking + embeddings | Pendiente | MUST | S | Sprint 3 - Pruebas del backend, validación y OCI (planificada en Sprint 5 - Demo) | QA |  | BE-RAG-005 |
| - | QA-003 Tests de integración del pipeline completo (vertical slice) | Pendiente | MUST | M | Sprint 4 - Vertical Slice | QA | ✔ | FE-API-002 |
| - | QA-004 Test de fidelidad con documento conocido (golden test) | Pendiente | SHOULD | S | Sprint 5 - Demo | QA |  | BE-VAL-002 |

## [EPIC-12](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/99) · Integración (reemplazo de mocks)

Sustituir los mocks de LLM, embeddings y OCI por integraciones reales; capa n8n opcional.

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| - | INT-001 Reemplazar mock de LLM por integración real | Pendiente | MUST | S | Sprint 4 - Vertical Slice | Orquestación/API | ✔ | BE-GEN-003 |
| - | INT-002 Reemplazar mock de embeddings por integración real | Pendiente | MUST | S | Sprint 4 - Vertical Slice | Orquestación/API | ✔ | BE-RAG-004 |
| - | INT-003 Reemplazar mock de OCI upload por integración real | Pendiente | MUST | S | Sprint 4 - Vertical Slice | Orquestación/API | ✔ | OCI-002 |
| - | [INT-004](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/100) Conectar webhook n8n -> FastAPI /adapt real + nodo IF con umbral DT-11 | En progreso | COULD | S | Sprint 3 - Pruebas del backend, validación y OCI | n8n |  | FE-API-002, BE-VAL-002 |

## [EPIC-13](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/101) · Demo y documentación

Tres escenarios de demo reproducibles, README y documento de arquitectura.

| Historia | Tarea | Estado | Prioridad | Est. | Sprint | Rol | Crit | Depende de |
|---|---|---|---|---|---|---|---|---|
| US-009 | DEMO-000 Seleccionar/preparar los 3 documentos técnicos de referencia | Pendiente | MUST | S | Sprint 4 - Vertical Slice (planificada en Sprint 5 - Demo) | QA | ✔ | - |
| US-009 | DEMO-001 Preparar escenario de demo 1 (perfil principiante) | Pendiente | MUST | S | Sprint 5 - Demo | QA | ✔ | QA-003, DEMO-000 |
| US-009 | DEMO-002 Preparar escenario de demo 2 (perfil líder técnico) | Pendiente | MUST | S | Sprint 5 - Demo | QA | ✔ | QA-003 |
| US-009 | DEMO-003 Preparar escenario de demo 3 (formato distinto, ej. quiz o resumen) | Pendiente | MUST | S | Sprint 5 - Demo | QA | ✔ | QA-003 |
| [US-010](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/102) | [SEC-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/103) Documentar configuración segura en README | Pendiente | MUST | XS | Sprint 5 - Demo | Foundation |  | SEC-001 |
| [US-010](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/102) | [DOC-001](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/104) Escribir README (setup, uso, arquitectura resumida) | Pendiente | MUST | S | Sprint 5 - Demo | Foundation | ✔ | DEMO-003 |
| [US-010](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/102) | [DOC-002](https://github.com/No-Country-simulation/G10-LATAM-Equipo-49-NuevaMente/issues/105) Documento de arquitectura (diagrama + descripción de capas) | Pendiente | MUST | S | Sprint 5 - Demo | Foundation |  | DOC-001 |
