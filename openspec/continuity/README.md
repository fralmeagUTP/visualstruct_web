# Continuidad de VisualStruct

Leer AGENTS.md al iniciar o continuar. Runtime estable: este README, index.json, assignments/ y scripts/check_session_continuity.py. No dependen de una propuesta activa del arnés.

## Uso mínimo
Usuario: «Continúa en D:, con el cambio y bloque asignados; recupera requisitos y evidencia, sin repetir trabajo cerrado».
Agente: confirmar mensaje vigente, proyecto/change/operación/task/assignment_id, leer fuentes enlazadas y ejecutar desde D:\MisProyectos\Web_VisualEstruct:
python -B scripts/check_session_continuity.py --change audit-local-quality-and-unified-controls --operation red-black.delete --assignment-id coordination-rbt-delete-20261002 --phase before
Al finalizar usar --phase after. Esa fase solo informa, incluso para cerrado; no autoriza repetición.

La asignación de ejemplo es una instrucción fechada, no siguiente tarea permanente. Si cambia la instrucción autorizada, coordinación/dueño del arnés registra un nuevo archivo inmutable en assignments/ y actualiza assignment_source en index.json, conservando el anterior. No derivar operación desde checkpoint histórico ni pedir reaprobar solicitud sustituida. Antes de trabajar, el ID/change/operación deben coincidir; el gate no lee ni autentica el prompt natural por sí solo.

## Fuentes y reapertura
index.json contiene bindings a fuentes, planes/evidencia y prefijos de tareas; no guarda contadores ni estado manual paralelo. La guarda deriva casillas, declaraciones de cierre, UTC y hashes. Los17bloques iniciales incluyen historial Lista/Circular, búsquedas Circular, RN y familias pendientes; familia amplia requiere precisar método/camino y añadir bindings finos al cerrar.
Repetir un bloque cerrado requiere decisión del mismo change con ID/motivo/evidencia nueva/alcance, --reopen-reason y --decision-ref, además de coincidir con asignación. No cambiar ID para eludir cierre ni usar after como permiso de implementación.

## Fotografías y cambios legítimos
--checkpoint archivo.json comprueba igualdad de fuentes/identidad. Un log nuevo no registrado no invalida lo capturado. Append/fuente nueva registrada exige leer cambios y emitir foto fresca sin --checkpoint. No borrar logs para mantener una foto antigua. Ediciones concurrentes durante lectura pueden exigir reintento; modificaciones posteriores siguen posibles.

## Persistencia y alcance
Solicitud → proposal/specs/design/tasks → checkpoint antes → implementación → evidencia → checkpoint después → revisión/consolidación/archivo. Nuevas specs viven en openspec/changes/<id>/specs; lo verificado se fusiona a openspec/specs y su contexto se archiva. La carpeta openspec/continuity conserva controles operativos aunque se archive el cambio que los introdujo.
Preservar dueño de tasks/progress/worklist/evidence de auditoría y preview5051. Sin suites app/publicación/despliegue cuando coordinación lo prohíbe. Cierres finitos y13/22 no son porcentaje de tiempo ni cierre global.

## Comprobaciones propias
python -B -m unittest discover -s scripts/tests -p test_session_continuity.py -v
python -B -m unittest discover -s scripts/tests -p test_continuity_installation.py -v
No importan ni ejecutan aplicación. La segunda prueba enlaces/runtime y spec consolidada después del archivo.

## Límites y pendientes
Guarda valida identidad documental y declaraciones; no demuestra corrección funcional, aprobación auténtica, cumplimiento humano, todos los caminos ni conducta de otras herramientas. No intercepta todos los comandos.
Ver reconciliation-status.md: C1 parcial1/12 y11pendientes, Hash H1 aprobado y reconciliado documentalmente; verificación técnica pendiente, validación RN parcial y auditoría global abiertas. Cerrar arnés no resuelve esas contradicciones.

## Extensión de roles consolidada
ROLE-WORKFLOW.md y ROLE-WORKFLOW-QUICKSTART.md describen operación permanente. role-workflow.json es perfil base sin tareas activas; role-task-template.json exige completar alcance aprobado. Mínimo técnico y piloto documentación/QA aceptados; piloto real specifications/code/visual también aceptado y archivado; uso rutinario general no certificado. role-workflow-archive.json conserva correspondencia con evidencia histórica; no usar comandos retirados como nueva asignación.

## Uso práctico y muestra local
USAGE.md explica capacidades, rutina y configuración de otro proyecto. examples/local-task conserva muestra exacta aceptada; es fotografía histórica, no autorización de tarea. example-archive.json resuelve evidencia original del piloto.

## Disposición documental vigente2026-10-13
La clasificación integral ymapas dearchivo están en openspec/changes/archive-verified-review-closures-20261013/classification-final.md. Lasmenciones anteriores aRNlimitado/auditoríaabierta son fotografías históricas:V3 yelalcancefinito deauditoría yaaceptados/specs consolidados. C1 mantiene sus11obligaciones sinadmisiones automáticas. Sólo siguen dospropuestas pendientes reales (auditoría didácticaoriginal ypilotoPila), más retiroadministrativo delremanente delogs protegido ynoautorizado porrechazoautomático. No elegir operaciones desde workflows/checkpoints archivados.

## Mantenimiento local final completado
AutorizaciónSentinel_d60312733bd081918cbed1ad70d6815f efectuada: remanenteaudit-local ausente, archivo completo, preview5051reiniciado conlogs fuera dechanges y3904sesiones originales preservadas.46changes originales archivados/2propuestas pendientes. Estadoanterior debloqueo eshistórico. Evidencia e informefinal enarchive-verified-review-closures-20261013.

## Publicación de este archivo
Este repositorio distribuye conclusiones/specs/documentos; los inputs deejecución ylas asignaciones locales activas permanecen enD. index.json publicado es una fotografía sin tareas activas; registrar instrucción/asignación ybindings revisados antes denuevo trabajo. Referencias marcadas locales no son archivos ausentes que deban fingirse con fixtures.

## Estado reconciliado y archivo final — 2026-10-14

Los cuatro expedientes restantes fueron reconciliados y archivados por autorización explícita posterior del usuario. `archive-four-final-20261014.json` conserva ubicaciones y bindings históricos; el índice no contiene asignaciones activas. C1 está admitido12/12 **en alcance finito documentado**:375entradas originales,369activas/vinculadas,8retirosNOT_PASS y2añadidas. Las menciones anteriores1/12/11pendientes/2propuestas abiertas son fotografías supersedidas, no próximas tareas.

Specs vigentes consolidadas:didactic-conformance-qa,application-quality-validation,didactic-conformance-remediation,sequential-structures,visual-playback-ui yapplication-quality-audit. Se mantienen cincoetapas/manual/educaciónaprobada;noLSan/universalidad/all15temporal/privatequeriespublicadas. SinGit/VPSactualizados. Antes de un nuevo trabajo registrar instrucción/change/operación/task/assignment yguarda vigente; no usar comandos/asignaciones cerradas. El flujo exige sincronización por instrucciones yCLI explícito, no agentes autónomos/hooks que la hagan automáticamente.
