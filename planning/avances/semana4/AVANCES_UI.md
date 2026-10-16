# Avances de la interfaz — NuevaMente

**Equipo:** G10-LATAM-Equipo-49-NuevaMente.
**Responsable:** Santiago Guarnizo.
**Roles asignados:** LLM Engineer, Frontend.
**Fecha:** 16 de octubre de 2026.
**Módulo:** Interfaz web (Streamlit) — `ui/`.

---

# 1. Avances de mi trabajo

## 1.1. Desarrollo de los estilos globales de la interfaz

**Archivo:** `ui/components/styles.py`

Se desarrolló y ajustó la hoja de estilos globales de NuevaMente para adaptar la apariencia de Streamlit al diseño establecido en Figma.

**Mejoras implementadas:**

- Definición y organización de la paleta de colores de la interfaz mediante variables CSS.
- Personalización de los colores principales, fondos, bordes y textos.
- Diseño visual de la barra lateral, utilizando un fondo azul claro y una estructura coherente con la identidad gráfica de NuevaMente.
- Ajustes de distribución, márgenes, espacios internos y alineación del contenido principal.
- Personalización de tamaños de fuente, pesos tipográficos y espaciados para títulos, descripciones y textos.
- Modificación de los estilos predeterminados de los componentes de Streamlit para acercarlos al diseño de referencia.
- Ajustes en elementos de la interfaz, como botones, contenedores, tarjetas y componentes de carga de archivos.
- Corrección de estilos que afectaban la visualización de elementos propios de Streamlit, incluyendo el encabezado, el pie de página y la barra lateral.
- Organización de los estilos para mantener una apariencia consistente entre las diferentes pantallas.

## 1.2. Implementación de la pantalla de carga de archivos

**Archivo:** `ui/components/upload_view.py`

Se desarrolló y ajustó la pantalla inicial, donde el usuario puede cargar el documento técnico que desea transformar en contenido educativo.

**Mejoras implementadas:**

- Adaptación de la pantalla al diseño definido en Figma.
- Organización visual del área de carga para facilitar la identificación de la acción principal.
- Incorporación y posicionamiento de los elementos visuales de la pantalla, incluyendo el icono, el título y el texto descriptivo.
- Ajustes en la ubicación del selector de archivos para mantener una distribución ordenada.
- Personalización del componente de carga nativo de Streamlit mediante CSS.
- Ajustes para ocultar la etiqueta nativa del archivo cargado y evitar que aparezca duplicada.
- Implementación de una presentación independiente del nombre del archivo seleccionado.
- Personalización de la tipografía, alineación y separación del nombre del archivo.
- Correcciones de márgenes y espacios para mejorar la composición visual.
- Ajustes de los elementos de carga para mantener una experiencia más clara y coherente con el diseño de la plataforma.

## 1.3. Implementación de la pantalla de selección de opciones

**Archivo:** `ui/components/selection_view.py`

Se desarrolló la pantalla que permite configurar la adaptación del documento según las necesidades del usuario.

**Mejoras implementadas:**

- Organización de las opciones en tres secciones:
  - Perfil del destinatario.
  - Formato pedagógico de salida.
  - Nicho o contexto de aplicación.
- Implementación de tarjetas de selección para facilitar la elección de las opciones.
- Incorporación de estados visuales para diferenciar las tarjetas seleccionadas de las no seleccionadas.
- Organización de las tarjetas mediante columnas para aprovechar el espacio disponible.
- Ajustes de tamaños, separación y distribución de los elementos.
- Adaptación de la disposición de las tarjetas para pantallas de menor tamaño, evitando que el contenido se desborde horizontalmente.
- Integración de las selecciones con el estado de la aplicación.
- Separación entre las etiquetas mostradas al usuario y los valores que requiere el backend.
- Integración del botón **Siguiente** con la solicitud de adaptación del documento.
- Corrección de errores relacionados con los valores de perfil y formato enviados al backend.

## 1.4. Integración del flujo entre las pantallas

