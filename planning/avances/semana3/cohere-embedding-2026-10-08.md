[cohere-embedding-2026-10-08.md](https://github.com/user-attachments/files/33210660/cohere-embedding-2026-10-08.md)
# Evidencia: embeddings, recuperación y flashcards con Cohere

- Fecha de registro: 2026-10-08
- Prueba ejecutada: `tests/integration/test_embedig_agente.py::test_embedig_agente`
- Resultado: **PASSED**
- Evidencia de ejecución: `1 passed, 1 warning in 4.54s`
- Proveedores probados: Cohere para embeddings y para generación LLM, usando la
  configuración disponible en `.env`.

## Escenario

Texto sobre Virtual Cloud Network (VCN) en Oracle Cloud Infrastructure,
con los parámetros del proyecto:

- Perfil: Principiante / Transición de Carrera
- Formato: Flashcards de Memorización
- Nicho: General
- Tema de recuperación: primeros 200 caracteres del texto VCN

## Comprobaciones realizadas

- Cohere devolvió un embedding del documento con las dimensiones configuradas.
- Los valores del vector fueron finitos y no todos cero.
- El servicio de recuperación usó el perfil, nicho y tema de la solicitud.
- El fragmento VCN fue recuperado del vector store de prueba.
- El LLM de Cohere generó una respuesta JSON válida para `ContenidoAdaptado`.
- El campo `cuerpo` no quedó vacío, menciona VCN y contiene tres preguntas y
  tres respuestas.
- La respuesta respetó el contrato del proyecto, que requiere `cuerpo` como
  texto; el test valida el JSON con `ContenidoAdaptado`.

El formato se configura en la solicitud, pero no se usa para crear el embedding
de consulta; se aplica al generar el contenido con el LLM.

## Flashcards generadas por Cohere

Estas son las tres tarjetas de la respuesta real capturada durante la ejecución:

1. **Pregunta:** ¿Qué es una VCN?  
   **Respuesta:** Una red privada y personalizable en Oracle Cloud Infrastructure.

2. **Pregunta:** ¿Qué elementos se pueden configurar en una VCN?  
   **Respuesta:** Subredes públicas y privadas, tablas de enrutamiento, Internet
   Gateways, NAT Gateways y Security Lists.

3. **Pregunta:** ¿Qué controlan las Security Lists en una VCN?  
   **Respuesta:** El tráfico de entrada (ingress) y salida (egress) mediante reglas.

## Ejecución

La prueba se ejecutó con las llamadas en vivo habilitadas mediante
`RUN_COHERE_LIVE_TESTS=1` y la impresión del resultado habilitada mediante
`COHERE_LIVE_TEST_SHOW_OUTPUT=1`, con `pytest -v -s`. La salida incluyó una
advertencia deprecada originada en el SDK de Cohere/Pydantic (`__fields__`); no
provocó que la prueba fallara. No se registra ni incluye la clave de API.

## Pruebas con la UI existente en el repo
<img width="1315" height="531" alt="image" src="https://github.com/user-attachments/assets/8f22e01c-6417-4b53-910e-3f5e9d1b9139" />

<img width="1340" height="596" alt="image" src="https://github.com/user-attachments/assets/eebd1ec6-7530-4157-a24f-59cba5b613da" />

<img width="1345" height="634" alt="image" src="https://github.com/user-attachments/assets/93b06c1c-8cb6-41a0-b109-f417fb89142b" />

<img width="1281" height="624" alt="image" src="https://github.com/user-attachments/assets/814e039a-e974-4e75-9ca3-7995fba2477c" />





