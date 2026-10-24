# Reporte de validación, ejecución de pruebas y revisión del proyecto

**Proyecto:** NuevaMente — G10 (NoCountry × Oracle Cloud Infrastructure)
**Fecha de ejecución:** 2026-10-23
**Ámbito validado:** `G10/nuevamente/backend` (tests unitarios, integración y auditoría), lint, imports, cobertura y flujo HTTP.
**Tipo de trabajo:** solo diagnóstico y evidencias. **No se modificó ningún archivo del proyecto.**

---

## 1. Veredicto ejecutivo

| Indicador | Resultado |
|---|---|
| Tests ejecutados | **290** |
| Tests aprobados | **282** |
| Tests fallidos | **8** |
| Tests omitidos | 0 (en la corrida final, con `ruff` en PATH) |
| Tiempo de la suite | **27,04 s** (sin cobertura) · 741,53 s (con cobertura) |
| Lint (`ruff`) | **All checks passed** |
| Importación de todos los módulos de `src/` | **OK** |
| Cobertura de líneas | **86 %** (1 737 statements, 250 sin cubrir) |
| Flujo `/ingest` | **Funciona** (6/6 documentos de prueba ingeridos) |
| Flujo `/adapt` | **Roto** (HTTP 500 en el 100 % de los casos) |

> **Veredicto: NO APTO para demo ni para cierre de integración.** Existe un defecto crítico y único que
> invalida el flujo principal del producto: `GenerationOrchestrator.generate_content()` sigue siendo un
> *stub* que devuelve `None`, y el orquestador accede a `content.cuerpo` sin validar el retorno.
> El resultado es que **todo `/adapt` termina en `ERROR` y responde HTTP 500**, incumpliendo el contrato
> de la Fase 6. Los 8 tests fallidos derivan de esta misma causa.

---

## 2. Entorno y método

### 2.1 Entorno de ejecución

| Elemento | Valor |
|---|---|
| Sistema operativo | Windows (win32) |
| Python | **3.12.10** (el CI declara **3.11**) |
| Entorno | `venv` temporal fuera del repositorio (`%TEMP%\opencode\venv-nm`) |
| Instalación | `pip install -r backend/requirements-dev.txt` |
| Fecha/hora | 2026-10-23 18:48 (hora local) |
| Repositorio Git | **No disponible** (no existe carpeta `.git` en el árbol entregado) |

Versiones relevantes instaladas:

```
fastapi==0.162.0            pydantic==2.14.1          pydantic-settings==2.16.1
uvicorn==0.54.0             streamlit==1.66.1         httpx==0.28.1
pypdf==6.21.2               reportlab==5.1.0          chromadb==1.5.9
google-genai==1.75.0        cohere==5.21.1            langchain-text-splitters==1.1.3
pytest==9.1.1               pytest-cov==7.1.0         coverage==7.17.0
ruff==0.17.2                onnxruntime==1.31.0       numpy==2.5.4
```

> Limitación: no hay `.git`, por lo que **no fue posible hacer `git diff` contra la última integración**.
> La comparación se hizo contra el estado documentado por el propio equipo (`docs/informe_audit_nuevamente.md`,
> `docs/AVANCES`, `docs/TRACEABILITY.md`, fechados 2026-10-14/15) y contra las marcas `MEJORA AUD-xxx`
> presentes en el código.

### 2.2 Comandos ejecutados

```bash
# 1. Lint (mismo comando del CI)
cd G10/nuevamente/backend
ruff check --config pyproject.toml src tests scripts ../ui

# 2. Verificación de imports (mismo paso del CI)
python -c "import importlib, pkgutil, src; \
  [importlib.import_module(n) for _, n, _ in pkgutil.walk_packages(src.__path__, prefix='src.')]"

# 3. Suite completa (misma invocación del CI)
pytest -q -p no:cacheprovider

# 4. Cobertura (adicional)
pytest -q --cov=src --cov-report=term-missing --cov-report=json:coverage.json

# 5. Reproducción independiente del pipeline
python repro/repro_01_pipeline.py

# 6. Validación de los 6 documentos de prueba contra /ingest y /adapt
python validate_docs.py
```

---

## 3. Resultados de la ejecución

### 3.1 Distribución por suite

