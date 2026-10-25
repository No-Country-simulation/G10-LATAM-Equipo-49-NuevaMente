# Reporte de cambios: Streamlit, n8n y API en AWS

**Fecha:** 25 de octubre de 2026  
**Estado:** corrección desplegada en AWS y confirmada con ejecuciones exitosas en n8n.

## Resumen

Se corrigió el flujo desplegado para que Streamlit envíe el archivo directamente al webhook de n8n como multipart, usando el campo binario `file`. n8n ingesta el archivo en la API FastAPI y continúa con la adaptación y el almacenamiento en OCI.

La causa no era el nombre `file` ni el endpoint del backend. En AWS, la función multipart `submit_to_workflow()` existía, pero la UI no la invocaba: primero hacía la ingesta directa en FastAPI y luego notificaba a n8n con JSON (`job_id`, `status` y resultado). Por eso el nodo `Ingest Document` recibía una ejecución, pero no encontraba el binario `file`.

## Flujo anterior en AWS

1. `upload_view.py` llamaba `api_client.ingest(...)` y subía el archivo directamente a FastAPI.
2. `selection_view.py` llamaba `api_client.request_adapt(...)` con el `document_id`.
3. `loading_view.py` llamaba `notify_n8n(...)`, que enviaba JSON al webhook, no el archivo.
4. El workflow n8n intentaba leer el binario `file` y fallaba porque el webhook había recibido JSON.

## Archivos modificados en AWS

| Archivo | Antes | Después |
|---|---|---|
| `nuevamente/ui/api_client.py` | `submit_to_workflow()` recibía un `UploadedFile`, aunque la pantalla no lo llamaba. | Recibe bytes, nombre y MIME; envía `files={"file": (...)}` junto con `perfil`, `formato` y `nicho` como campos multipart. Valida la respuesta de n8n y devuelve su objeto `data`. |
| `nuevamente/ui/components/upload_view.py` | Ingestaba inmediatamente el archivo por `api_client.ingest()`. | Conserva bytes, nombre y tipo MIME en `st.session_state["source_file"]`; solo avanza a la selección. |
| `nuevamente/ui/components/selection_view.py` | Solicitaba adaptación directamente a FastAPI con `request_adapt()` y pasaba a la pantalla de polling. | Recupera `source_file`, llama a `submit_to_workflow()` una vez, muestra un spinner y guarda el resultado final para la pantalla de resultados. |
| `nuevamente/ui/components/result_view.py` | Al subir otro archivo limpiaba `ingest`, `job_id` y `result`. | También limpia `source_file` para liberar el archivo anterior. |

El nuevo flujo evita la ingesta duplicada: Streamlit ya no ingesta primero y luego vuelve a enviar el mismo archivo para que n8n lo ingeste.

## Backend y workflow n8n

No se modificó código del backend. El endpoint existente `POST /ingest` ya recibe `file` como `UploadFile` multipart. Tampoco se cambió el workflow n8n: el nodo `Ingest Document` ya estaba configurado para enviar el binario de entrada `file` al campo multipart `file` de FastAPI.

`loading_view.py` no se modificó. En el camino corregido, la respuesta completa llega sincrónicamente desde n8n y la UI pasa directamente a Resultados, por lo que no usa el polling ni la notificación JSON de ese flujo anterior.

## Despliegue

- Instancia: rama `feature/containerize-infrastructure`, commit base `58f9822`.
- Se guardó una copia de los cuatro archivos originales en `/home/ec2-user/nuevaMente-ui-backup-20261025`.
- Se reconstruyó y recreó únicamente el servicio Docker `ui` con `docker compose build ui` y `docker compose up -d --no-deps ui`.
- El servicio `backend` no se reconstruyó, reinició ni modificó.
- `N8N_WEBHOOK_URL` estaba configurada y apuntaba al n8n de OCI; no se incluyó su valor en este reporte.

## Verificaciones

- `py_compile` pasó para los cuatro archivos modificados, tanto antes de copiarlos como dentro del contenedor UI.
- Una prueba aislada confirmó que el cliente envía `files["file"]`, los tres campos del formulario y devuelve `data` de la respuesta de n8n.
- Healthcheck de Streamlit: `ok` en el puerto 8501.
- Healthcheck de FastAPI: `{"status":"ok"}` en el puerto 8000.
- El contenedor UI quedó `healthy`; el backend permaneció `healthy`.
- Después del despliegue, se confirmó que n8n registra ejecuciones exitosas en verde.

## Versionado pendiente

La corrección se aplicó directamente en la instancia y se desplegó, pero todavía no está comprometida en Git. La copia de respaldo está en el servidor. Para conservar y compartir este arreglo de forma reproducible, queda exportar el diff de estos cuatro archivos y llevarlo a una rama/commit del repositorio.
