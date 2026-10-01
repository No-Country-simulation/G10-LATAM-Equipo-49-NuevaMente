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
## BACKEND
> La adaptación (`/adapt`) funciona en **modo mock**: cita fragmentos reales del documento,
> pero todavía no usa inteligencia artificial.

## Requisito
Python **3.11 o superior** (en Windows, marcar "Add python.exe to PATH" al instalarlo).

## Encender la API (2 pasos)

| Paso | Windows | Mac / Linux |
|---|---|---|
| 1. Instalar (una sola vez) | `setup.bat` | `./setup.sh` |
| 2. Encender la API | `run_api.bat` | `./run_api.sh` |

- API: http://127.0.0.1:8000
- Documentación interactiva (probar desde el navegador): http://127.0.0.1:8000/docs
- No hace falta crear `.env`: todo funciona con los valores por defecto.
- Prueba rápida por consola (con la API encendida): `./demo.sh`

Manual, sin scripts:
```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
cd backend
python -m uvicorn src.api.main:app --host 127.0.0.1 --port 8000
```

## Endpoints

| Endpoint | Qué hace | Respuesta |
|---|---|---|
| `GET /health` | ¿Está viva la API? | `200 {"status":"ok"}` |
| `POST /ingest` (campo `file`) | Sube un PDF/MD/TXT | `201` con `document_id` y resumen |
| `POST /adapt` (JSON) | Pide la adaptación | `202` con `job_id` |
| `GET /adapt/{job_id}` | Consulta el resultado | `200` resultado · `202` en proceso · `404` no existe |

```bash
curl -F "file=@ejemplos/sample_contenedores.md" http://127.0.0.1:8000/ingest
curl -X POST http://127.0.0.1:8000/adapt -H "Content-Type: application/json" \
  -d '{"document_id":"doc_...","perfil":"principiante","formato":"tutorial"}'
curl http://127.0.0.1:8000/adapt/job_...
```

Opciones de `/adapt`: perfil `principiante · developer · lider_tecnico · ejecutivo`;
formato `tutorial · resumen_ejecutivo`; `nivel_detalle` `breve · estandar · profundo` (opcional).

Errores: siempre `{"error": {"code": "...", "message": "..."}}`.

| Código | HTTP | Cuándo |
|---|---|---|
| `INVALID_FILE` | 400 | Tipo no soportado, vacío, > 10 MB, PDF dañado o con contraseña |
| `SCANNED_PDF` | 400 | PDF sin texto seleccionable (escaneado) |
| `DOCUMENT_TOO_LARGE` | 400 | Texto demasiado largo |
| `INVALID_REQUEST` | 400 / 422 | Perfil/formato/nivel desconocido o cuerpo mal formado |
| `DOCUMENT_NOT_FOUND` / `JOB_NOT_FOUND` | 404 | Id inexistente |
| `STORAGE_ERROR` | 502 | Falla el almacenamiento |

## Estructura
```
backend/src/
  api/         endpoints y coordinación         ingestion/   leer PDF/MD/TXT
  processing/  limpieza y fragmentación         storage/     guardar archivos (local u OCI)
  generation/  adaptación mock + catálogo       output/      formato de la respuesta
  db/          base de datos SQLite             core/        configuración, errores, logs
ejemplos/      documento de prueba              data/        datos locales (se crea solo)
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

