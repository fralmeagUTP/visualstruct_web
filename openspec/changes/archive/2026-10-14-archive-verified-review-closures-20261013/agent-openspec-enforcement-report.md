# Agentes y OpenSpec: qué es obligatorio y qué está automatizado

Las instrucciones del proyecto obligan al agente a registrar cada instrucción/tarea/cambio y a actualizar las especificaciones al cerrar. **Eso no está garantizado por un motor automático que vigile todas las herramientas.**

| Control | Configurado y comprobado | Límite real |
|---|---|---|
| Continuidad | `check_session_continuity.py` comprueba proyecto/cwd, change/operación/asignación, fuentes, tarea, reapertura y checkpoint. En este cierre before/after terminaron con exit0. | Se invoca explícitamente; no intercepta ediciones, no registra tareas ni ejecuta pruebas. |
| Cinco roles | `role_workflow.py` configura specifications, code, quality, visual y documentation, con checks, propietario, dependencias, rutas, SHA y QA distinta. | Sólo se evalúa con `--workflow-config/--task/--gate`; no lanza cinco agentes, no autentica personas/permisos ni bloquea globalmente archivos. |
| Cierre de rol | verify/close rechazan evidencia ausente/fallida/obsoleta y exigen QA/documentación según contrato. | El evaluador no ejecuta checks ni modifica `state`; coordinación registra el cierre. |
| Specs canónicas | OpenSpec archive consolida deltas y valida las specs. Bloqueó realmente escenarios omitidos y gramática DEBE; se corrigieron con trazabilidad. | No se ejecuta automáticamente al terminar una tarea; validación sintáctica no demuestra funcionalidad. |
| Hooks/CI | No hay hooks Git activos. CI actual llama inventario básico `--check`. | No fuerza `role_workflow`, guardas ni archivo; tampoco el inventario estricto `--bindings/overlay`. |

## Evidencia de ejecución, sin repetirla

El expediente `archive/2026-10-02-extend-continuity-role-workflow` conserva un log de23tests del validador (OK), la aceptación técnica de68checks y probes, y el piloto real documentación/QA con close antes de state=closed y after0. El expediente `archive/2026-10-02-adopt-local-role-documentation-example` acredita seis tests y el piloto specifications/code/visual: mismo autor secuencial, QA distinta, HTML reproducible, teclado/visual en1280/390/320 y tres close0/after0. Son alcances históricos aceptados, no pruebas nuevas de hoy ni adopción universal.

El perfil permanente `openspec/continuity/role-workflow.json` tiene cinco contratos habilitables, pero tareas vacías y placeholders. `role-workflow-approval.json` es una plantilla approved=false. No hay `.agents` ni `.codex` locales. Los hilos reales autor/QA de C1 son coordinación de plataforma; no los lanzó este script. El perfil base protege app/static/templates/docsC/tests por su origen de piloto; un trabajo productivo necesita perfil y rutas aprobadas propios.

Las guardas utilizadas en C1 y este archivo son las básicas: el JSON final C1 no tiene sección workflow. Por tanto no se atribuye un role-close que no se invocó. Usar la extensión de roles exige añadir su configuración real por tarea. No se amplió AISEF ni el arnés para ocultar esa diferencia.

## Rutina concreta para un trabajo futuro

1. Registrar propuesta/requisitos/diseño/tareas, asignación y binding actual en el change aprobado.
2. Invocar before; si se usan roles, añadir perfil/tarea/gates y autorización real, sin reutilizar uno cerrado.
3. Ejecutar sólo los checks autorizados, conservar fuentes y resultados, y obtener QA independiente cuando corresponda.
4. Registrar cierre, capturar after y consolidar los deltas verificados al archivar con OpenSpec. Revisar rutas e integridad y retirar bindings activos archivados.

El índice ahora está sin tareas activas. Se requiere un registro nuevo para otro encargo. Inventario correcto:375originales,369activas/369vinculaciones,8retirosNOT_PASS,2añadidas. No375pendientes; los39sitios creadores son otra clasificación. C1 12/12 sigue limitado al corpus aprobado:sinLSan,universalidad ni garantía temporal de otros algoritmos/todas las entradas de15nodos. Consultas privadas no publicadas. Sincommit/push/VPS en este cierre.

Fuentes:AGENTS.md,openspec/AGENTS.md,continuity/ROLE-WORKFLOW.md,scripts/check_session_continuity.py,scripts/role_workflow.py; logs/decisiones citados arriba y evidence/four-final-reconciliation-20261014/agent-enforcement-evidence.json.
