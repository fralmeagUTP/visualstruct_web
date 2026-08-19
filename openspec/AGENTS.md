# OpenSpec — Instrucciones para agentes

Este proyecto usa **OpenSpec** para Spec-Driven Development (SDD).

## Estructura

```
openspec/
  project.md        # Contexto y convenciones del proyecto
  AGENTS.md         # Este archivo
  specs/            # VERDAD ACTUAL: capacidades ya implementadas
    <capability>/
      spec.md
  changes/          # PROPUESTAS: cambios aún no implementados
    <change-id>/
      proposal.md
      tasks.md
      design.md     # opcional
      specs/<capability>/spec.md   # deltas
    archive/        # cambios ya desplegados
```

## Reglas fundamentales

1. `specs/` describe **lo que el sistema hace hoy**. Solo se edita cuando un cambio
   archivado modifica el comportamiento real.
2. `changes/` describe **lo que se propone hacer**. Nunca mezclar propuestas con el
   estado actual.
3. Toda capacidad nueva o modificada pasa primero por una propuesta en `changes/`,
   se implementa, se verifica, y luego se archiva actualizando `specs/`.

## Formato de requisitos

Cada requisito usa lenguaje normativo (`DEBE`, `SHALL`) y al menos un escenario:

```markdown
### Requirement: <Nombre>
El sistema DEBE <comportamiento>.

#### Scenario: <nombre del escenario>
- **GIVEN** <contexto>
- **WHEN** <acción>
- **THEN** <resultado esperado>
```

## Formato de deltas (en changes/)

Los archivos de spec dentro de `changes/<id>/specs/<capability>/spec.md` usan
encabezados de operación:

- `## ADDED Requirements` — requisitos nuevos.
- `## MODIFIED Requirements` — requisito existente reescrito completo (incluye sus escenarios).
- `## REMOVED Requirements` — requisitos eliminados (nombre + razón).
- `## RENAMED Requirements` — `FROM: nombre viejo` / `TO: nombre nuevo`.

## Validación de una propuesta

Antes de considerar completa una propuesta de cambio:

- [ ] `proposal.md` explica el **por qué** y el **qué** (no el cómo detallado).
- [ ] `tasks.md` tiene checklist de tareas implementables y verificables.
- [ ] Cada requisito en deltas tiene al menos un escenario `#### Scenario:`.
- [ ] Los nombres de requisitos en `MODIFIED`/`REMOVED` existen en `specs/` actuales.
- [ ] Tras implementar: suite `pytest -q` pasa y cobertura no baja.

## Capacidades especificadas (estado actual)

| Capacidad | Spec |
|-----------|------|
| `application-shell` | App factory, config, health, assets |
| `session-state` | Sesiones server-side, historial, replay |
| `sequential-structures` | Módulo secuencial (6 TADs) |
| `hierarchical-structures` | Módulo jerárquico (4 TADs) |
| `graph-structures` | Módulo de grafos (4 fases, 6 algoritmos) |
| `hash-table` | Módulo de tabla hash |
| `sorting-visualizer` | Módulo de ordenamiento |
| `c-code-interpreter` | Extracción de código C y trazas de ejecución |
| `visual-playback-ui` | Simulación visual, controles, exportación |
| `help-system` | Ayudas por módulo/estructura y manual |
