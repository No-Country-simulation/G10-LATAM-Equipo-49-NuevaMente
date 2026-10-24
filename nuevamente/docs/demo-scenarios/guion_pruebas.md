 Guion de pruebas — Generación de contenido adaptado (3 escenarios)

Basado en `guia_documentos_demo.md` y los escenarios DEMO-001, DEMO-002 y DEMO-003 · Fecha de elaboración: 2026-10-23

## 1. Objetivo y alcance

Validar que el sistema genera contenido **adaptado al perfil y al formato** a partir de un único documento técnico (PDF o Markdown), reutilizando el mismo `document_id` y manteniendo la fidelidad al texto fuente.

| Escenario | Perfil | Formato | Qué valida |
| --- | --- | --- | --- |
| **E1 — DEMO-001** | Principiante / Transición de Carrera | Guía Práctica Paso a Paso (Tutorial) | RF-001, RF-009, RF-010, RF-014, RF-016, RF-017, RF-018 |
| **E2 — DEMO-002** | Líder Técnico / Arquitecto (opcional: Gestor / Ejecutivo) | Resumen Ejecutivo (TL;DR) | RF-009, RF-010, CU-002 (reutilización de embeddings) |
| **E3 — DEMO-003** | Principiante / Transición de Carrera (igual que E1) | Quiz | RF-012, REQ-24 (≥ 2 formatos pedagógicos distintos) |

La lógica es una prueba controlada: **E1 vs E2 cambia solo el perfil** (más el formato TL;DR) y **E1 vs E3 cambia solo el formato** (mismo perfil).

## 2. Documento de prueba recomendado

**Principal: `helios-rec-10p.md`** (10 páginas equivalentes, densidad media, 14 chunks). Tiene secciones diferenciadas (API, ranking, seguridad, evaluación) y suficiente sustancia para los 3 formatos, sin depender del parser PDF.

**Variante de paridad: `helios-rec-10p.pdf`** (10 páginas, 17 chunks). Repetir los 3 escenarios con el PDF permite comparar resultados y verificar que `sources[].page` apunta a páginas reales.

Alternativas: `orion-platform-13p.md` si se quiere enfatizar claims técnicos (lag de Kafka, rollback, RTO/RPO); no usar `atlas-pay-5p` para estos escenarios, porque su baja densidad es para probar `NO_CONTEXT`.

## 3. Precondiciones

1. API levantada (`run_api.bat` o `./run_api.sh`) en `http://127.0.0.1:8000`.
2. UI Streamlit levantada (`run_ui.bat` o `./run_ui.sh`) si se prueba por interfaz.
3. Documentos disponibles en la carpeta de pruebas (la guía menciona `documentos_demo/` y los comandos usan `documentos_prueba/`: confirmar la ruta real antes de empezar).
4. **DEMO-000 resuelto:** los escenarios figuran como CONTRACT-ONLY y dependen de seleccionar/preparar los documentos de referencia. Este guion usa los documentos de la guía como esa referencia.
5. Registrar el entorno: versión de la API, modelo de embeddings, modelo generador y fecha.

## 4. Paso 0 — Ingesta (una sola vez)

**Acción (API):**

```bash
curl -F "file=@documentos_prueba/helios-rec-10p.md" http://127.0.0.1:8000/ingest
```

**Acción (UI):** pantalla de carga → subir `helios-rec-10p.md`.

**Resultado esperado:**

- HTTP 201 y un `document_id` con formato `doc_...` (anotarlo: se reutiliza en E1, E2 y E3).
- `page_count = 0` (por diseño en Markdown) y `chunk_count ≈ 14`.
- Confirmación de que el original quedó almacenado en OCI.
- Sin chunks vacíos ni errores de codificación (acentos, tablas y guiones largos intactos).

**Criterio de paso:** se obtiene `document_id` y el conteo de chunks está en el rango esperado.

## 5. Escenario 1 — Perfil Principiante + Tutorial (DEMO-001)

**Objetivo:** contenido educativo, didáctico y anclado al documento para alguien que no domina el tema.

### Paso 1.1 — Configurar y generar

```bash
curl -X POST http://127.0.0.1:8000/adapt \
  -H "Content-Type: application/json" \
  -d '{"document_id":"doc_...","perfil":"Principiante / Transición de Carrera","formato":"Guía Práctica Paso a Paso (Tutorial)","nicho":"General"}'
```

En la UI: elegir los mismos tres valores. Debe mostrarse "generando...".

### Paso 1.2 — Consultar el resultado

```bash
curl http://127.0.0.1:8000/adapt/job_...
```

### Paso 1.3 — Revisar fidelidad

Revisar el score de fidelidad y la lista de claims no sustentados (`claims_no_soportados`).

### Verificaciones

| # | Verificación | Resultado esperado |
| --- | --- | --- |
| 1.1 | El job se crea y termina | Estado final exitoso, sin timeout |
| 1.2 | Estructura de Tutorial | Pasos numerados, objetivo inicial, orden lógico |
| 1.3 | Adaptación al perfil | Lenguaje sencillo, términos técnicos explicados, analogías o ejemplos |
| 1.4 | Anclaje al documento | Todo el contenido proviene de Helios Rec (arquitectura, API, ranking, etc.); no aparecen datos inventados |
| 1.5 | Fuentes | `sources` presentes, con sección o página coherente |
| 1.6 | Fidelidad | Score visible y **≥ 0,9** (DT-11); claims no sustentados listados explícitamente si existen |
| 1.7 | Persistencia | Contenido y JSON guardados en OCI junto con el original |

**Guardar** el resultado de E1 como línea base para las comparaciones.