| Suite | Tests | Aprobados | Fallidos | % éxito |
|---|---:|---:|---:|---:|
| `tests/unit` | 227 | 227 | 0 | 100 % |
| `tests/integration` | 31 | 26 | 5 | 83,9 % |
| `tests/audit` | 32 | 29 | 3 | 90,6 % |
| **Total** | **290** | **282** | **8** | **97,2 %** |

La suite coincide en tamaño con la reportada por el equipo el 2026-10-15 (**290 tests**), pero aquel
informe afirmaba **290 passed**. Hoy hay **8 fallos**: la diferencia no es de tests faltantes, sino de
**código no integrado o revertido**.

### 3.2 Tests fallidos (los 8)

| # | Test | Error observado |
|---|---|---|
| 1 | `tests/audit/test_audit_rag.py::test_aud_001_el_tema_pedido_orienta_las_fuentes` | `AttributeError: 'NoneType' object has no attribute 'cuerpo'` |
| 2 | `tests/audit/test_audit_rag.py::test_aud_007_un_reinicio_no_degrada_el_resultado_en_silencio` | `AttributeError: 'NoneType' object has no attribute 'cuerpo'` |
| 3 | `tests/audit/test_audit_rag.py::test_aud_009_las_plantillas_no_cuentan_como_afirmaciones_no_soportadas` | `AttributeError: 'NoneType' object has no attribute 'cuerpo'` |
| 4 | `tests/integration/test_llm_fallback_to_mock.py::test_full_flow_fallback_to_mock_when_llm_fails` | `assert 500 == 200` |
| 5 | `tests/integration/test_pipeline_e2e.py::test_full_flow_returns_valid_partial_output` | `assert 500 == 200` |
| 6 | `tests/integration/test_pipeline_e2e.py::test_detail_level_is_ignored_and_default_source_count_is_stable` | `KeyError: 'metadatos'` (la respuesta es un error, no un output) |
| 7 | `tests/integration/test_pipeline_e2e.py::test_same_document_can_be_adapted_with_other_profile` | `KeyError: 'metadatos'` |
| 8 | `tests/integration/test_pipeline_e2e.py::test_niche_defaults_to_general` | `KeyError: 'metadatos'` |

**Los 8 fallos tienen una única causa raíz.** Los tests de auditoría AUD-001/007/009 **no fallan por sus
propias correcciones** (el código de retrieval, reindexado y claims sí está implementado), sino porque
su *arrange* usa `run_adaptation()` y este explota antes de evaluar la aserción.

### 3.3 Evidencia del fallo raíz

```
File "G10\nuevamente\backend\src\api\orchestrator.py", line 313, in run_adaptation
    fidelity_eval = validation_service.validate(content.cuerpo, contexto)
                                                ^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'cuerpo'
```

Cadena causal:

1. `src/generation/orchestrator.py` (líneas 12-33) declara `GenerationOrchestrator.generate_content()`
   con cuerpo `...` → devuelve `None` y **nunca invoca al proveedor LLM**.
2. `src/api/orchestrator.py` (líneas 295-298) envuelve la llamada en `try/except`, pero como el *stub*
   **no lanza excepción**, el `except` de *fallback* a mock no se activa.
3. En la línea 313 se accede a `content.cuerpo` fuera del `try` → `AttributeError`.
4. `execute_job` captura la excepción genérica y marca el job como `ERROR`.
5. `GET /adapt/{job_id}` responde **500 INTERNAL_ERROR**.

### 3.4 Evidencia HTTP del flujo completo

| Paso | HTTP | Resultado |
|---|---:|---|
| `GET /health` | **200** | `{"status":"ok"}` |
| `POST /ingest` (PDF de 13 páginas) | **201** | `INGESTED`, `page_count=13`, `chunk_count=23` |
| `POST /adapt` (solicitud válida) | **202** | `job_id` creado, `status=PROCESSING` |
| `GET /adapt/{job_id}` | **500** | `{"error":{"code":"INTERNAL_ERROR","message":"Error interno durante la adaptación."}}` |
| `GET /adapt/job_inexistente` | **404** | `JOB_NOT_FOUND` |
| `POST /adapt` (documento inexistente) | **404** | `DOCUMENT_NOT_FOUND` |
| `POST /adapt` (perfil inválido) | **422** | `INVALID_REQUEST` |

