# Resumen: integración de Cohere en NuevaMente

Se integró Cohere como proveedor configurable para **generación de contenido** y **embeddings**, manteniendo Gemini y el proveedor mock disponibles.

## Cambios realizados

- Se agregó el proveedor Cohere de embeddings en `cohere.py`. Implementa embeddings de documentos y consultas, lotes de hasta 96 textos y reintentos ante errores.
- Se registró Cohere en la factory de embeddings en `factory.py`.
- La generación de texto Cohere quedó seleccionable mediante la factory de `generation/factory.py`, usando la implementación existente en `generation/providers/cohere.py`.
- Se añadieron la configuración de Cohere y su dimensión de embeddings a `config.py`. La colección Chroma usa la dimensión activa configurada en `vectorstore/client.py`.
- Se declaró el SDK en `requirements.txt` y se documentaron variables de ejemplo en `.env.example`.
- Se agregaron pruebas unitarias de los proveedores y se actualizó la trazabilidad en `TRACEABILITY.md`.

## Configuración de ejecución

En `.env` se configuraron los selectores de proveedor para Cohere y su clave de API, que debe permanecer secreta y no incluirse en el repositorio. También se ajustó el modelo de generación: `command-r-plus` estaba retirado y Cohere respondía `404`; al usar `command-a-03-2025`, la generación respondió correctamente.

Después de modificar `.env` o instalar dependencias, se debe reiniciar el backend para que tome los cambios.

## Resultado verificado

La demo completó correctamente el flujo:

1. La ingesta del documento terminó con `201 Created`.
2. Cohere generó embeddings mediante `/v2/embed` con respuesta `200 OK`.
3. Cohere generó el contenido mediante `/v2/chat` con respuesta `200 OK`.
4. La API devolvió `SUCCESS` y la demo informó que la adaptación terminó correctamente.

Las pruebas automatizadas de Cohere y las de no regresión Gemini/mock dieron **33 pasadas**. Se ejecutaron con clientes falsos; la integración real quedó confirmada después con la demo.

## Consideraciones

- La integración permite seleccionar Cohere para LLM y embeddings, pero las evaluaciones de fidelidad del proyecto siguen siendo provisionales; `SUCCESS` no debe interpretarse por sí solo como garantía de fidelidad.
- Si `VECTORSTORE_PROVIDER=memory`, el índice vectorial se pierde al reiniciar el backend. Chroma permite persistencia local.
- La salida con acentos deformados en la terminal es un problema de codificación separado de la integración con Cohere.
