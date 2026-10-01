# Guía de Git y GitHub — NuevaMente

Archivo aparte de `CONTRIBUTING.md`, dedicado exclusivamente a
convenciones de control de versiones y colaboración en GitHub. Aplica
desde el primer commit real (este repositorio de arquitectura no crea
ningún commit por sí mismo).

## Convenciones de ramas (branching)

- `main` — rama estable. Solo recibe merges vía Pull Request desde `develop`.
- `develop` — rama de integración activa. Base de todas las ramas de trabajo.
- Ramas de trabajo, siempre desde `develop`:

  ```
  feature/<id-tarea>-descripcion-corta   # feature/BE-RAG-009-retrieval-service
  fix/<descripcion-corta>
  docs/<descripcion-corta>
  chore/<descripcion-corta>
  ```

  El `<id-tarea>` debe coincidir con un ID del backlog
  (`FND-001`, `BE-VAL-002`, `TASK-003`, etc.) siempre que exista, para que
  la rama sea trazable a `docs/TRACEABILITY.md` sin ambigüedad.
- Prohibido: commitear directamente a `main` o `develop`.

## Convenciones de commits

[Conventional Commits](https://www.conventionalcommits.org/), incluyendo
el ID de tarea:

```
<tipo>(<alcance opcional>): <resumen en imperativo> [<ID-tarea>]

feat(processing): implementar chunk_text con overlap configurable [TASK-002]
fix(validation): excluir claim del cálculo si el LLM-juez falla [VAL-005]
docs: actualizar matriz de trazabilidad tras cerrar BE-RAG-010
chore: fijar versión de ruff
```

Tipos válidos: `feat`, `fix`, `test`, `docs`, `refactor`, `chore`, `ci`.
Un commit = un cambio lógico. No mezclar formateo automático con cambios
funcionales en el mismo commit.

## Reglas de Pull Request

Un PR debe:

- [ ] Estar dirigido a `develop` (nunca directo a `main`).
- [ ] Referenciar el/los ID(s) de tarea del backlog que cierra o avanza.
- [ ] Indicar contra qué fila de `docs/TRACEABILITY.md` corresponde (qué
      "Future Implementation" queda resuelta).
- [ ] Si el PR toca `output/schema.py` (`NuevaMenteOutput`), marcar
      explícitamente en la descripción que se revisó contra todos los
      consumidores del contrato (nota de TASK-003 en el Plan Técnico).
- [ ] Pasar el CI (`ruff check`, import-check, `pytest --collect-only` —
      ver `.github/workflows/ci.yml`).
- [ ] Tener al menos 1 revisión aprobada antes de mergear.
- [ ] No introducir código fuera de alcance de la tarea referenciada (un
      PR = una tarea o un grupo pequeño de subtareas relacionadas).

Plantilla sugerida de descripción de PR:

```markdown
## Qué hace
<resumen en 1-2 líneas>

## Tarea(s) del backlog
- ID-TAREA-1
- ID-TAREA-2

## Fila de docs/TRACEABILITY.md afectada
<Requisito / Componente>

## Checklist
- [ ] CI en verde
- [ ] Contrato de salida no roto (si aplica)
- [ ] Documentación actualizada (si aplica)
```

## Estructura esperada de Issues

Un Issue debe nacer de una tarea existente en el backlog (Plan Técnico,
Fase 8) o de una tarea nueva que se agregue primero ahí. Plantilla
sugerida:

```markdown
**ID de tarea (backlog):** <FND-001 | BE-ING-002 | ... | nueva — agregar
primero al backlog>
**Componente:** <COMP-01..COMP-11>
**Tipo:** feature | bug | docs | chore
**Descripción:**
<qué falta o qué está mal>
**Criterio de aceptación:**
<copiado o derivado del Plan Técnico / docs/TRACEABILITY.md>
**Bloquea / depende de:**
<otros IDs de tarea, ver el DAG de docs/TRACEABILITY.md>
```

Un Issue nunca describe una función completa "para copiar y pegar": debe
apuntar al contrato ya existente en `backend/src/.../*.py` (la firma con
cuerpo `...`) y pedir su implementación, no redefinir el contrato desde
cero salvo que el PR asociado también actualice `docs/architecture.md` y
`docs/TRACEABILITY.md`.
