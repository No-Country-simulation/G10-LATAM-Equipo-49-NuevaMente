# DEMO-001 — Perfil Principiante (placeholder de contrato)

**Estado: CONTRACT-ONLY.** No hay documento de referencia todavía —
DEMO-000 ("seleccionar/preparar los 3 documentos técnicos de referencia")
está pendiente y es prerrequisito de este escenario.

**Demuestra (una vez implementado):** RF-001, RF-009, RF-010, RF-014,
RF-016, RF-017, RF-018.

## Paso 1 — Subir documento
Acción prevista: subir el documento de referencia por la interfaz web.
Resultado esperado: se muestra `document_id` y confirmación de que el
original quedó en OCI.

## Paso 2 — Configurar generación
Acción prevista: elegir perfil "Principiante / Transición de Carrera",
formato "Guía Práctica Paso a Paso (Tutorial)" y nicho "General".
Resultado esperado: la interfaz muestra "generando..." y luego el
contenido adaptado.

## Paso 3 — Revisar fidelidad
Acción prevista: revisar el score de fidelidad mostrado junto al resultado.
Resultado esperado: score visible (≥0.9 esperado, DT-11) y, si existieran,
claims no sustentados listados explícitamente.

**Resultado final esperado:** contenido educativo coherente con el
perfil, anclado al documento fuente y persistido en OCI (original + JSON).
