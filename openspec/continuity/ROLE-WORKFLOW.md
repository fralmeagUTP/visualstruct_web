# Protocolo permanente de roles del arnés

Núcleo: scripts/role_workflow.py; CLI: scripts/check_session_continuity.py. Se conserva el mismo arnés. [Guía breve](ROLE-WORKFLOW-QUICKSTART.md), [perfil base](role-workflow.json), [plantilla de tarea](role-task-template.json) y [mapa de archivo](role-workflow-archive.json).

## Contratos y tarea nueva
Cinco contratos activables: specifications, code, quality, visual, documentation. Required_checks del perfil exige specification-validation, isolated-harness-tests, independent-review, visual-accessibility-responsive o documentation-coherence según rol. Contratos configurables no equivalen a cinco agentes/procesos ni competencia demostrada.

El perfil permanente tiene tasks vacío y placeholders de change/operation: es base para copiar, no asignación activa. Registrar propuesta/requisitos/diseño/decisión/tareas y bindings de continuidad bajo un nuevo change aprobado. Copiar perfil y plantilla a ese change, cambiar raíz/IDs/propietario/rutas/requisitos/base/approval/evidencia/siguiente paso. Conservar historial de tareas cerradas que compartan el ámbito; no crear perfil nuevo para eludir su cierre. Configurar un solo escritor activo y transferir propiedad explícitamente. Desactivar roles ajenos al alcance con justificación.

## Gates
before: contexto/alcance aprobado, decisiones resueltas, propiedad/dependencias, LOW o escalado acotado. verify: checks requeridos realmente ejecutados y vigentes. close: verify + QA real distinta del autor + documentación. after: informe; no autoriza trabajo ni cierra state. Primero close válido; después coordinación registra cierre y captura after antes de archivo. CLI no modifica perfiles ni ejecuta pruebas.

--checkpoint compara identidad/config/fuentes; ante cambio legítimo leer/replanificar y capturar nuevo resultado sin --checkpoint. No borrar evidencias para conservar hashes anteriores. evaluate(root,config,task,gate,previous) copia profundamente config y entrega recovered_task separado; snapshot devuelto es editable, no firma.

## Evidencia, decisiones y reapertura
Cada evidencia requerida: check, executed=true, result=passed, exit_code=0 entero, observed_at_utc ISO-8601 con segundos/fracción opcional hasta seis dígitos y Z/+00:00; inputs exactos SHA256 de requirements+base+deliverables+documentation sin duplicados. Preservar resultados antiguos. QA: kind=independent-qa, role=quality, author del task y reviewer real distinto. Nombres distintos sin revisión genuina no bastan.

Decision JSON status=resolved. Si una tarea nueva solapa rutas de tarea cerrada, closed_scope_decisions mapea predecessor a archivo incluido en decisions: approved=true, status=resolved, predecessor/task/owner/allowed_paths exactos, reason no vacío, kind=reopening; sucesor de nuevo alcance usa kind=successor y new_scope no vacío, objetivo/requisitos distintos. Dependencias cerradas requieren evidencia de cierre todavía vigente.

## Alcance completado y límites
Mínimo determinista aceptado técnicamente (68 pruebas y QA/probes independientes) y piloto documental con QA real. Piloto local specifications/code/visual aceptado por QA después del piloto documentación/QA; no uso rutinario universal, motor autónomo, lanzamiento de agentes ni pipeline distribuido. Guías/profiles aceptados originalmente están congelados en archivo; mapa enlaza exactamente sus bytes para conservar validez histórica. Guías permanentes posteriores explican operación y retiro: no presentarlas como el mismo documento aprobado por aquella QA.

Registro no impone aislamiento OS/reserva global entre perfiles ni autentica permisos/revisores/tiempos/ejecución. Un coordinador real mantiene escritor único. Fuentes no registradas y cambios posteriores no quedan cubiertos. LOW por defecto; escalado exige block/reason/scope/return_to_low.

No usar auditoría activa o preview5051 como piloto. Sin publicar/merge/desplegar automáticamente. OpenSpec local observado 1.6.0; roles/gates son protocolo local autorizado, no exigencias de OpenSpec.

Guía práctica vigente: USAGE.md. Muestra histórica aceptada: examples/local-task; no es tarea activa.
