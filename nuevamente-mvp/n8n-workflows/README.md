# n8n-workflows

Capa de orquestación externa (DT-10) — wrapper sobre `POST /adaptar` con
nodo IF de fidelidad (umbral `FIDELITY_THRESHOLD`, DT-11).

No reemplaza la orquestación interna del pipeline (`FE-API-002`); es una
capa adicional de control de calidad + auditoría sobre ella.

Prioridad: COULD_HAVE — Semana 5, tarea INT-004. No bloquea el Vertical Slice.