**Archivos:** `ui/app.py`, `ui/components/upload_view.py`, `ui/components/selection_view.py`, `ui/components/loading_view.py`

Se trabajó en la conexión de las diferentes pantallas para que la aplicación funcione como un flujo continuo.

La interfaz está organizada mediante cinco estados principales:

1. Carga del archivo.
2. Selección de opciones.
3. Procesamiento.
4. Resultados.

**Mejoras implementadas:**

- Organización de la navegación mediante `st.session_state["stage"]`.
- Conexión entre la carga del archivo y la pantalla de selección.
- Integración del envío de las opciones seleccionadas al backend.
- Almacenamiento de los identificadores de procesamiento necesarios para consultar los resultados.
- Ajustes en las transiciones entre pantallas para evitar que permanezcan visibles componentes de una pantalla anterior.
- Manejo del retorno a las pantallas correspondientes cuando se producen errores.
- Organización del flujo para facilitar la continuidad del proceso desde la carga del documento hasta la generación del resultado.

## 1.5. Implementación de la pantalla de procesamiento

**Archivo:** `ui/components/loading_view.py`

Se desarrolló la pantalla que informa al usuario sobre el avance del procesamiento del documento.

**Mejoras implementadas:**

- Creación de una tarjeta central con el mensaje de procesamiento.
- Incorporación de una barra de progreso con una pista de fondo y un indicador de avance.
- Implementación de cinco etapas visuales:
  - Lectura y análisis del contenido.
  - Aplicación de las configuraciones seleccionadas.
  - Generación del contenido adaptado.
  - Organización de los resultados.
  - Finalización del proceso.
- Incorporación de indicadores visuales para distinguir las etapas completadas, la etapa actual y las pendientes.
- Inclusión de un recuadro informativo sobre la adaptación del contenido al perfil, formato y contexto seleccionados.
- Ajuste de la tipografía, distribución y espaciado para acercar la pantalla al diseño de Figma.
- Manejo de la duración mínima de visualización para evitar que el proceso desaparezca demasiado rápido cuando el backend responde inmediatamente.

## 1.6. Integración de la barra de progreso con el backend

**Archivos:** `ui/components/loading_view.py`, `ui/api_client.py`

Se conectó la pantalla de procesamiento con las consultas periódicas al backend para comprobar el estado de la adaptación.

**Mejoras implementadas:**

- Consulta del resultado mediante `api_client.poll_adapt_result(job_id)`.
- Actualización periódica de la interfaz mientras el procesamiento continúa.
- Uso de `st.fragment(run_every=...)` para actualizar la pantalla sin volver a ejecutar toda la aplicación en cada consulta.
- Actualización progresiva de la barra de carga durante la espera.
- Transición automática a la pantalla de resultados cuando el procesamiento finaliza.
- Manejo de errores que pueden ocurrir durante las consultas al backend.
- Corrección del problema que dejaba visible la pantalla de selección detrás de la pantalla de procesamiento.

## 1.7. Adaptación responsive de la interfaz

**Archivos:** `ui/components/styles.py`, `ui/components/upload_view.py`, `ui/components/selection_view.py`, `ui/components/loading_view.py`

Se realizaron ajustes de presentación para mejorar el comportamiento de la interfaz en diferentes tamaños de pantalla.

**Mejoras implementadas:**

- Ajustes en la distribución de los componentes para aprovechar el espacio disponible.
- Adaptación de las tarjetas de selección para que se reorganizen en pantallas estrechas.
- Corrección de desbordamientos horizontales en la pantalla de selección.
- Ajustes de espaciado y alineación en los componentes principales.
- Conservación de los tamaños tipográficos definidos durante el trabajo de diseño.
- Revisión de la presentación de las pantallas para mantener la coherencia visual entre los diferentes estados del flujo.

## 1.8. Verificación de calidad del código

**Archivos revisados:** `ui/app.py`, `ui/components/loading_view.py`, `ui/components/selection_view.py`, `ui/components/upload_view.py`

