# NuevaMente · Informe y Manual Técnico del Backend
**Estado actual, arquitectura y plan de trabajo**
Hackathon ONE · NoCountry × Oracle Cloud Infrastructure · Grupo 10
Versión 0.1 · 17 de septiembre de 2025 · Elaboró: Rodrigo Reyes (Orquestación / Backend / Arquitectura)

> **Nota de uso:** este documento describe una **base de trabajo, no un diseño cerrado**.
> Las secciones marcadas con ✍️ **ESPACIO EQUIPO** están en blanco a propósito:
> son para que cualquier integrante agregue propuestas, correcciones y mejoras.
> Toda decisión aquí escrita puede reabrirse en refinamiento presentando datos.

---

## 1. Resumen ejecutivo

| Pregunta | Respuesta |
|---|---|
| ¿Qué existe hoy? | Backend FastAPI v0.1 con contrato Pydantic congelado y endpoints `/health` y `/adaptar` operativos (motor mock). Orquestador n8n en producción local con control de fidelidad ≥ 0.9. Repo Git en rama `main`. README con arquitectura publicado. |
| ¿Qué nivel es ese? | Vertical slice funcional con motores mock: ~35% del backend MVP, pero **100% del contrato, la validación y la orquestación**. |
| ¿Por qué sirve así? | El contrato está congelado: cada integrante construye su módulo en paralelo y se integra en FASE 8 sin romper nada. |
| ¿Qué falta? | Ingesta real (PDF/MD/TXT), RAG (embeddings + ChromaDB), generación con Gemini, validación LLM-juez, subida real a OCI, interfaz y despliegue en VM. |
| ¿Regla innegociable? | Todo recurso cloud bajo **Oracle Always Free**. |

---

## 2. Arquitectura

```text
┌──────────────────┐  POST /webhook   ┌──────────────────────────┐
│  Interfaz (UI)   │ ───────────────► │  n8n · ORQUESTADOR       │
│  (decisión UX)   │                  │  (VM OCI Always Free)    │
└──────────────────┘                  └─────────────────────────┘
                                                   │ POST /adaptar
                                      ┌────────────▼─────────────┐
                                      │  FastAPI · BACKEND IA    │
                                      │  Pydantic · RAG · Agentes│
                                      └───┬──────────────┬───────┘
                                          │              │
                              ┌───────────▼──────┐  ┌────▼─────────────────┐
                              │ ChromaDB         │  │ OCI Object Storage   │
                              │ (vector store)   │  │ (Always Free)        │
                              └──────────────────┘  └──────────────────────┘
  n8n · nodo IF: score_fidelidad ≥ 0.9 → ✅ Paquete educativo JSON
                 score_fidelidad < 0.9 → ⛔ Rechazo amigable FIDELIDAD_BAJA
```

### 2.1 Capas y responsabilidades

| Capa | Tecnología | Responsabilidad | Estado |
|---|---|---|---|
| Interfaz | Por decidir en refinamiento (Streamlit según DT-01) | Vitrina: perfiles, formatos, JSON, estado OCI | ⏳ FASE 7 |
| Orquestación | n8n self-hosted | Webhook, control de fidelidad, reintentos, bitácora, alertas | ✅ Operativa |
| Núcleo IA | Python · FastAPI · Pydantic | Contrato JSON, RAG, agentes | 🟡 Contrato ✅ / motores mock |
| Conocimiento | ChromaDB + Gemini Embeddings | Chunking, embeddings, retrieval | ⏳ FASE 3 |
| Persistencia | OCI Object Storage | Documento original + JSON generado | ⏳ FASE 6 |

### 2.2 Por qué n8n como orquestador (DT-10)

1. Orquestación de producción sin costo (self-hosted en VM Always Free).
2. Anti-alucinación como política de infraestructura: el nodo IF es una puerta de calidad ejecutable.
3. Auditabilidad nativa: cada corrida queda logueada como evidencia.
4. Manejo de errores de primera clase (reintentos, timeouts, alertas).
5. Separación de responsabilidades: la lógica de IA vive en Python; n8n solo orquesta.
6. Colaboración: los flujos se exportan como JSON al repo (`/n8n-workflows/`).

### 2.3 Compromiso 100% gratuito

| Componente | Servicio | Capa gratuita |
|---|---|---|
| Orquestador n8n | OCI Compute self-hosted | ✅ Always Free |
| Almacenamiento | OCI Object Storage | ✅ Always Free |
| LLM + embeddings | Google Gemini API | ✅ Free tier |
| Vector store | ChromaDB embebido | ✅ Open source |
| Repo y alertas | GitHub / Discord | ✅ Free |

---

## 3. Estado actual del backend (v0.1)

### 3.1 Estructura del repositorio

