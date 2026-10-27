# Adopción del arnés

## Para el usuario
Al pedir continuar, indicar proyecto/change y bloque si se conoce: «Continúa auditoría en D:, Eliminar RN; recupera el estado y no repitas búsquedas cerradas». No necesita copiar toda la conversación. Pedir al agente el checkpoint y los enlaces a requisitos/evidencia; lo que no esté persistido debe registrarse en el cambio dueño.

## Para el agente
1. Leer AGENTS, README, alcance/decisiones y binding correspondiente.
2. Desde D:\MisProyectos\Web_VisualEstruct ejecutar:
   `python -B scripts/check_session_continuity.py --change audit-local-quality-and-unified-controls --operation red-black.delete --assignment-id coordination-rbt-delete-20261002 --phase before`
3. Leer fuente/context_sources/evidence de la salida; comunicar bloque, límites y siguiente acción. SHA valida identidad documental, no semántica.
4. Después de actualizar seguimiento/evidencia propios, ejecutar el mismo comando con `--phase after`. Es informe de cierre, no permiso para trabajar otra vez en un bloque cerrado.
5. Si reutiliza fotografía: `--checkpoint <json>` exige igualdad exacta de fuentes. Un log adicional no registrado no bloquea. Si cambia un log registrado o se añade un binding, el checkpoint anterior queda obsoleto: leer cambios y emitir uno fresco sin --checkpoint. No borrar evidencia para mantener una fotografía válida.
6. Reabrir cerrado: decisión del mismo change con ID/motivo/evidencia nueva/alcance; --phase before --reopen-reason y --decision-ref. No usar --phase after como autorización de nueva implementación.

## Bloques registrados
Los cinco iniciales distinguen historial Lista/Circular, instrucción Buscar Circular, Insertar RN y Eliminar RN. Eliminar ahora enlaza baseline real, revisión SHA, resumen/log, plan por instrucción y decisión de Validar; no hereda cierre de Insertar.

Siguientes bloques disponibles sin afirmar orden ni estado manual:
- graph.construction, graph.traversal, graph.shortest-path, graph.minimum-spanning
- hash.instructions, sorting.instructions
- documentation.symbols, documentation.manual, dependencies.hidden-api
- decisions.red-black-validator, audit.final-regression, audit.delivery

task_status se deriva de casilla original; status de bloque distingue cierre explícito. Completar un task transversal no inventa signoff de cada operación. Elegir algoritmo/operación/camino concreto dentro de bloques amplios y persistir su alcance en registros originales del dueño; añadir bindings finos al cerrar para evitar repetirlos. No declarar cobertura total de13TAD a partir de17IDs.

## Aún necesario
Coordinación confirmó adopción before/after04:50UTC. Tras el incidente de asignación se añadió ID obligatorio; esa extensión requiere confirmación de la tarea técnica con el comando vigente. No confundir adopción anterior con gate nuevo ya ejecutado por otro agente.

## Asignación vigente frente a recuperación histórica
El índice apunta a assignment_source; registro conserva ID/change/operation/task/instrucción/procedencia/alcance sin otro estado de implementación. La asignación actual exige --assignment-id coordination-rbt-delete-20261002 y operation red-black.delete tanto before como after. Una selección Lista/Circular, aunque tenga decisión de reapertura, falla por contradicción de asignación antes de evaluar su cierre. Seguir instrucción vigente; no pedir al usuario reconciliar solicitudes históricas sustituidas.

Una instrucción nueva que cambie bloque requiere registro nuevo e índice apuntando a él, conservando histórico. No derivar asignación de cabeceras/contadores/checkpoints ni cambiar ID para eludir cierre. Otros17bindings permiten recuperar fuentes pero no autoasignan trabajo. El propio cambio continuity.implementation no tiene assignment_source: su comando no lleva assignment-id.

La herramienta no ve ni autentica el prompt por sí sola: compara invocación con la instrucción persistida y exige al agente contrastarla con el mensaje nuevo. Si el registro difiere del mensaje vigente, actualizarlo desde ese mensaje autorizado antes de continuar; no obedecer la fotografía vieja.
