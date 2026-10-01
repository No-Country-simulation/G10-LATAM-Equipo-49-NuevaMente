# NuevaMente  

> Sistema Inteligente de Adaptación y Generación de Contenido Educativo
> Hackathon ONE · Grupo 10 · NoCountry × Oracle Cloud Infrastructure

## 🎯 Problema que resuelve NuevaMente

La documentación técnica es densa y única para todas las audiencias.
NuevaMente la convierte en contenido educativo personalizado según
perfil, formato pedagógico y nicho, validando que el resultado esté
anclado a la fuente antes de entregarlo.

## 📁 Estructura del proyecto

```
nuevamente-g10/
├── .env.example                 # variables declaradas en Fase 6, sin secretos
├── .gitignore
├── README.md
├── demo.sh                       # guion de demo — placeholder, sin lógica real
│
├── backend/
│   ├── pyproject.toml / requirements.txt
│   ├── src/
│   │   ├── core/                # config declarativa, logging, excepciones
│   │   ├── ingestion/            # COMP-01 — contratos de extracción PDF/MD/TXT
│   │   ├── processing/           # COMP-02 — DocumentChunk, chunking
│   │   ├── embeddings/           # COMP-03 — EmbeddingProvider (Gemini/Mock)
│   │   ├── vectorstore/          # COMP-04 — VectorStore (ChromaDB)
│   │   ├── rag/                  # COMP-05 — RetrievalService, NO_CONTEXT
│   │   ├── generation/           # COMP-06 — LLMProvider, prompts versionados
│   │   ├── validation/           # COMP-07 — ValidationService, fidelidad
│   │   ├── output/               # COMP-08 — NuevaMenteOutput (contrato Fase 6)
│   │   ├── storage/               # COMP-09 — StorageClient (OCI/Mock)
│   │   ├── db/                    # persistencia de Jobs (DT-08)
│   │   └── api/                   # COMP-11 — endpoints FastAPI (contrato)
│   └── tests/
│       ├── unit/  ├── integration/  └── fixtures/
│       └── TESTING_STRATEGY.md   # QUÉ se probará — sin `def test_...`
│
├── ui/                           # COMP-10 — Streamlit (5 pantallas, contrato)
├── n8n-workflows/                # DT-10 — diferencial, fuera de alcance
├── docs/
│   ├── architecture.md           # arquitectura completa + decisiones de diseño
│   ├── TRACEABILITY.md            # Plan → Componente → Contrato → Backlog → Implementación futura
│   ├── AUDIT.md                   # auditoría de salida (clasificación por archivo)
│   ├── diagrams/pipeline.mmd
│   └── demo-scenarios/
├── docs-git/GIT_GITHUB_GUIDE.md  # convenciones de branches/commits/PR/Issues (archivo aparte)
├── CONTRIBUTING.md
└── data/                          # gitignored — estado local futuro
```

## 📖 Empezar a leer por aquí

1. [`docs/architecture.md`](docs/architecture.md) — qué construye
   NuevaMente, los 11 componentes, el contrato de la API y las decisiones
   de diseño que este repositorio agregó sobre lo explícito en el Plan
   Técnico.
2. [`docs/TRACEABILITY.md`](docs/TRACEABILITY.md) — de cada requisito del
   Plan Técnico a su componente, su contrato, su(s) tarea(s) de backlog, y
   qué falta implementar.
3. [`CONTRIBUTING.md`](CONTRIBUTING.md) — cómo implementar sobre esta base
   sin romper los contratos.
4. [`docs-git/GIT_GITHUB_GUIDE.md`](docs-git/GIT_GITHUB_GUIDE.md) —
   convenciones de branches, commits, Pull Requests e Issues.
5. [`docs/AUDIT.md`](docs/AUDIT.md) — verificación de que ningún archivo
   de este repositorio quedó como implementación funcional.

