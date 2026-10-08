# Cambios realizados en la rama `main`

Fecha: 2026-10-08

## Objetivo

Dejar `main` limpia y alineada con `develop` antes de promover todo el trabajo a `main`.

## Estado final de `main`

```
.github/        # único workflow de CI
.gitignore      # nuevo, definido en la raíz
nuevamente/     # toda la aplicación (backend, ui, docs, ejemplos...)
```

## Cambios

### 1. Merge de `develop` (PR #107, commit `d16e6b2`)

`main` ahora contiene todo lo desarrollado: pipeline RAG (ingesta, chunking, embeddings,
retrieval, validación), UI Streamlit, proveedores mock/Gemini, storage OCI y 94 tests.

### 2. Alineación de archivos binarios y documentos operativos (commit `0239e16`)

- `PLAN.pdf`, `LISTbacklog.pdf`, `Nuevamente_PlanTecnico_v1.pdf` → `nuevamente/docs/adjuntos/`
  (las 3 copias externas sin trackear que estaban en la raíz del repo).
- `AVANCES_SEMANA3.md` → `nuevamente/docs/avances/semana3.md`. Había sido commiteado
  por error bajo `main/planning/avances/semana3/`; esa ruta `main/` fue eliminada.
- Bloqueo OCI (`bloqueo_despliegue_vm_oci.md`) → `nuevamente/docs/bloqueo_oci_semana2.md`.
- Nuevo `.gitignore` en la raíz (secretos `.env`, `*.pem`, `.oci/`, caches de Python,
  `data/` local).

### 3. Eliminación de `planning/` (PR #108, en revisión)

`planning/`, que había entrado por el PR #12, se sacó de `main`:

- Todo `planning/` vive ahora en la rama **`docs/planning`** (archivado).
- `planning/backlog/*` se trasladó a `nuevamente/docs/backlog/` y sigue visible.
- `planning/avances/semana3/AVANCES_SEMANA3.md` era duplicado de
  `nuevamente/docs/avances/semana3.md`, eliminado.
- Por tanto, **no usar `planning/` como ruta activa**: referencias legacy deben
  apuntar a `docs/planning` (historia) o `nuevamente/docs/backlog/` (backlog).

### 4. Depuración local (sin impacto en el repo)

Se borraron de la máquina: `backend/` (restos del layout antiguo, sin código),
`documentacion/` (ya en `nuevamente/docs/`), `__pycache__/`, caches de pytest/ruff.

## Advertencias conocidas

- **Historial duplicado en `main`**: `14341a9` ≡ `3ffd8d6`, `5125710` ≡ `3e9b927`, etc.
  (mismo mensaje y árbol, distinto hash) porque `develop` fue rebasado localmente.
  Cosmético; los árboles son idénticos.
- `origin/OCI`, `origin/proposal/v1`, `origin/RAG-Gemini` conservan layouts antiguos
  y siguen siendo ramas independientes.
- Crear `main` local con `git checkout main` puede quedar 19 commits atrás;
  sincronizar con `git pull` o `git reset --hard origin/main`.