```text
nuevamente-g10/
├── backend/            # schemas.py (contrato), main.py (motor mock), venv/
├── n8n-workflows/      # nuevamente-v1.json (orquestador versionado)
├── .gitignore          # blinda venv/, .env y secretos
├── .env.example        # plantilla sin secretos
├── demo.sh             # guion de demo ejecutable
└── README.md           # documento base
```

### 3.2 El contrato: `backend/schemas.py` (NO se rompe; se evoluciona por acuerdo)

| Bloque | Qué define | Requisito que cubre |
|---|---|---|
| Enums (perfil, formato, nicho, nivel) | Valores permitidos | REQ-10 a REQ-13 |
| `SolicitudAdaptacion` | Entrada: título, contenido, perfil, formato, nicho, nivel | REQ-17 |
| Items (flashcard, quiz, tutorial, resumen, guion) | Formatos pedagógicos | REQ-11, REQ-24 |
| `Metadatos` / `ContenidoAdaptado` / `EvaluacionCalidad` / `AlmacenamientoOCI` | Bloques de salida | REQ-15, REQ-14, REQ-18 a 20 |
| `PaqueteEducativo` + validador anti-"frankenstein" | Paquete final coherente con el formato declarado | REQ-16 |
| `RespuestaError` | Error amigable + detalle técnico interno | Checklist |

### 3.3 El motor: `backend/main.py` (mocks con reemplazo asignado)

| Función hoy | Qué hace hoy | Qué la reemplaza | Tarea backlog | Perfil sugerido |
|---|---|---|---|---|
| `chunk_text()` | Trocea por oraciones (~400 chars) | `RecursiveCharacterTextSplitter` | BE-PROC-001/002 | Data/RAG |
| `tokens()` + `retrieve()` | Búsqueda por palabras compartidas | Embeddings Gemini + ChromaDB | BE-RAG-004…011 | Data/RAG |
| `INTROS`/`TITULOS`/`BUILDERS` | Plantillas por perfil y formato | Prompts + agente redactor | GEN-001/002, BE-GEN-003 | AI/LLM |
| `anclaje_score()` + `CAMPOS_CONTENIDO` | Fidelidad léxica 0–1 | LLM-juez + heurística | VAL-001, BE-VAL-002 | AI/LLM |
| Bloque `AlmacenamientoOCI` | Subida simulada (`pendiente`) | SDK `oci` real | OCI-002…005, INT-003 | Cloud |
| `/health` y `/adaptar` | Endpoints operativos | Mismo endpoint con motor real | FE-API-002, INT-001…003 | Orquestación |

### 3.4 Capa n8n (workflow `NuevaMente v1`, activo)

| Nodo | Función |
|---|---|
| Webhook `POST /webhook/nuevamente-adaptar` | Entrada de producción |
| HTTP Request | Llama `/adaptar` con el body del webhook |
| IF (score ≥ 0.9) | Puerta de fidelidad (DT-11) |
| Respond (true) | Devuelve el `PaqueteEducativo` |
| Respond (false) | Error amigable `FIDELIDAD_BAJA` |

**Evidencia:** ejecuciones de producción registradas en la bitácora de n8n (éxitos en milisegundos + historial de debugging).

### 3.5 Cómo correrlo local

```bash
cd backend && source venv/bin/activate
uvicorn main:app --reload --port 8000      # Terminal 1 (no se cierra)
curl http://localhost:8000/health          # Terminal 2 (pruebas)
```

---

## 4. Mapeo con el plan del equipo (backlog)

| Tarea backlog | Estado real | Evidencia |
|---|---|---|
| FE-API-001 (contrato mock) | ✅ DONE | `schemas.py` + `/adaptar` mock |
| FE-API-002 (endpoint operativo) | ✅ DONE a nivel mock | Endpoint vivo; swap en FASE 8 |
| INT-004 (n8n + IF fidelidad) | ✅ DONE (planificada COULD semana 5) | Workflow activo + JSON exportado |
| DOC-001 / DOC-002 |  Parcial | README publicado con arquitectura |
| SEC-001 | 🟡 Parcial | `.gitignore` blindando secretos; auditoría pendiente |
| FND-002 / FND-003 | 🟡 Parcial | `requirements.txt`, `.env.example` |

✍️ **ESPACIO EQUIPO — propuesta a validar:** reclasificar `INT-004` a DONE libera margen en Semana 5. ¿De acuerdo? Sí / No / Comentarios: ______________________

---

## 5. Lo que falta, por fases

| Fase | Contenido | Objetivo de salida | Dueño sugerido |
|---|---|---|---|
| FASE 2 | Ingesta PDF/MD/TXT + chunking | Ingesta probada + contrato publicado | Backend devs |
| FASE 3 | Embeddings + ChromaDB + retrieval | RAG operativo | Data/RAG |
| FASE 4 | Prompts + generación adaptada | Contenido real por perfil/formato | AI/LLM |
| FASE 5 | LLM-juez + metadatos educativos | Score de fidelidad real | AI/LLM |
| FASE 6 | SDK oci + naming DT-07 | Persistencia real en bucket | Cloud |
| FASE 7 | UI conectada + reemplazo de mocks | Punta a punta sin mocks | UX + Orquestación |
| FASE 8 | INT-001…003 + QA-003 | Vertical slice completo | Orquestación |
| FASE 9-10 | Tests, 3 escenarios, docs | MVP robusto + demo | QA + todos |

