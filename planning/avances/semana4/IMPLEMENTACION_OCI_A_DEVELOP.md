# Implementación OCI → Develop: Resumen de Cambios (Semana 4)

**Fecha:** 2026-10-14
**Autor:** Pedro Orozco (@PedrOroz)
**Rama origen:** `OCI` → **Rama destino:** `develop` (commit `a92de51`)

---

## Resumen Ejecutivo

Se completó la migración de la funcionalidad de generación con LLM real (Cohere + Gemini) desde la rama `OCI` a `develop`, implementando:

1. **Provider Cohere para generación** con failover automático a Gemini
2. **Failover automático** Cohere → Gemini → Mock
3. **Prompt versionado** cargado desde archivo (`generacion_v1.txt`)
4. **Tests completos** (unitarios + integración)
5. **Correcciones** en providers existentes (Gemini embeddings + generation)

---

## Cambios Principales

### 1. Provider Cohere para Generación (`src/generation/providers/cohere.py`)

**Nuevo archivo** - Implementación completa del `CohereLLMProvider`:

- **SDK:** `cohere.ClientV2` (v2 chat API)
- **Formato de respuesta:** `response_format={"type": "json_object"}` para forzar JSON válido
- **Modelo:** `command-r-plus` (alias, apunta a última revisión estable)
- **Max tokens:** 4096 (límite de command-r-plus)
- **Retry/Backoff:** Exponencial (2^attempt segundos), configurable vía `LLM_MAX_RETRIES`
- **Lectura defensiva:** `response.message.content[0].text` con guards para `None`/vacío
- **Lazy import:** `import cohere` dentro de `_get_client()` para tests sin SDK

### 2. Failover Automático Cohere → Gemini → Mock (`src/generation/failover.py`)

**Nuevo archivo** - `FailoverLLMProvider`:

```python
# Flujo:
1. Intenta Cohere (primario)
2. Si falla tras reintentos → log WARNING + intenta Gemini (respaldo)
3. Si ambos fallan → propaga LLMProviderError
   → Orquestador captura → fallback a mock → status="PARTIAL" + MOCK_NOTICE
```

**Seguridad:** El respaldo Gemini **solo** se encadena si `GEMINI_API_KEY` está definida. Si el equipo solo tiene key de Cohere, no se intenta construir un Gemini que fallaría.

### 3. Factory Actualizado (`src/generation/factory.py`)

```python
if provider == "cohere":
    cohere_provider = CohereLLMProvider()
    if settings.GEMINI_API_KEY:
        return FailoverLLMProvider(primary=cohere_provider, backup=GeminiLLMProvider())
    return cohere_provider
```

### 3. Prompt Versionado (`src/generation/prompt_loader.py` + `prompts/generacion_v1.txt`)

**Mejora sobre la rama OCI:** En lugar de prompt inline `f"""..."""`, se usa el prompt versionado del Plan Técnico (PROMPT-001):

- Carga `src/generation/prompts/generacion_v1.txt`
- Parsea secciones `SYSTEM:` / `CONTEXTO:`
- Rellena variables: `{contexto}`, `{perfil}`, `{formato}`, `{nicho}`, `{nivel}`
- **Alineación de esquema:** Prompt ajustado a `ContenidoAdaptado` real (`cuerpo`, `conceptos_clave`, `prerrequisitos`, `tiempo_estimado_min`)

### 4. Protocol `@runtime_checkable` (`src/generation/llm_provider.py`)

```python
@runtime_checkable
class LLMProvider(Protocol):
    def generate(self, prompt: str, temperature: float = 0.3) -> str: ...
```

Permite `isinstance(client, LLMProvider)` en tests y valida implementaciones en runtime.

### 5. Configuración (`src/core/config.py`)

```python
COHERE_MAX_TOKENS: int = 4096          # Límite command-r-plus
COHERE_MODEL: str = "command-r-plus"    # Alias a última revisión estable

@property
def active_embedding_dimensions(self) -> int:
    """Dimensión efectiva según proveedor activo."""
    if self.EMBEDDING_PROVIDER.lower() == "cohere":
        return self.COHERE_EMBEDDING_DIMENSIONS  # 1024
    return self.EMBEDDING_DIMENSIONS  # 768 (gemini/mock)
```

**Arregla bug crítico:** En develop original, `EMBEDDING_DIMENSIONS=768` pero `MockEmbeddingProvider.DIM=256` → colección Chroma se llamaba `nuevamente_mock_768` con vectores de 256. Ahora usa dimensión real por proveedor.

### 6. Correcciones Gemini (`src/embeddings/providers/gemini.py` + `generation/providers/gemini.py`)

