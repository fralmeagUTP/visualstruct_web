# Diseño y límites

El generador ya contenía printf para Dijkstra. `execute_book_operation` ejecutaba sólo llamadas del TAD y liberaba sus listas; por ello `session.machine.stdout` no incluía la salida del main. El frontend además sustituía la consola por la traza actual y forzaba el scroll al final.

Las instrucciones de impresión se comparten con el generador (`caller_output_program`). El intérprete acotado evalúa su AST sobre las celdas y punteros devueltos por la llamada canónica, antes de liberar listas propias. No ejecuta otra implementación del algoritmo ni formatea su resultado en Python. El soporte de `%lld` del printf del intérprete usa la conversión entera equivalente bajo su perfil ABI existente. Los eventos incluyen `caller_C_executed`, `source_role=caller`, línea y texto del caller; nunca se atribuyen al archivo C canónico ni a sus hashes. `C_instruction_events` conserva únicamente el TAD canónico.

El replay reconstruye `console_prefix` ejecutando callers anteriores. La respuesta mantiene `console_stdout` como salida de la operación actual y la vista inicial conserva stdout completo. El frontend presenta prefijo más snapshot en el cursor; no concatena eventos de nuevo al retroceder o repetir. Al abandonar una traza conserva el stdout de sesión completada. Restablecer borra el historial y su consola. Una nueva creación de grafo conserva el stdout anterior, como el main cronológico.

El scroll vertical es estable y el horizontal conserva líneas largas. La actualización sigue el final sólo cuando el lector ya estaba allí, y conserva su posición horizontal. No se agregan mensajes a funciones void.

Alcance de implementación: grafo y CSS de consola compartido. Otros módulos poseen contratos distintos (snapshots de stdout de secuenciales y consultas ABB/heap; eventos/listas en hash, RN y ordenamiento). Su diagnóstico no autoriza inferir resultados ni inyectar printf generales. La coordinación asignó su presentación a otro agente independiente.