### 5.1 Evoluciones propuestas del contrato (v0.2) — NO son decisiones aún

| Evolución | Por qué | Prueba del Product Goal que cubre | Estado |
|---|---|---|---|
| `POST /ingestar` + `document_id` | El documento se sube a OCI y se consulta por id | Prueba 1 | ✍️ A validar |
| `fuentes: [{chunk_id, page}]` | Trazabilidad de la respuesta | Prueba 5 | ✍️ A validar |
| SQLite de estado (DT-08) | Metadatos locales de docs/jobs | REQ-19/20 | ✍️ A validar |

---

## 6. Plan de pasos inmediatos

1. Subir el repo a GitHub e invitar al equipo completo.
2. Publicar reglas de la casa: ramas `feat/<ID>`, PR con ID en título, `.env` jamás commiteado, naming DT-07.
3. Kickoff FASE 2: ingesta + chunking con criterios de aceptación por historia.
4. QA escribe tests contra el mock desde hoy (QA-003 vertical slice).
5. UX avanza mockups de las 5 pantallas (agnósticos de herramienta) antes de FASE 7.
6. Mover el umbral de fidelidad a `.env` (DT-11), sin hardcodear.
7. Refinamiento semanal aplicando la regla de control de tareas CRIT.

---

## 7. ✍️ ESPACIOS EQUIPO (escriban aquí con confianza)

### 7.1 Propuestas de mejora

| # | Propuesta | Autor/a | Fase/área | Prioridad sugerida | ¿Acordada? |
|---|---|---|---|---|---|
| 1 |  |  |  |  |  |
| 2 |  |  |  |  |  |
| 3 |  |  |  |  |  |
| 4 |  |  |  |  |  |
| 5 |  |  |  |  |  |

### 7.2 Decisiones técnicas por validar en refinamiento

| # | Decisión | Opción actual | Opción propuesta | Dueño | Costo (días) | Resolución |
|---|---|---|---|---|---|---|
| 1 | UI de demo | Streamlit (DT-01) |  |  |  |  |
| 2 | Contrato v0.2 | Entrada inline | `document_id` + `fuentes` |  |  |  |
| 3 | Umbral fidelidad | IF n8n + `.env` |  |  |  |  |
| 4 |  |  |  |  |  |  |
| 5 |  |  |  |  |  |  |

### 7.3 Preguntas abiertas

| # | Pregunta | Quién la hace | Respuesta / responsable |
|---|---|---|---|
| 1 |  |  |  |
| 2 |  |  |  |
| 3 |  |  |  |

### 7.4 Notas libres del equipo

______________________________________________________________________

______________________________________________________________________

______________________________________________________________________

---

## 8. Glosario

| Término | Definición simple |
|---|---|
| API / Endpoint | Puente entre programas / cada URL que hace una cosa concreta |
| Webhook | Puerta que se activa sola cuando llega una petición |
| JSON / Schema (Pydantic) | Formato universal de datos / molde que valida entrada y salida |
| RAG | La IA consulta tus documentos antes de responder, en vez de inventar |
| Chunking / Embedding | Trocear el documento / convertir texto en huella numérica |
| Vector store (ChromaDB) | Despensa ordenada de huellas para buscar por significado |
| LLM (Gemini) | Modelo de lenguaje que redacta la respuesta |
| Orquestador (n8n) / Workflow / Nodo | Coordinador del flujo / el flujo / cada paso |
| Score de fidelidad | Nota 0–1 de cuánto de lo generado está sostenido por la fuente |
| Bucket / VM / Contenedor | Carpeta en la nube / computadora virtual / caja sellada que corre igual en cualquier lado |
| Deploy / Always Free | Llevar el proyecto a la nube / capa gratuita permanente de Oracle |

---

## 9. Anexos

**A. Comandos útiles:** ver sección 3.5 + `./demo.sh` (demo guiada en 3 pasos).
**B. Curl de prueba:** `curl -X POST http://localhost:8000/adaptar -H "Content-Type: application/json" -d '{...}'` (payload completo en `demo.sh`).
**C. Prioridades y DoD:** P0 necesaria para el MVP · P1 diferible · P2 evolución · P3 fuera. Una historia está Done cuando: implementada, cumple criterios, funciona, probada, con manejo de errores, integrada y demostrable.
**D. Referencias:** repo del equipo · PLAN y backlog (Diana) · Product Goal y pruebas de éxito (Pedro) · README del repo.
