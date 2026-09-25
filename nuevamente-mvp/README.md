# NuevaMente 🧠

> Sistema Inteligente de Adaptación y Generación de Contenido Educativo
> Hackathon ONE · Grupo 10 · NoCountry × Oracle Cloud Infrastructure

Esta rama es la **línea base del MVP (MVP Repository Baseline)**: el código
de los 11 componentes, tests, scripts de verificación y CI, extraídos tal
cual de `NuevaMente-Guia-Desarrollo.md` (fuente de autoridad Alta para la
implementación). Corre de punta a punta en **modo mock** sin ninguna
credencial real.

## 🎯 Problema

La documentación técnica es densa y única para todas las audiencias.
NuevaMente la convierte automáticamente en contenido educativo
personalizado según perfil, formato, nicho y nivel de detalle, validando
que el resultado esté anclado a la fuente (score de fidelidad) antes de
entregarlo.

## 🏗️ Arquitectura (resumen)

```
UI (Streamlit) ──HTTP──▶ API (FastAPI) ──▶ Orchestrator ──▶ Ingestion → Processing
                                                              → Embeddings → VectorStore
                                                              → RAG → Generation
                                                              → Validation → Output
                                                              → Storage (OCI / mock)
```

Detalle por capa, dónde va cada tipo de cambio y el contrato de datos:
[`docs/architecture.md`](docs/architecture.md) · Diagrama:
[`docs/diagrams/pipeline.mmd`](docs/diagrams/pipeline.mmd).

## 📁 Estructura del proyecto

```
nuevamente-g10/
├── backend/
│   ├── requirements.txt / pyproject.toml
│   ├── scripts/               # check_definition_of_done.sh, verify_mvp.sh, audit_checklist.py
│   ├── src/
│   │   ├── core/               # config (pydantic-settings), logging, exceptions
│   │   ├── ingestion/          # PDF (PyMuPDF) / MD / TXT
│   │   ├── processing/         # DocumentChunk, limpieza, chunking
│   │   ├── embeddings/         # EmbeddingProvider (Gemini / Mock) + factory
│   │   ├── vectorstore/        # ChromaDB
│   │   ├── rag/                # retrieval + contexto (regla NO_CONTEXT)
│   │   ├── generation/         # perfiles, prompts, LLMProvider, orquestador
│   │   ├── validation/         # claims + fidelidad (LLM-juez + score determinista)
│   │   ├── output/             # NuevaMenteOutput (contrato Pydantic v2)
│   │   ├── storage/            # OCI real + mock_client.py
│   │   ├── db/                 # SQLite (jobs)
│   │   └── api/                # FastAPI — solo orquesta
│   └── tests/
│       ├── unit/  ├── integration/  └── fixtures/
├── ui/                          # Streamlit (5 pantallas)
├── docs/                        # arquitectura, trazabilidad, escenarios de demo
├── data/                        # gitignored — chroma, sqlite, mock_oci
├── .github/workflows/ci.yml
├── .env.example
├── CONTRIBUTING.md
└── demo.sh
```

## 🚀 Instalación y uso local

```bash
git clone https://github.com/NoCountry-simulation/G10-LATAM-Equipo-49-NuevaMente.git
cd G10-LATAM-Equipo-49-NuevaMente
cp .env.example .env        # valores por defecto ya corren en modo mock

cd backend
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt

uvicorn src.api.main:app --reload --port 8000   # Terminal 1
curl http://localhost:8000/health                # Terminal 2
```

UI:

```bash
cd ui
streamlit run app.py
```

Por defecto `.env.example` trae `LLM_PROVIDER=mock` y
`EMBEDDING_PROVIDER=mock`: todo el pipeline corre sin API key de Gemini ni
credenciales de OCI. Cambiar a real es solo editar esas dos variables.

## ✅ Verificación (orden recomendado antes de una demo)

```bash
cd backend
./scripts/check_definition_of_done.sh   # lint + tests + sin secretos
pytest tests/ -v --cov=src              # suite completa
./scripts/verify_mvp.sh                 # flujo end-to-end vía curl (con el server corriendo)
python scripts/audit_checklist.py       # checklist final (Fase 20)
```

Ver el flujo completo de contribución (branching, commits, PRs, testing,
Definition of Done) en [`CONTRIBUTING.md`](CONTRIBUTING.md).

## 📖 Documentación

- [Arquitectura del sistema](docs/architecture.md)
- [Trazabilidad Plan ↔ Backlog ↔ Guía ↔ Repo ↔ Demo](docs/TRACEABILITY.md)
- [Guía de contribución](CONTRIBUTING.md)
- [Escenarios de demo](docs/demo-scenarios/)

## 👥 Equipo

| Rol | Integrante |
|-----|------------|
| Orquestación / Backend | Rodrigo Reyes |
| Cloud Developer | Pedro Orozco |
| Backend Developers | Miguel, Fernando, Osvaldo |
| UX/UI Designer | Viviana Hurtado |
| QA / Testing | Eduardo C |
| Scrum Lead | Diana |

## 📋 Estado del proyecto

- ✅ **Fase 1 (esta línea base):** los 11 componentes implementados en modo
  mock, suite de tests (unit + integration + golden), CI, scripts de DoD /
  verificación MVP / auditoría del checklist final.
- ⏳ **Pendiente formal:** confirmación del equipo del proveedor de
  LLM/embeddings (Gemini está integrado pero no confirmado formalmente),
  reconciliación de roles Scrum, selección de los 3 documentos de demo
  (DEMO-000).

## 🏆 Requisitos del hackathon

Ver la clasificación completa (REQ-01..24, DIF-01..11), decisiones técnicas
DT-01..DT-11 y el mapeo componente por componente en
[`docs/architecture.md`](docs/architecture.md) y
[`docs/TRACEABILITY.md`](docs/TRACEABILITY.md).
