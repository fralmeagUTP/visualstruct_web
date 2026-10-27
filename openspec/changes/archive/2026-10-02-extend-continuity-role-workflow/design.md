# Diseño mínimo
Módulo role_workflow reutiliza read_source/GuardError del arnés existente; raíz/config explícitas, sin rutas VisualStruct en núcleo. CLI existente añade workflow-config/task/gate. Config VisualStruct declara exclusiones técnicas y no asigna su auditoría a roles nuevos.
Tarea contiene objetivo, requisitos y refs, base, rutas exactas permitidas, propietario, dependencias, entregables, evidencias, siguiente paso y estado. Piloto permite un solo escritor activo, detecta rutas solapadas incluso jerarquías. Dependencias cerradas deben conservar evidencia vigente.
Gates before (contexto/asignación/alcance/decisiones/propiedad/dependencias), verify (ejecuciones obligatorias aprobadas y hashes), close (verify, QA distinto del autor y entregables docs). after sólo fotografía/informe. No interpretar checkbox como cierre ni not-run como passed.
Recuperación usa archivos actuales con hashes y checkpoints previos; evidencia liga hashes de entradas/base/entregables. Config y manifiesto forman fotografía. QA separado declarado requiere owner/reviewer diferentes y resultado ejecutado vigente; no autentica independencia real.
OpenSpec instalado 1.6.0. FAQ oficial consultada: https://github.com/Fission-AI/OpenSpec/blob/main/docs/faq.md. OpenSpec describe acuerdo/spec/deltas/archivo/recuperación; roles, propiedad, hashes/gates son decisiones locales, no requisitos de esa FAQ. No asumir comandos de versión main disponibles localmente.

## Correcciones solicitadas por QA independiente (2026-10-02)
1. Capturar configuración mediante deepcopy y recovered_task separado; no compartir referencias anidadas del llamador. Regresión directa sin deepcopy previo en la prueba.
2. Para tareas nuevas con rutas solapadas con tareas cerradas, exigir closed_scope_decisions, decisión resuelta/aprobada vinculada predecessor/task/owner/allowed_paths/motivo. Reopening repite alcance explícitamente; successor requiere new_scope y objetivo/requisitos nuevos. after es informe y no autoriza retomar trabajo.
3. Validar observed_at_utc como fecha ISO-8601 con Z/+00:00 y fecha/hora válidas, también en QA. No autentica el momento real ni la ejecución.
No se modifica guard anterior ni evidencia/probes independientes. Revisión posterior/adopción pendientes.
