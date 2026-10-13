# Continuidad obligatoria de VisualStruct

Proyecto canónico: `D:\MisProyectos\Web_VisualEstruct`. Una copia en C: no autoriza usar sus resultados como evidencia del destino.

## Al iniciar o continuar
1. Confirmar cwd/proyecto antes de cualquier acción. Leer `openspec/AGENTS.md`, `openspec/project.md` (su fotografía de pruebas es histórica) y `openspec/continuity/README.md`.
2. Identificar primero la instrucción nueva vigente, change y bloque/operación; para cambios con assignment_source leer ese registro y exigir coincidencia de ID/operación/task. Un checkpoint histórico nunca sustituye la instrucción nueva. Si esta cambia la asignación, guardar nuevo registro de instrucción y actualizar solo el puntero del índice de continuidad, conservando registro anterior; no pedir reconciliación de instrucciones antiguas ya sustituidas. Después leer propuesta, diseño, deltas, tareas y evidencia correspondiente. No elegir siguiente operación desde un checkpoint histórico.
3. Ejecutar desde raíz: `python -B scripts/check_session_continuity.py --change <change> --operation <operation-id> --assignment-id <id-vigente> --phase before`. Omitir assignment-id solo en cambios sin assignment_source. Consultar IDs/fuentes en `openspec/continuity/index.json`. Un bloque no registrado exige bindings revisados; no cambiar de ID para eludir un cierre.
4. Comunicar proyecto/change/operación, alcance autorizado, qué está cerrado, siguiente acción y límites. Leer fuentes enlazadas: una guarda verde no demuestra aprobación ni cumplimiento funcional.
5. Antes de repetir un bloque declarado cerrado, registrar ID exacto, motivo, evidencia nueva y alcance en decisión del change. Pasar `--reopen-reason "<motivo exacto>" --decision-ref openspec/changes/<change>/<decisión>.md`. El texto no autentica autorización: consultar autorización real cuando corresponda.
6. Al terminar, actualizar solo seguimiento/evidencia propia conservando resultados anteriores. Ejecutar `--phase after`; informar resultados/siguiente acción. Esta fase solo reporta, incluso si acaba de cerrarse el bloque; no permite reimplementarlo. Checkpoint capturado es fotografía fechada; `--checkpoint <archivo.json>` rechaza fuentes cambiadas y exige releer/replanificar. Después de cambios legítimos leerlos y generar checkpoint fresco sin --checkpoint; no borrar logs para conservar fotografía.

## Persistencia y coordinación
Specs nuevas: `openspec/changes/<change>/specs/<capability>/spec.md`; allí también proposal, decisiones/design, tasks y evidence. Al consolidar cambio verificado, fusionar deltas con `openspec/specs` y conservar historia en `changes/archive`. No archivar por mera validación sintáctica. Resolver decisiones antes de escoger contratos contradictorios.

Estado se deriva de fuentes existentes, sin otro contador manual. Progress/tasks/worklist pueden contener instrucciones superadas; leer última decisión aplicable y evidencia. No confundir casos registrados con cierre global ni13/22 con porcentaje de tiempo.

La auditoría activa posee sus tasks/progress/worklist/evidence; otros trabajos no los sobrescriben. Mantener preview5051 y no publicar/desplegar/commit/push/merge/reset/rebase sin autorización. La guarda es obligatoria para agentes, no intercepta todas las herramientas ni recupera conversaciones no persistidas.