Los caminos de error, validación y consulta de jobs funcionan. **El único camino roto es la generación.**

### 3.5 Cobertura (y por qué no detectó el defecto)

| Módulo | Cobertura | Lectura |
|---|---:|---|
| **Total `src/`** | **86 %** | Buena cobertura global |
| `generation/orchestrator.py` (defectuoso) | **100 %** | **Métrica engañosa**: el `...` del stub se “ejecuta” |
| `api/orchestrator.py` | 81 % | Líneas 299-309 y 315-331 (fallback/éxito) no se alcanzan |
| `generation/prompt_loader.py` | **0 %** | Código muerto en la práctica |
| `storage/oci_client.py` | 23 % | Cliente OCI real no ejercitado |
| `storage/oci_config.py` | 21 % | Configuración OCI no ejercitada |
| `generation/providers/gemini.py` | 33 % | Camino real de Gemini sin cubrir |

**Hallazgo metodológico:** el 86 % de cobertura y el 100 % del módulo roto demuestran que la cobertura
de líneas no sustituye una prueba de contrato. No existe ningún test unitario de
`generate_content()`: solo se ejercita de forma indirecta en integración, y al no haber aserción sobre
el tipo de retorno, el defecto pasa inadvertido en la suite unitaria.

### 3.6 Lint e imports

- `ruff check --config pyproject.toml src tests scripts ../ui` → **All checks passed!**
- Importación de los 74 módulos de `src/` → **OK** (la app arranca y `/health` responde).
- Verificación estática de gramática compatible con Python 3.11 (`ast.parse(..., feature_version=(3,11))`)
  sobre 132 archivos `.py` → **sin errores**. No se encontraron *f-strings* con barras invertidas
  (caso AUD-016).

> El CI declara Python 3.11 y la validación local se hizo con 3.12.10. No se pudo ejecutar la suite en
> 3.11 porque el entorno solo dispone de 3.12; se hizo la comprobación estática como sustituto parcial.

---

## 4. Hallazgos de la revisión (respecto a la última integración documentada)

### 4.1 Tabla de hallazgos

| ID | Severidad | Hallazgo | Evidencia | Impacto |
|---|---|---|---|---|
| **H-01** | **Crítico** | `GenerationOrchestrator.generate_content()` es un *stub* (`...`); `/adapt` responde 500 | `src/generation/orchestrator.py:12-33`, `src/api/orchestrator.py:295-313`, 8 tests fallidos | Bloquea el flujo principal, la demo y la validación de fidelidad |
| **H-02** | **Alto** | La documentación de la última integración declara implementado y “290 passed” lo que el código no cumple | `docs/informe_audit_nuevamente.md:234-242` (AUD-020), `docs/TRACEABILITY.md:20` vs. código y corrida real | Genera una falsa sensación de cierre; el CI real fallaría |
| **H-03** | Medio | `README.md` está duplicado y corrupto: dos documentos concatenados a mitad de frase y con afirmaciones contradictorias | `README.md:8-11` (`...for# NuevaMente`) y `README.md:271-273`; `fidelidad_score` heurístico (l. 222) vs `null` (l. 475) | Documentación no confiable para onboarding y demo |
| **H-04** | Medio | No hay test unitario del contrato de `generate_content()`; la cobertura del módulo roto es 100 % | `coverage.txt`: `generation/orchestrator.py 4 stmts 100%` | El defecto crítico es invisible para la suite unitaria |
| **H-05** | Medio | El test de *fallback* muta `os.environ` sin limpieza ni invalidación de caché de settings | `tests/integration/test_llm_fallback_to_mock.py:10-19` | Riesgo de dependencia de orden y contaminación entre tests |
| **H-06** | Medio | `.env.example` y `docker-compose.yml` exponen *namespace* y bucket OCI reales, mientras la documentación afirma “sin valores reales” | `.env.example:87-88`, `docker-compose.yml:8-12`, `README.md:236` | Divulgación de infraestructura y deriva de configuración |
| **H-07** | Medio | Los escenarios de demo siguen marcados `CONTRACT-ONLY` y DEMO-000 sin resolver | `docs/demo-scenarios/*.md` | No hay evidencia de demo reproducible pese a que el pipeline se declara listo |
| **H-08** | Bajo | `DAILY_SYNC_2026-10-12.md` tiene secciones duplicadas (61-112) | `docs/planning/avances/semana4/DAILY_SYNC_2026-10-12.md:61-112` | Ruido documental |
| **H-09** | Bajo | `requirements.txt` raíz conserva un bloque comentado de dependencias antiguas pese a AUD-021 (“fuente única”) | `G10/requirements.txt:1-9` | Deriva/duplicación residual |
| **H-10** | Bajo | Metadatos y estrategia desactualizados: `pyproject` dice “RAG y LLM pendientes”; `TESTING_STRATEGY.md` lista suites ya implementadas | `backend/pyproject.toml:4`, `backend/tests/TESTING_STRATEGY.md:3-5` | Confusión sobre el estado real |
| **H-11** | Bajo | Brechas de cobertura en OCI real (21-23 %), `prompt_loader` (0 %) y proveedor Gemini (33 %) | `coverage.txt` | Riesgo no verificado en los caminos reales |
| **H-12** | Informativo | Imágenes Docker instalan dependencias de desarrollo y la UI monta una clave SSH privada | `Dockerfile.backend:18-19`, `Dockerfile.ui:18-19`, `docker-compose.yml:20-21,43` | Superficie y tamaño innecesarios en producción |
| **H-13** | Informativo | El workflow CI vive en `G10/.github/workflows` con `working-directory: nuevamente/backend`; sin `.git` no se puede confirmar que sea la raíz del repositorio | `.github/workflows/ci.yml:20-23` | Riesgo de que el CI no se dispare si la raíz es otra |

