# Suite de auditoría — NuevaMente

Pruebas que convierten cada hallazgo del informe en una regresión **ejecutable y determinista**
(sin red, sin credenciales, sin datos reales: cada test usa su propia base SQLite y su propio
storage temporal, vía el `conftest.py` existente).

> **Estado 2026-10-15:** se aplicaron las correcciones del informe y **se retiraron todos los
> marcadores `xfail`**: cada prueba es ahora una regresión permanente (`PASSED`). Salida esperada:
> `pytest tests -q` → **290 passed** (con `ruff` en el `PATH`; si no, 1 `SKIPPED` en
> `test_audit_016`, que comprueba el lint).

## Convención de resultados
| Resultado | Significado | Qué hacer |
|---|---|---|
| `XFAIL` | Defecto confirmado **todavía presente** (`xfail(strict=True)`) | Nada: es el estado actual esperado |
| `XPASS(strict)` → **FAILED** | El defecto **ya se corrigió** | Quitar el marcador `xfail` de ese test; pasa a ser regresión permanente |
| `PASSED` (sin marcador) | Control positivo: comportamiento correcto que no debe romperse | Si falla, es una regresión nueva |
| `SKIPPED` | Falta una herramienta (p. ej. `ruff`) | Instalar `requirements-dev.txt` |

## Instalación
```bash
cd backend
python -m venv .venv && source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements-dev.txt pytest-cov            # incluye python-multipart y reportlab (AUD-005, AUD-006)
```

## Ejecución
```bash
pytest tests/audit -q -rxXs                                # solo la suite de auditoría
pytest tests -q -rxXs --cov=src --cov-report=term-missing --cov-report=html:reports/cov \
       --junitxml=reports/junit.xml                        # todo + cobertura + reporte JUnit
python ../repro/repro_01_pipeline.py                       # evidencia numérica (ver tabla)
```
Salida esperada (código corregido): `pytest tests -q` → **290 passed** (o 289 passed + 1 skipped
si `ruff` no está en el `PATH`; `test_audit_016` lo verifica).

## Diagnóstico
- `ModuleNotFoundError: fastapi/httpx/chromadb` → faltan dependencias; instalar `requirements-dev.txt`.
- Un `XFAIL` que falla por un error distinto a `AssertionError` (p. ej. `ImportError`) **no** prueba el defecto:
  ejecutar con `-rx` y revisar el motivo antes de concluir.
- `test_aud_008` (hilos) puede tardar hasta 5 s; si en una máquina muy lenta no reproduce la carrera
  aparecerá como `XPASS`: repetir la ejecución antes de retirar el marcador.
- Las pruebas de Gemini simulan el SDK con un módulo falso; no llaman a Google.

## Mapa hallazgo → prueba → script de evidencia
| ID | Prueba | Script (`repro/`) |
|---|---|---|
| AUD-001 | `test_audit_rag::test_aud_001_*` | `repro_01_pipeline.py` (H-02) |
| AUD-002 | `test_audit_rag::test_aud_002_*`, `test_audit_api::test_aud_002_*` | `repro_01_pipeline.py` (H-03) |
| AUD-003 | `test_audit_providers::test_aud_003_*` | `repro_04_providers.py` (H-10) |
| AUD-004 | `test_audit_rag::test_aud_004_*` | `repro_03_state.py` (H-04) |
| AUD-005 / 006 | `test_audit_contracts::test_aud_005_*`, `test_aud_006_*` | — (análisis estático) |
| AUD-007 | `test_audit_rag::test_aud_007_*` | `repro_03_state.py` (H-05) |
| AUD-008 | `test_audit_rag::test_aud_008_*` | `repro_03_state.py` (H-07) |
| AUD-009 | `test_audit_rag::test_aud_009_*` | `repro_01_pipeline.py` (H-06) |
| AUD-010 | `test_audit_rag::test_aud_010_*` | `repro_02_threshold.py` |
| AUD-011 | `test_audit_providers::test_aud_011_*` (3) | `repro_04_providers.py` (H-09) |
| AUD-012 / 013 / 014 | `test_audit_providers::test_aud_012_*`, `_013_*`, `_014_*` | `repro_03_state.py` (H-08), `repro_04_providers.py` |
| AUD-015 | `test_audit_contracts::test_aud_015_*` | — |
| AUD-016 | `test_audit_contracts::test_aud_016_*` (requiere `ruff`) | — |
| AUD-019 | `test_audit_contracts::test_aud_019_*` | `repro_05_logs.py` |
| AUD-022 | `test_audit_providers::test_aud_022_*` (2) | `repro_04_providers.py` |
| (sin hallazgo) | rendimiento de PDF y SQLite: medidos y **no** son defecto | `repro_06_perf.py` |

AUD-017 (calidad de la suite existente), AUD-018 (jobs huérfanos), AUD-020 y AUD-021 se documentan en
el informe; no tienen prueba automatizable determinista.