Se realizaron verificaciones para mejorar la calidad y consistencia del código de la interfaz.

**Acciones realizadas:**

- Ejecución de Ruff para detectar problemas de estilo y organización del código.
- Corrección del orden de las importaciones en los archivos señalados.
- Revisión de los cambios preparados para Git.
- Ejecución de `git diff --cached --check` para comprobar que no hubiera errores de espacios en blanco.
- Verificación final de Ruff hasta obtener el resultado `All checks passed!`.

**Comando utilizado:**

```bash
python -m ruff check --config backend/pyproject.toml backend/src backend/tests ui
```

## 1.9. Revisión de dependencias para el despliegue

**Archivos relacionados:** `backend/requirements.txt`, `ui/api_client.py`

Durante las pruebas de despliegue se identificó un error `ModuleNotFoundError: No module named 'httpx'`.

Se verificó que `httpx` ya estaba declarado en `backend/requirements.txt`, por lo que se identificó la necesidad de revisar qué archivo de dependencias está utilizando la plataforma de despliegue.

**Estado:** pendiente de verificación del despliegue con las dependencias correctamente configuradas.

## 1.10. Archivos principales de mi trabajo

| Archivo | Avance realizado |
|---|---|
| `ui/components/styles.py` | Desarrollo y personalización de los estilos globales de la interfaz. |
| `ui/components/upload_view.py` | Diseño y ajustes de la pantalla de carga de archivos. |
| `ui/components/selection_view.py` | Tarjetas de selección, estados visuales, integración con el backend y ajustes responsive. |
| `ui/components/loading_view.py` | Diseño de la pantalla de procesamiento y barra de progreso dinámica. |
| `ui/api_client.py` | Integración de las consultas al backend para comprobar el estado y obtener resultados. |
| `ui/app.py` | Organización de los estados y transiciones principales de la aplicación. |
| `backend/requirements.txt` | Revisión de las dependencias relacionadas con el problema de despliegue. |

## 1.11. Pruebas realizadas

- Verificación visual de la pantalla de carga de archivos.
- Comprobación de la presentación del nombre del archivo seleccionado.
- Pruebas de selección del perfil, formato pedagógico y contexto.
- Verificación del envío de las opciones al backend.
- Comprobación de la actualización de la barra de progreso.
- Prueba de la transición desde el procesamiento hasta los resultados.
- Revisión de la distribución de las tarjetas en pantallas estrechas.
- Ejecución de Ruff hasta obtener `All checks passed!`.
- Identificación del problema de dependencias durante el despliegue, pendiente de validación final.

---

# 2 Avances de la interfaz — NuevaMente

**Equipo:** G10-LATAM-Equipo-49-NuevaMente.
**Responsable:** Viviana Hurtado.
**Roles asignados:** UX/UI Designer, Frontend.
**Fecha:** 15 de octubre de 2026.
**Módulo:** Interfaz web (Streamlit) — `ui/`.

## Resumen

Se hicieron tres mejoras en la interfaz:

1. Botón **Volver** en la pantalla de selección de opciones.
2. Barra superior **funcional** en la pantalla de resultados (Vista previa / Markdown / Descargar).
3. Logo del sidebar en **SVG** (más nítido) y **favicon** con el logo de la "N".

---

## 2.1. Botón "Volver" en la pantalla de selección

**Archivo:** `ui/components/selection_view.py`

### Problema
Una vez en la pantalla "Seleccionar opciones", no había forma de regresar a la pantalla de carga para cambiar el archivo.

### Cambios
- Se reescribió `_render_page_header()` para mostrar el título a la izquierda y el botón **← Volver** a la derecha, en la misma línea.
- Al pulsar el botón, `st.session_state["stage"]` pasa a `"upload"` y se ejecuta `st.rerun()`.
- Se agregaron estilos propios (`.st-key-selection_header`, `.st-key-selection_back`): botón con fondo blanco y borde azul, para diferenciarlo del botón principal "Siguiente →".
- Se añadió una regla en el `@media (max-width: 600px)` para que el encabezado no se rompa en móvil (el CSS existente convertía todos los `stHorizontalBlock` en una cuadrícula de 2 columnas iguales).