### 4.2 Contradicciones documentales sobre el mismo archivo

| Fuente | Afirmación sobre `generation/orchestrator.py` |
|---|---|
| `docs/informe_audit_nuevamente.md:234-242` | “**Corregido**: arma el prompt, invoca al `LLMProvider` y mapea a `ContenidoAdaptado`” |
| `docs/TRACEABILITY.md:20` | “**IMPLEMENTADO** … respuesta JSON validada como `ContenidoAdaptado`” |
| `docs/AUDIT.md:56` | “`orchestrator.py` — **CONTRATO (pendiente)**” |
| `docs/avances/semana3.md:94` | “`generate_content()` … **pendiente**” |
| Código real + suite | **Stub (`...`)** → 8 tests fallidos |

La fuente de verdad operativa es el código y los tests, y ambos confirman que la pieza **no está
integrada**. El patrón sugiere una integración parcial: se incorporaron tests, documentación y correcciones
periféricas (assembler, validación, retrieval, vector store), pero **no la implementación de generación**.

> Nota importante sobre los tests de auditoría: `test_aud_001`, `test_aud_007` y `test_aud_009` son
> **regresiones permanentes** que validan correcciones reales ya presentes en el código. Su fallo es
> colateral de H-01 y no debe interpretarse como reapertura de AUD-001/007/009.

---

## 5. Validación de los 6 documentos de prueba

Se generaron 3 artefactos técnicos ficticios, cada uno en PDF y Markdown, con extensiones de **5, 10 y 13
páginas**. Todos se ingirieron correctamente; todos fallaron en `/adapt` por H-01 (no por el documento).

| Archivo | Formato | Bytes | Ingesta | Páginas | Chunks | Caracteres | `/adapt` |
|---|---|---:|---|---:|---:|---:|---|
| `atlas-pay-5p.pdf` | PDF | 9 773 | OK | **5** | 6 | 3 502 | ERROR |
| `atlas-pay-5p.md` | MD | 3 899 | OK | 0¹ | 6 | 3 749 | ERROR |
| `helios-rec-10p.pdf` | PDF | 18 824 | OK | **10** | 17 | 8 788 | ERROR |
| `helios-rec-10p.md` | MD | 9 451 | OK | 0¹ | 14 | 9 126 | ERROR |
| `orion-platform-13p.pdf` | PDF | 23 670 | OK | **13** | 23 | 11 649 | ERROR |
| `orion-platform-13p.md` | MD | 12 439 | OK | 0¹ | 19 | 12 037 | ERROR |

