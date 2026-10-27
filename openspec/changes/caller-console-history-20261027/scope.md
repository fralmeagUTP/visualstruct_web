# Caller y consola C

Asignación vigente delegada por coordinación el 2026-10-27: corregir stdout real del caller de consultas, empezando por Dijkstra, y conservar su historial visible con navegación por cursor y scroll usable. Trabajo aislado desde bfe7ab0; sin publicación, commit ni cambios en C/H canónicos. No reabre auditorías históricas.

El main generado es la fuente del contrato del caller. Cada printf visible debe provenir de su ejecución, nunca de mensajes de dominio inventados. El prefijo de operaciones anteriores permanece al retroceder dentro de la operación actual, cuyo stdout sólo aparece cuando se ejecuta. Replay no duplica salida.