## 6. Escenario 2 — Líder Técnico / Ejecutivo + TL;DR (DEMO-002)

**Objetivo:** demostrar que el **mismo documento** produce contenido perceptiblemente distinto según el perfil.

### Paso 2.1 — Generar con el mismo `document_id`

```bash
curl -X POST http://127.0.0.1:8000/adapt \
  -H "Content-Type: application/json" \
  -d '{"document_id":"doc_...","perfil":"Líder Técnico / Arquitecto","formato":"Resumen Ejecutivo (TL;DR)","nicho":"General"}'
```

No volver a subir el archivo: se debe reutilizar el `document_id` de E1 (CU-002).

### Paso 2.2 — Repetir con el perfil Gestor (opcional)

Cambiar `perfil` a "Gestor / Ejecutivo (No Técnico)" y mantener TL;DR. Sirve como tercer punto de comparación de perfiles.

### Verificaciones

| # | Verificación | Resultado esperado |
| --- | --- | --- |
| 2.1 | Reutilización de embeddings | No hay nueva ingesta ni nuevo `document_id`; la generación es más rápida que la primera ingesta |
| 2.2 | Estructura TL;DR | Breve, con conclusiones y puntos clave al inicio; claramente más corto que el Tutorial |
| 2.3 | Adaptación al perfil | Tono ejecutivo/arquitectónico: decisiones de diseño, riesgos, compromisos (trade-offs) y métricas; sin explicaciones básicas |
| 2.4 | Diferencia con E1 | Contenido perceptiblemente distinto en tono, profundidad y vocabulario |
| 2.5 | Fidelidad | Score ≥ 0,9; cifras y nombres coinciden con el documento |
| 2.6 | Fuentes | Pueden diferir de E1 (otras secciones recuperadas por el perfil) |

## 7. Escenario 3 — Mismo perfil, formato alterno: Quiz (DEMO-003)

**Objetivo:** demostrar que el formato cambia la **estructura** de salida manteniendo el perfil de E1.

### Paso 3.1 — Generar

```bash
curl -X POST http://127.0.0.1:8000/adapt \
  -H "Content-Type: application/json" \
  -d '{"document_id":"doc_...","perfil":"Principiante / Transición de Carrera","formato":"Quiz","nicho":"General"}'
```

Si el catálogo de formatos incluye "Resumen" o "Flashcards", puede ejecutarse una variante adicional con el mismo procedimiento.

### Verificaciones

| # | Verificación | Resultado esperado |
| --- | --- | --- |
| 3.1 | Estructura Quiz | Preguntas con opciones y respuesta correcta (o retroalimentación), no pasos de tutorial |
| 3.2 | Perfil conservado | El nivel de las preguntas y el lenguaje coinciden con Principiante |
| 3.3 | Corrección | La respuesta marcada como correcta se puede comprobar en el documento fuente |
| 3.4 | Diferencia con E1 | Estructura de salida distinta (valida RF-012 y REQ-24: al menos 2 formatos pedagógicos distintos) |
| 3.5 | Fidelidad | Score ≥ 0,9; sin preguntas sobre temas que el documento no menciona |

## 8. Comparación cruzada

Completar tras ejecutar los tres escenarios.

| Criterio | E1 (Principiante + Tutorial) | E2 (Líder + TL;DR) | E3 (Principiante + Quiz) |
| --- | --- | --- | --- |
| Longitud aproximada (palabras) |  |  |  |
| Estructura |  |  |  |
| Nivel de vocabulario |  |  |  |
| Secciones citadas en `sources` |  |  |  |
| Score de fidelidad |  |  |  |
| Claims no soportados |  |  |  |
| Tiempo de generación |  |  |  |

**Conclusiones esperadas:**

- **E1 ≠ E2:** cambia el perfil, y el contenido es distinto en tono y profundidad con los mismos hechos.
- **E1 ≠ E3:** cambia el formato, y la estructura es distinta con el mismo nivel.
- Ningún escenario introduce datos que no estén en el documento.

## 9. Pruebas complementarias (opcionales)

1. **Paridad PDF ↔ MD:** repetir E1–E3 con `helios-rec-10p.pdf`. Esperado: contenido equivalente, `page_count = 10` y `sources[].page` correctos.
2. **Reingesta:** subir el mismo archivo dos veces. Esperado: `document_id` nuevo y sin duplicados lógicos en el índice.
3. **Control de no invención:** con `atlas-pay-5p`, pedir un Tutorial. Esperado: respuesta `PARTIAL` o `NO_CONTEXT` si el contexto es insuficiente, sin relleno inventado.
4. **Variación de nicho:** repetir E1 con un nicho distinto de "General" y comprobar que el enfoque cambia sin salirse del documento.
5. **Persistencia:** reiniciar la API y volver a consultar un job o generar de nuevo; verificar que el índice se reconstruye (`_ensure_indexed`).

## 10. Criterios globales de aceptación

- Los 3 escenarios terminan sin errores y generan contenido consultable.
- Fidelidad ≥ 0,9 en todos, con claims no sustentados listados cuando existan.
- E1, E2 y E3 son perceptiblemente distintos entre sí, según la matriz de comparación.
- Un solo `document_id` sirve para los tres escenarios.
- Original y JSON de resultado persistidos en OCI.

## 11. Registro de ejecución

| Escenario | Fecha | Responsable | document\_id | job\_id | Resultado (OK / Falla) | Observaciones |
| --- | --- | --- | --- | --- | --- | --- |
| Ingesta |  |  |  |  |  |  |
| E1 |  |  |  |  |  |  |
| E2 |  |  |  |  |  |  |
| E3 |  |  |  |  |  |  |
