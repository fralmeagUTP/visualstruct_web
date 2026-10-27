# Evidencia finita — 2026-10-27

Base: bfe7ab0284a4735cd5660dcc0c88c5ac05b8a6ac. Rama local `fix/caller-stdout-20261027`, worktree `visualstruct-stdout-review`. Sin commit, push ni despliegue. C/H originales intactos y verificados por los hashes de `book_source.HASHES`.

## Diagnóstico

El main ya imprimía Dijkstra; la ejecución visual sólo llamaba al TAD y devolvía stdout vacío. El renderer mostraba únicamente la traza actual. Ahora el caller interpretado ejecuta las mismas sentencias de impresión antes de liberar sus resultados, y la consola presenta prefijo de sesión más stdout al cursor.

## Verificación

- `python -m pytest tests/test_caller_console_history.py -q --disable-warnings --maxfail=1`: **17 passed in 56.74s** (repetición final). Dieciséis callers compilados con GCC C17 `-Wall -Wextra -Wpedantic -Werror`, stdout nativo exactamente igual a prefijo + stdout interpretado; incluye cuatro caminos de Dijkstra, BFS/DFS/Bellman-Ford/Prim/Kruskal, vecinos, listas, existencia y costo presente/ausente. Caso adicional de mutaciones void sin mensajes inventados. Prueba modo normal y pasos, snapshots de retroceso/replay y recarga del viewmodel.
- `python -m pytest tests/test_graph_console_history_dom.py -q --disable-warnings --maxfail=1`: **2 passed in 34.39s**, Chromium aislado. Componente real con traza real: cursor inicial/final/medio, repetición sin duplicados, scroll manual conservado, seguimiento al final y overflow horizontal. Página completa con servidor efímero localhost: preparación HTTP de sesión, botón Dijkstra, modo normal/pasos, anterior/siguiente, cero nuevos POST al repetir, recarga con salida idéntica y cero errores JS.
- Regresión dirigida `test_graph_shared_main.py`, `test_graph_default_weight_caller.py`, `test_graph_mark_history.py`, `test_graph_snapshot_pool.py`, `test_graph_routes.py`: **61 passed, 1 failed in 466.35s**. El único fallo, `test_generate_random_graph_via_route`, espera HTTP200 para grafo aleatorio de siete vértices sin semilla en modo pasos y recibe HTTP400 al superar 4000 eventos. La comprobación inicial en `visualstruct-publish-review` también falló (**1 failed in 0.81s**), pero se verificó después que su HEAD era 59e84f8, por lo que no constituye evidencia de bfe7. En un worktree detached limpio bfe7 (`vs-cb`), el mismo test sin semilla pasó (**1 passed in 11.04s**). Al ser aleatorio sin semilla no se atribuye el fallo de forma concluyente a preexistencia ni al overhead nuevo del caller. Queda una limitación abierta del caso aleatorio en modo pasos; no se sube el presupuesto ni se oculta. No afecta el oráculo finito de consultas verificadas.
- `node --check static/js/graph.js` y `git diff --check`: sin errores.

La primera ejecución Chromium en sandbox falló antes de iniciar navegador por `WinError5` en named pipe. La ejecución local escalada fue aprobada y completó las pruebas; no se usaron perfiles personales.

## Artefactos

`qa/caller-console-20261027/` conserva `native-report.json`, cuatro `*-main.c` generados, cuatro `*.stdout.txt` de ejecución nativa, `native-tests.log`, `capture_native.py` reproducible y PNG de componente/página completa.

| Dijkstra | stdout de la consulta (además del prefijo real) |
| --- | --- |
| Ruta 1 a 3 | `Dijkstra: estado=0 1->2(2) 2->3(3) \| costo=5` |
| Sin ruta | `Dijkstra: estado=2` |
| Inicio=destino | `Dijkstra: estado=0 (sin arcos; resultado valido) \| costo=0` |
| Peso negativo | `Dijkstra: estado=3` |

## Límites

No es una auditoría universal ni una validación de publicación. La implementación de caller y reconstrucción del prefijo se limita al grafo. El CSS de scroll es compartido; la presentación de otras familias fue asignada por coordinación a otro agente. El renderer de grafo utiliza `ConsoleHistory.publish` cuando ese helper está disponible y mantiene fallback standalone; las pruebas de esta rama validaron el fallback, por lo que la integración con el helper compartido requiere la prueba de composición del coordinador.

El patch textual completo pasó `git apply --check` sobre bfe7 limpio (`vs-cb`). El primer intento de baseline con nombre largo falló por un archivo histórico que supera MAX_PATH; Git retiró ese checkout fallido y el segundo checkout corto con core.longpaths=true completó correctamente. Ningún archivo C/H fue modificado.
