# Permisos IAM del bucket para agentes de embeddings y generación

**Fecha:** 2026-10-13
**Rama de implementación:** `OCI` (worktree `../oci-permisos`)
**Rama de documentación:** `docs/planning`

---

## 1. Estado real verificado (vs. documentación oficial)

| Recurso | Valor verificado en OCI (CLI) | Doc oficial (desactualizada) |
|---|---|---|
| **Tenancy** | `ocid1.tenancy.oc1..aaaa...x62gcnq` (Free Tier, propia) | "administrador de la tenancy" |
| **Compartment** | `Nuevamente` = `ocid1.compartment.oc1..aaaa...n5cjgmq` | No documentado |
| **Bucket** | `bucket-20260921-2152-nuevamente-docs-test` | OK |
| **Namespace** | `axkf02paerjf` | OK |
| **Región** | **`mx-queretaro-1`** (`~/.oci/config`) | `us-ashburn-1` ❌ |
| **Contenido actual** | Solo `docs-originales/` (7 PDFs, ~76 MB) | No documentado |
| **Grupo `hackathon-readers`** | Diana (sin API key) | OK |
| **Política `hackathon-readers-policy`** | `read objects` sobre el bucket | OK |
| **Regla guía §0.5** | "nadie debe subir" | **Bloquea REQ-18/OCI-003/OCI-005** |

> **Conclusión:** La guía `documentacion/semana1/guia_entorno_oci_equipo.md` y `documentacion/semana2/bloqueo_oci_semana2.md` contienen la región incorrecta y una regla ("solo lectura") que contradice los requisitos del plan técnico (REQ-18: DT-07, OCI-003 upload original, OCI-005 upload JSON + verificación).

---

## 2. Diseño de roles IAM (mínimo privilegio)

Tres grupos, dos políticas, un grupo runner que hereda ambos. Sin crear nuevos usuarios ni API keys: el usuario actual (Pedro) se añade al runner para las pruebas de hoy.

### 2.1 Grupo `nuevamente-embeddings` — Política `nuevamente-embeddings-policy`

```
Allow group nuevamente-embeddings to read objects in compartment Nuevamente
  where target.bucket.name = 'bucket-20260921-2152-nuevamente-docs-test'

Allow group nuevamente-embeddings to manage objects in compartment Nuevamente
  where all {
    target.bucket.name = 'bucket-20260921-2152-nuevamente-docs-test',
    target.object.name = 'originals/*',
    any { request.permission = 'OBJECT_CREATE',
          request.permission = 'OBJECT_OVERWRITE' }
  }
```

**Rol:** lee todo el bucket (incluye `docs-originales/`, `generated/`, `originals/`), escribe **solo** en `originals/*` (DT-07).

### 2.2 Grupo `nuevamente-generator` — Política `nuevamente-generator-policy`

```
Allow group nuevamente-generator to read objects in compartment Nuevamente
  where target.bucket.name = 'bucket-20260921-2152-nuevamente-docs-test'

Allow group nuevamente-generator to manage objects in compartment Nuevamente
  where all {
    target.bucket.name = 'bucket-20260921-2152-nuevamente-docs-test',
    target.object.name = 'generated/*',
    any { request.permission = 'OBJECT_CREATE',
          request.permission = 'OBJECT_OVERWRITE' }
  }
```

**Rol:** lee todo el bucket, escribe **solo** en `generated/*` (DT-07).

### 2.3 Grupo `nuevamente-runner` (sin política propia)

Miembro de `nuevamente-embeddings` **y** `nuevamente-generator`. Hereda ambos roles. Usado por el pipeline único actual (`PipelineOrchestrator`) para pruebas end-to-end.

### 2.4 `hackathon-readers` y `hackathon-readers-policy` → **no se tocan**

Diana conserva `read objects` sobre el bucket completo.

---

## 3. Prefijos de objeto (DT-07 canónico)

| Prefijo | Agente responsable | Operaciones permitidas |
|---|---|---|
| `originals/{doc_id}/{timestamp}_{nombre}` | Embeddings (ingesta) | PUT (CREATE/OVERWRITE), GET, HEAD |
| `generated/{doc_id}/{job_id}.json` | Generación | PUT (CREATE/OVERWRITE), GET, HEAD |
| `docs-originales/` | Seed data (solo lectura) | GET, HEAD, LIST |
| `resultados/` | **Ninguno** (legacy OCI branch) | Bloqueado → prueba negativa 403 |

> **Nota:** La rama OCI usaba `originales/` y `resultados/`; se alinea a `originals/` / `generated/` según `src/storage/naming.py` de develop (DT-07, OCI-003).

---

## 4. Entregables en rama `OCI`

