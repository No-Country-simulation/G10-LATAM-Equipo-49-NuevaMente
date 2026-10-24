# Workflow n8n

`webhook-nuevamente-v2 (2).json` recibe un archivo y las opciones pedagógicas,
llama a la API FastAPI local y devuelve el resultado si la fidelidad alcanza
0.9. La interfaz Streamlit envía la solicitud al webhook; n8n orquesta la
ingesta, la adaptación y la consulta del job.

## Configuración

1. Importa el JSON del workflow en n8n y actívalo.
2. Mantén los nodos HTTP apuntando a `http://localhost:8000` cuando n8n y la
	API corran directamente en la misma computadora.
3. Inicia Streamlit con `N8N_WEBHOOK_URL` apuntando al webhook activo. El valor
	predeterminado es `http://localhost:5678/webhook/webhook-nuevamente-v2`.
	Para probar en modo escucha, ejecuta Streamlit con la URL `/webhook-test/`
	que muestra n8n, por ejemplo:

	```bash
	export N8N_WEBHOOK_URL=http://localhost:5678/webhook-test/webhook-nuevamente-v2
	./run_ui.sh
	```

El webhook recibe un formulario multipart con `file`, `perfil`, `formato` y
`nicho`. La API admite PDF, Markdown y TXT. El workflow consulta el job hasta
que termina y responde con el resultado bajo `data`.

El nodo de fidelidad rechaza resultados con puntaje nulo o menor que 0.9; no
se debe considerar exitosa una adaptación si el backend no produjo una
evaluación verificable.
