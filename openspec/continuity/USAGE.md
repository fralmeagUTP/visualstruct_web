# Uso práctico del arnés de continuidad

El arnés ayuda al coordinador/agente a recuperar contexto y verificar precondiciones. No dirige automáticamente agentes, no ejecuta tests por sí mismo y no impone aislamiento del sistema operativo. Núcleo existente: scripts/check_session_continuity.py y role_workflow.py. Perfil base vacío y tarea base están en [role-workflow.json](role-workflow.json) y [role-task-template.json](role-task-template.json).

## Qué puede hacer hoy
- Recuperar identidad proyecto/change/operación/instrucción y fuentes/requisitos/tareas/evidencia persistidos; exigir assignment_id si el change usa assignment_source.
- Derivar tareas/cierres declarados y capturar hashes/fecha; rechazar raíz incorrecta, operación desconocida/cerrada, asignación incompatible y checkpoint obsoleto.
- Aplicar contratos activables specifications/code/quality/visual/documentation con checks obligatorios, un escritor activo por perfil, rutas/propiedad/dependencias y decisiones de reapertura o sucesor.
- Rechazar prueba obligatoria fallida/no ejecutada, decisión pendiente, evidencia de texto obsoleta y autocertificación QA declarada; exigir documentación para close.
- Generar muestra HTML local (evidencia local: `openspec/continuity/examples/local-task/artifact/index.html`) desde una tarea mediante builder estándar, sin ejecutar herramientas ni insinuar aprobación. Manual del ejemplo (evidencia local: `openspec/continuity/examples/local-task/README.md`).

Los cinco roles tienen adopción real pertinente repartida en dos pilotos: documentación + QA independiente; después specifications/code/visual por el mismo autor y nueva QA independiente. No cinco equipos/agentes ni ciclo completo de dependencias cerradas: último piloto declaró dependencies=[] y usó bases/handoffs. Aceptación de ejemplos finitos no prueba uso rutinario universal.

## Flujo de uso
1. Confirmar raíz e instrucción vigente; leer AGENTS.md, contexto/proyecto y propuesta/diseño/specs/tareas/decisiones/evidencia. No elegir siguiente tarea desde foto histórica.
2. Registrar change y operación en index.json; crear profile workflow.json del change con tarea explícita: objetivo/rol/owner, requisitos/base/rutas, dependencias, entregables/documentación, checks/evidencia, next_step, approval, decisiones y LOW. Plantillas no autorizan trabajo; sustituir placeholders. Asignación nueva conserva registro anterior y actualiza su puntero cuando corresponda.
3. Ejecutar before desde raíz con IDs registrados. El coordinador mantiene un solo escritor; transferir propiedad explícitamente. No declarar closed para eludir dependencia; una tarea cerrada solapada exige decisión vinculada de reapertura/sucesor.
4. Trabajar sólo alcance autorizado y ejecutar comprobaciones pertinentes. Guardar resultados reales con UTC ISO-8601 Z/+00:00 y hashes exactos de requirements+base+deliverables+documentation; usar verify. Validar OpenSpec no demuestra cumplimiento funcional.
5. Revisor genuino distinto inspecciona/reproduce y registra independent-qa sobre inputs actuales. close sólo comprueba precondiciones; después coordinación registra state=closed y after. Consolidar/archivar sólo alcance aceptado, conservando historia, runtime y correspondencia de rutas.

Ejemplo de comando, reemplazando todos los identificadores y ruta por los de la instrucción vigente (no ejecutar placeholders):
```
python -B scripts/check_session_continuity.py --change CAMBIO_APROBADO --operation OPERACION_REGISTRADA --workflow-config openspec/changes/CAMBIO_APROBADO/workflow.json --task TAREA_ASIGNADA --gate before
```
Usar --gate verify y --gate close según paso. Añadir --assignment-id ID_VIGENTE si assignment_source existe. Informe: --phase after --gate after. Recuperación: --checkpoint FOTO_PROPIA.json compara fotografía y fuentes; si cambian legítimamente, leer/replanificar/reverificar lo afectado y crear nueva sin --checkpoint, sin borrar evidencias antiguas.

## Configurar otro proyecto
Llevar los dos scripts del núcleo y estructura OpenSpec/continuidad a su raíz, respetando sus instrucciones locales/permisos reales. Ajustar canonical_project del index, project_root del perfil, contexto/AGENTS/project, bindings change/operación/fuentes/tasks/assignment_source y rutas de aprobación. Ajustar protected_paths/rutas permitidas, propietarios, roles pertinentes/checks, dependencias, entregables y evidencias/siguiente paso. No copiar asignaciones ni resultados de VisualStruct como aprobación/evidencia de otro destino.

CLI calcula raíz desde la instalación del script, exige cwd canónico y archivos OpenSpec de ese proyecto; núcleo evaluate permite raíz/config explícitas. Copiar una config con ruta D: sin ajustarla falla. Permisos del entorno/sandbox son independientes de configuration: el perfil no amplía acceso. Rutas permitidas deben ser precisas y resolución contenida. No rellenar identidad de QA con nombre ficticio.

## Evidencia binaria y límites
Native guard lee UTF-8. PNG/binarios necesitan manifiesto de hashes y checker suplementario explícito; cambio aislado de PNG no invalida automáticamente gate si texto no cambia. El piloto conservó cuatro capturas/hashes y rechazo de corrupción en copia temporal; ese suplemento se ejecutó antes de cierre. Registros no autentican permisos/revisores/tiempos o ejecución ni ofrecen reserva global entre perfiles. Cambios después de lectura/fuentes no registradas quedan fuera. LOW por defecto; escalar sólo bloque/motivo/alcance/retorno LOW.

Muestra/fixtures cerrados son historia, no tareas vigentes. [Mapa del piloto de roles](role-workflow-archive.json) y [mapa del ejemplo](example-archive.json) resuelven evidencia fechada a bytes originales. Runtime manual posterior no hereda automáticamente aprobación de guías anteriores. WCAG global/screenreader/matriz de navegadores no certificados; sólo comprobaciones finitas locales aceptadas.

## Pendientes reales de SDD del proyecto
[Reconciliación conservada](reconciliation-status.md): C1 sólo1/12 requisitos históricos consolidado, otros11 aún requieren decisión/evidencia; no29casos globalmente cerrados. Hash H1 entero/capacidad fija está aprobado y documentado, pero esta entrega no cierra auditoría funcional/instrucción/sesiones legacy. Validar RN conserva limitación abierta de black-height/parents/cycles y propuesta pendiente de decisión de producto. Auditoría activa/global y otros changes poseen su propio seguimiento; esta entrega no los cierra. El13/22 observado es conteo de tareas, no porcentaje de tiempo ni cierre por métodos registrados.

El arnés no sustituye mantener requisitos actuales y deltas coherentes, justificar cambios de alcance, QA independiente real y pruebas/evidencia causal. Debe sostenerse esa disciplina en trabajo rutinario; no se crea siguiente proyecto ni motor.