¹ Por diseño, el extractor Markdown no asigna páginas (`page_count=0`); el PDF sí conserva el conteo real.
Los PDF fueron verificados con `pypdf`: 5, 10 y 13 páginas exactas, con encabezado y pie “Página X de N”.

Detalle completo en `evidencias/validacion_documentos.md` y `evidencias/validacion_documentos.json`.
La recomendación de uso por escenario está en **`GUIA_DOCUMENTOS_PRUEBA.md`**.

---

## 6. Recomendaciones priorizadas (no aplicadas)

> No se realizó ningún cambio en el código. Estas son acciones sugeridas para el equipo.

### P0 — Bloqueante de demo

1. **Implementar `GenerationOrchestrator.generate_content()`**: construir el prompt con
   `generation/prompts/generacion_v1.txt`, invocar `provider.generate()`, validar el JSON y mapearlo a
   `ContenidoAdaptado`. Mientras no exista, **lanzar `NotImplementedError`** para que el *fallback* a
   mock se active en lugar de devolver `None`.
2. **Validar el retorno en `PipelineOrchestrator.run_adaptation()`**: si `content is None`, activar el
   *fallback* mock o lanzar `LLMProviderError`; no acceder a `.cuerpo` sin comprobación.
3. **Añadir un test unitario de contrato** para `generate_content()` (tipo de retorno, campos no vacíos,
   JSON inválido → excepción) y otro que garantice `status=PARTIAL` + `MOCK_NOTICE` en modo mock.
4. **Re-ejecutar la suite completa** y actualizar el informe de auditoría solo con la salida real de
   `pytest -q`.

### P1 — Consistencia y confiabilidad

5. Regenerar/limpiar `README.md` (eliminar la concatenación y unificar la descripción de
   `fidelidad_score`).
6. Alinear `informe_audit`, `TRACEABILITY`, `AUDIT.md` y `TESTING_STRATEGY` con el estado real; marcar
   claramente qué es histórico y qué es vigente.
7. Aislar el test de *fallback*: usar `monkeypatch`, limpiar `os.environ` y `get_settings.cache_clear()`.
8. Quitar `namespace`/bucket reales de `.env.example` y `docker-compose.yml` (dejarlos como placeholders).
9. Actualizar los 3 escenarios de demo a `READY` usando los documentos entregados.

### P2 — Calidad y operación

10. Elevar cobertura de los caminos reales (OCI, Gemini, `prompt_loader`) o eliminar código muerto.
11. Ejecutar la suite en Python 3.11 (versión del CI) además de 3.12.
12. Endurecer imágenes Docker (sin `requirements-dev`, usuario no root, sin montar claves SSH en la UI).

---

## 7. Evidencias generadas

| Archivo | Contenido |
|---|---|
| `evidencias/pytest_final.txt` | Salida completa de la suite final (282 passed, 8 failed) |
| `evidencias/junit_final.xml` | Resultado JUnit para trazabilidad automática |
| `evidencias/pytest_fallos_detalle.txt` | Trazas largas de los fallos representativos |
| `evidencias/ruff.txt` | Resultado del lint (`All checks passed!`) |
| `evidencias/import_check.txt` | Verificación de importación de todos los módulos |
| `evidencias/coverage.txt` / `coverage.json` | Cobertura por archivo (86 % total) |
| `evidencias/repro_01.txt` | Reproducción independiente del fallo en `repro/repro_01_pipeline.py` |
| `evidencias/smoke_api.md` / `smoke_api.json` | Evidencia HTTP del flujo (`/health`, `/ingest`, `/adapt`, errores) |
| `evidencias/validacion_documentos.md` / `.json` | Ingesta y adaptación de los 6 documentos |
| `documentos_prueba/*.pdf`, `*.md` | Los 6 artefactos de prueba |
| `GUIA_DOCUMENTOS_PRUEBA.md` | Para qué escenario sirve cada documento |

### Limitaciones de la validación

- No se probó contra OCI real (sin credenciales ni paquete `oci`; `STORAGE_PROVIDER=mock`).
- No se probaron proveedores Gemini/Cohere reales (sin API keys; toda la suite usa mocks).
- No se ejecutó el CI de GitHub Actions; se replicaron sus comandos localmente con Python 3.12.
- No hay historial Git, por lo que “última integración” se interpreta como el estado documentado por el
  equipo, no como un commit verificable.
