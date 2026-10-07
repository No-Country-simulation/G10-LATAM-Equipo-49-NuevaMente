# Matriz de trazabilidad

| Requisitos | Historia | Casos de uso | Componentes | Tareas |
|---|---|---|---|---|
| REQ-01, REQ-02, REQ-03, REQ-04 | US-001 Ingesta de documento técnico (PDF/MD/TXT) | CU-001 | COMP-01 | BE-ING-001, BE-ING-002, BE-ING-003, BE-ING-004, ING-005, ING-006, ING-007, ING-008, ING-009 |
| REQ-05 | US-002 Chunking con metadata | CU-001 | COMP-02 | BE-PROC-001, PROC-003, BE-PROC-002, PROC-004, PROC-005 |
| REQ-08 | US-003 Retrieval semántico | CU-001, CU-002 | COMP-05 | BE-RAG-008, BE-RAG-009, BE-RAG-010, BE-RAG-011 |
| REQ-09, REQ-10, REQ-11, REQ-12, REQ-13, REQ-24 | US-004 Adaptación pedagógica | CU-001, CU-002 | COMP-06 | GEN-001, GEN-002, BE-GEN-003, GEN-004, GEN-005, GEN-006, GEN-007 |
| REQ-14 | US-005 Validación de fidelidad | CU-001, CU-003 | COMP-07 | VAL-001, BE-VAL-002, VAL-005 |
| REQ-16 | US-006 JSON estructurado | CU-001 | COMP-08 | BE-OUT-002, BE-OUT-003 |
| REQ-18, REQ-19, REQ-20 | US-007 Persistencia OCI | CU-001 | COMP-09 | OCI-001, OCI-002, OCI-003, OCI-005 |
| REQ-17 | US-008 Interfaz funcional | CU-001, CU-002, CU-003 | COMP-10, COMP-11 | FE-API-001, UX-001, FE-UI-003, FE-UI-004, FE-API-002, FE-UI-005 |
| REQ-21 | US-009 Escenarios de demo | CU-001, CU-002 | - | DEMO-000, DEMO-001, DEMO-002, DEMO-003 |
| REQ-22, REQ-23 | US-010 Documentación | - | - | SEC-002, DOC-001, DOC-002 |
| REQ-06, REQ-09 | _(tarea técnica)_ | - | - | PREP-001 |
| REQ-18 | _(tarea técnica)_ | - | - | PREP-003 |
| RNF-001 | _(tarea técnica)_ | - | - | FND-003 |
| RNF-003 | _(tarea técnica)_ | - | - | FND-004 |
| RNF-001 | _(tarea técnica)_ | - | - | SEC-001 |
| REQ-06 | _(tarea técnica)_ | - | COMP-03 | BE-RAG-004 |
| REQ-06 | _(tarea técnica)_ | - | COMP-03 | BE-RAG-005 |
| REQ-06 | _(tarea técnica)_ | - | COMP-03 | OUT-004 |
| REQ-07 | _(tarea técnica)_ | - | COMP-04 | BE-RAG-006 |
| REQ-07 | _(tarea técnica)_ | - | COMP-04 | OUT-005 |
| REQ-07 | _(tarea técnica)_ | - | COMP-04 | BE-RAG-007 |
| DIF-06 | _(tarea técnica)_ | - | COMP-06 | DIF-Q-001 |
| DIF-02, DIF-03, DIF-04, DIF-05 | _(tarea técnica)_ | - | COMP-06 | DIF-AGT-001 |
| REQ-15 | _(tarea técnica)_ | - | COMP-07 | VAL-003 |
| REQ-15 | _(tarea técnica)_ | - | COMP-07 | VAL-004 |
| DIF-10 | _(tarea técnica)_ | - | COMP-08 | DIF-EXP-001 |
| DIF-09 | _(tarea técnica)_ | - | COMP-08 | DIF-EXP-002 |
| DIF-11 | _(tarea técnica)_ | - | COMP-08 | DIF-EXP-003 |
| REQ-08, REQ-09, REQ-10, REQ-11 | _(tarea técnica)_ | - | COMP-05, COMP-06 | QA-005 |
| REQ-16, REQ-17, REQ-24 | _(tarea técnica)_ | - | - | QA-006 |
| REQ-14 | _(tarea técnica)_ | - | COMP-07 | QA-004 |

## Requisitos sin tareas asociadas
- DIF-01 OCI Compute
- DIF-07 Soporte multimodal
- DIF-08 Interpretación de diagramas
- RNF-002 Disponibilidad durante la ventana de demo
- RNF-004 Privacidad: datos solo en el bucket OCI del equipo
- RNF-005 Mantenibilidad: capas independientes y proveedor intercambiable
- RNF-006 Trazabilidad: document_id, chunk_id, posición, página
- RNF-007 Costos: solo capa gratuita
- RNF-008 Rendimiento orientativo < 60 s por generación