### Comportamiento
- El stepper del sidebar vuelve a marcar "Cargar archivo" automáticamente, porque se calcula a partir de `stage`.
- `st.session_state["ingest"]` se conserva, pero se sobrescribe al pulsar "Siguiente" con un nuevo archivo, por lo que no hay conflicto.

---

## 2.2. Barra superior funcional en resultados

**Archivo:** `ui/components/result_view.py`

### Problema
La barra gris superior (Vista previa · Markdown · Descargar) estaba hecha con HTML estático, por lo que **ninguno de sus botones hacía nada**. Debajo existían además unas pestañas `st.tabs` que sí funcionaban, lo que generaba dos controles duplicados y confusos.

### Cambios
- `_render_toolbar()` ahora usa **botones reales de Streamlit** (`st.button` y `st.download_button`) dentro de un contenedor con `key="results_toolbar"`.
- La vista activa se guarda en `st.session_state["result_view"]` (`"preview"` o `"markdown"`).
- Se eliminaron las pestañas `st.tabs` duplicadas; `render()` ahora muestra `_render_preview()` o `_render_markdown_view()` según la vista activa.
- El botón **Descargar** de la barra descarga:
  - **PDF** cuando la vista activa es "Vista previa".
  - **Markdown (.md)** cuando la vista activa es "Markdown".
- Se reemplazó el CSS `.nm-results-toolbar*` por reglas sobre `.st-key-results_toolbar`, manteniendo el diseño original: barra gris, pestaña activa en azul (`#0282fb`) y botones inactivos transparentes.

### Comportamiento
- Los botones del panel derecho ("Descargar resultado (PDF)", "Descargar en Markdown", "Copiar al portapapeles", "Generar nueva versión") se mantienen sin cambios.

## 2.3. Logo SVG y favicon

**Archivo:** `ui/app.py`
**Recursos:** `ui/assets/logo.svg`, `ui/assets/N_nuevamente.png`

### Problema
El logo del sidebar se veía borroso al escalarse, y la pestaña del navegador no tenía un ícono propio de la marca.

### Cambios
- **Logo del sidebar:** ahora se carga `assets/logo.svg` (vectorial), por lo que se ve nítido en cualquier tamaño y densidad de pantalla.
- **Favicon:** se definió `LOGO_N` apuntando a `assets/N_nuevamente.png` (logo solo con la "N") y se pasa a `st.set_page_config(page_icon=LOGO_N)`.
- Si `logo.svg` no existe, el sidebar muestra el texto "NuevaMente" como respaldo.

---

## Archivos modificados

| Archivo | Cambio |
|---|---|
| `ui/components/selection_view.py` | Botón Volver + estilos del encabezado |
| `ui/components/result_view.py` | Barra superior funcional, eliminación de `st.tabs`, nuevo CSS |
| `ui/app.py` | Logo del sidebar en SVG y favicon con la "N" |
| `ui/assets/logo.svg` | Nuevo logo vectorial |
| `ui/assets/N_nuevamente.png` | Logo "N" usado como favicon |

## Cómo probar

1. Ejecutar desde la raíz del proyecto: `streamlit run ui/app.py`
2. Subir un documento y pulsar **Siguiente →**.
3. En "Seleccionar opciones", pulsar **← Volver** y verificar que regresa a "Cargar archivo".
4. Completar el flujo hasta "Resultados".
5. Alternar entre **Vista previa** y **Markdown** y comprobar que el contenido cambia y la pestaña activa se ve en azul.
6. Pulsar **Descargar** en cada vista y verificar que baja el PDF o el `.md` correspondiente.
7. Verificar que el logo del sidebar se ve nítido y que la pestaña del navegador muestra la "N" (si no cambia, refrescar con Ctrl+F5, porque el navegador cachea el favicon).
