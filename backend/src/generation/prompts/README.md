# Prompts (Fase 15 del Plan Técnico)

Convención de versionado: `<tipo>_v<n>.txt`. Ningún prompt se edita
in-place una vez usado en producción: se crea una nueva versión y se
actualiza la referencia en `llm_provider.py` / `orchestrator.py`.

Este directorio contiene únicamente **placeholders** — el contenido real
de cada prompt (variables, reglas, restricciones) está especificado en la
Fase 15 del Plan Técnico y debe copiarse ahí como implementación futura.

- `generacion_v1.txt` (PROMPT-001) — generación de contenido adaptado.
  Variables: `{contexto}`, `{perfil}`, `{formato}`, `{nicho}`, `{nivel_detalle}`.
- `verificacion_v1.txt` (PROMPT-002) — verificación de un claim contra el
  contexto fuente. Variables: `{claim}`, `{contexto_fuente}`.
