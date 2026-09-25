# Prompts versionados

Convención: `<tipo>_v<n>.txt`. No editar un prompt en producción in-place:
crear una nueva versión y actualizar la referencia en `llm_provider.py` /
`orchestrator.py`.

- `generacion_v1.txt` — PROMPT-001 (generación de contenido adaptado)
- `verificacion_v1.txt` — PROMPT-002, pendiente de extraer a archivo propio
  (hoy vive embebido en `validation/fidelity_checker.py`, ver guía §16)
- `perfiles/` — GEN-001, GEN-007 (plantillas por perfil, si se separan de `generation/profiles.py`)
- `formatos/` — GEN-002, GEN-006 (plantillas por formato pedagógico)