| Archivo | Propósito |
|---|---|
| `backend/scripts/bootstrap_iam_roles.py` | Script idempotente (oci.identity) para crear/actualizar grupos, políticas y membresías. `--dry-run` por defecto, `--apply` para escribir. Imprime comandos de rollback. |
| `backend/scripts/smoke_bucket_real.py` | Prueba end-to-end: put/head/list/get en `originals/` y `generated/` + prueba negativa 403 en `resultados/`. Skip si no hay credenciales. |
| `backend/src/storage/naming.py` | Port de develop: `sanitize_filename` + `build_object_name` (timestamp `%Y%m%dT%H%M%SZ`). |
| `backend/src/storage/oci_client.py` | Re-exporta `build_object_name` desde `naming.py`. |
| `backend/src/storage/upload.py` | Prefijos `originals/` / `generated/`, verificación post-upload (`verify_upload`). |
| `backend/tests/integration/test_storage_mock.py` | Tests actualizados a nuevos prefijos. |
| `backend/src/api/orchestrator.py` | Fix: pasa `job_id` real (no `""`); llama `upload_original` en `register_document`. |
| `backend/src/api/main.py` | Pasa `content` a `register_document`. |

---

## 5. Procedimiento de validación

```bash
# 1. Worktree OCI (ya creado)
cd ../oci-permisos

# 2. Lint + tests mock
cd backend && ruff check --config pyproject.toml src tests
pytest -q

# 3. Dry-run bootstrap
python -m backend.scripts.bootstrap_iam_roles --dry-run --verbose

# 4. Apply (requiere admin en la tenancy)
python -m backend.scripts.bootstrap_iam_roles --apply --verbose

# 5. Esperar propagación de políticas (1-5 min, Oracle advierte delay)
# 6. Crear marcadores de prefijo (0 bytes) para listados con política de objeto
oci os object put -ns axkf02paerjf -bn bucket-20260921-2152-nuevamente-docs-test \
  --file /dev/null --name "originals/"
oci os object put -ns axkf02paerjf -bn bucket-20260921-2152-nuevamente-docs-test \
  --file /dev/null --name "generated/"

# 7. Smoke test real
python -m backend.scripts.smoke_bucket_real

# 8. Verificación independiente
python backend/scripts/list_bucket.py --prefix originals/
python backend/scripts/list_bucket.py --prefix generated/
```

---

## 6. Riesgos y mitigaciones

| Riesgo | Mitigación |
|---|---|
| **Propagación de políticas** (Oracle: delay en políticas Object Storage) | Esperar 1-5 min tras `--apply`; smoke test reintenta implícitamente. |
| **ListObjects con prefijo bajo política de objeto** puede filtrar resultados | Crear objetos marcadores vacíos `originals/` y `generated/` antes del test. |
| `read objects` podría no cubrir `HEAD` en algunos tenants | El verbo `read` en Object Storage = `OBJECT_INSPECT` + `OBJECT_READ` (doc oficial). Si falla `head_object`, añadir statement explícito `inspect objects`. |
| `hackathon-readers` se rompe si se mueve el bucket | No se toca; bucket no se mueve. |
| `.env` en raíz contiene `GITHUB_TOKEN` vivo | Rotar token y eliminar del `.env` (ya está en `.gitignore`). |

---

## 7. Correcciones a la documentación oficial (pendientes de PR)

1. `documentacion/semana1/guia_entorno_oci_equipo.md`:
   - §2 tabla "Región": `us-ashburn-1` → **`mx-queretaro-1`**
   - §8.1 script: `bucket_test.py` → `list_bucket.py` (endpoint HTTP `/test/oci/objects` ya no existe)
   - §0.5 regla "solo lectura": añadir nota *"Excepto roles `nuevamente-embeddings` (originals/) y `nuevamente-generator` (generated/) por REQ-18/OCI-003/OCI-005"*

2. `documentacion/semana2/bloqueo_oci_semana2.md`:
   - §2.1 tabla "Región": `us-ashburn-1` → **`mx-queretaro-1`**
   - §3 tabla "OCI Object Storage": añadir nota de región real

3. `planning/avances/semana2/EstructuraRamaOCI.md`:
   - Bug 1 y Bug 5 ya corregidos en este plan (job_id real, upload_original conectado).

---

## 8. Rollback (si algo falla)

```bash
# Eliminar membresías
oci iam group remove-user --group-id <runner_gid> --user-id <user_ocid>
# Eliminar políticas
oci iam policy delete --policy-id <embeddings_pid> --force
oci iam policy delete --policy-id <generator_pid> --force
# Eliminar grupos
oci iam group delete --group-id <embeddings_gid> --force
oci iam group delete --group-id <generator_gid> --force
oci iam group delete --group-id <runner_gid> --force
```

> Los OCIDs exactos los imprime `bootstrap_iam_roles.py --apply` al final.