| Archivo | Corrección |
|---|---|
| `embeddings/providers/gemini.py` | API v1 forzada (`HttpOptions(api_version="v1")`), sanitiza prefijo `models/` del nombre del modelo |
| `generation/providers/gemini.py` | `response_mime_type: "application/json"` para forzar salida JSON |

---

## Tests Implementados (257 totales, +28 nuevos)

| Archivo | Tests | Qué valida |
|---|---|---|
| `test_embeddings_cohere.py` | 7 | Lotes 96, `input_type` semántico, retry, error handling |
| `test_generation_cohere.py` | 8 | JSON output, parámetros, retry, contenido vacío |
| `test_generation_failover.py` | 6 | Cadena primaria/respaldo, logging, sin respaldo |
| `test_generation_factory.py` | 6 | mock/gemini/cohere, failover, validación API keys |
| `test_llm_fallback_to_mock.py` | 1 | Integración: LLM falla → mock → `status=PARTIAL` + `MOCK_NOTICE` |

**Total:** 257 tests pass (218 base + 28 nuevos + 11 previos embeddings/generation)

---

## Documentación Actualizada

| Archivo | Cambios |
|---|---|
| `README.md` | Sección "Almacenamiento en OCI" + corrección "ya probado en bucket real" |
| `TRACEABILITY.md` | REQ-06 (add Cohere) + REQ-09..13 (PARCIAL → IMPLEMENTADO) |
| `DAILY_SYNC_2026-10-12.md` | Correcciones históricas + estado real completado |
| `PERMISOS_IAM_BUCKET.md` | Roles IAM, políticas, smoke test, riesgos |

---

## Verificación en Bucket Real (OCI)

**Bucket:** `bucket-20260921-2152-nuevamente-docs-test` (namespace `axkf02paerjf`, región `mx-queretaro-1`)

```bash
# Smoke test verificado:
python -m scripts.smoke_bucket_real
# → Put/Head/List/Get + SHA256 verify en originals/ y generated/
# → Policy check: 403 en resultados/ (bloqueado para roles)
```

**Objetos creados en bucket real:**
```
originals/smoke_20261014T113755Z/test_20261014T113755Z.pdf
originals/smoke_20261014T114028Z/test_20261014T114028Z.pdf
generated/smoke_20261014T113755Z/result_20261014T113755Z.json
generated/smoke_20261014T114028Z/result_20261014T114028Z.json
```

---

## Riesgos y Mitigaciones

| Riesgo | Mitigación |
|---|---|
| `response_format` experimental en Cohere | `except` en orquestador cae a mock, no rompe demo |
| Prompt versionado pide campos inexistentes (`titulo`, `dificultad`) | Pydantic ignora extras; prompt alineado a `ContenidoAdaptado` real |
| `SUCCESS` ahora alcanzable | Tests existentes aserten `PARTIAL` con mock default → se mantiene verde |
| `remote develop` se mueve frecuentemente | Fase 0: `fetch + rebase` obligatorio antes de commitear |

---

## Commits Relacionados

| Commit | Descripción |
|---|---|
| `a92de51` | feat(sprint3): Cohere generation provider + failover Cohere→Gemini→mock |
| `fd4863f` | feat: integrate OCI IAM roles + bucket validation to develop |
| `3e22e65` | feat: IAM roles + bucket real validation for embeddings/generator agents |

---

## Próximos Pasos (Post-Sprint 3)

1. **DT-09 - Modelo de generación confirmado:** Decidir si Cohere/Gemini u otro proveedor para LLM principal
2. **LLM Juez real:** Implementar `verify_claim` con LLM (hoy heurístico por solapamiento de tokens)
3. **Asignar rol Orquestación/API** (hoy SIN ASIGNAR en `plan_tecnico.md:121`)
4. **Tests de carga** en bucket OCI con documentos reales
3. **Demo end-to-end** con documentos reales del bucket `docs-originales/`

---

## Comandos de Verificación Rápida

```bash
# Tests completos
cd nuevamente/backend && ruff check --config pyproject.toml src tests && pytest -q

# Smoke test bucket real
OCI_NAMESPACE=axkf02paerjf OCI_BUCKET_NAME=bucket-20260921-2152-nuevamente-docs-test \
  python -m scripts.smoke_bucket_real

# Listar objetos
python scripts/list_bucket.py --prefix originals/
python scripts/list_bucket.py --prefix generated/

# Bootstrap IAM (idempotente)
python -m scripts.bootstrap_iam_roles --dry-run  # ver plan
python -m scripts.bootstrap_iam_roles --apply    # aplicar
```

---

*Documento generado automáticamente como parte de la implementación Sprint 3 - OCI → Develop*