# Evidencia local conjunta — 2026-10-27

Base bfe7ab0284a4735cd5660dcc0c88c5ac05b8a6ac; copia aislada visualstruct-syntax-review. Sin publicación ni despliegue.

## Sintaxis

Sorting main se renderizaba como didactic-history-main fuera del tokenizador anterior: 0 tokens semánticos antes, 7 después, fuente idéntica. No se confirmó que Hash TAD inicial estuviera sin colores. Renderizador dependiente del título tenía una ruta dinámica con título acentuado sin colores; prueba dedicada confirma corrección compartida.

Tokenizador común usa nodos de texto, nunca interpreta código como HTML. Conserva texto, tabs/CRLF, filas/listeners, línea activa y scroll. Inventario13estructuras+13ayudas+manual; pruebas de cinco familias cubren ejecutar, siguiente/anterior, operación/reset, ampliación y pestañas, copia/descarga conforme rutas existentes. ABB no tiene ruta main descargable; se verifican copia main y descarga C fuente real.

27 passed in153.31s: python -m pytest tests/test_c_syntax_highlight_e2e.py tests/test_caller_console_history.py tests/test_graph_console_history_dom.py -q --tb=short. Desglose8 sintaxis +17 C17 nativo +2 Chromium consola graph. Tokenizador Node también PASS.

Capturas representativas guardadas en ../syntax-evidence: syntax-sorting-main-before.png, syntax-sorting-main-after.png, syntax-{seq,hier,graph,hash,sorting}-expanded.png y syntax-help.png. Evidencia sólo de esta copia local.

## Consola integrada

Graph ejecuta printf real del caller C sobre máquina canónica, muestra prefijo de operaciones y stdout al cursor sin duplicar ni adelantar. Componentes publican texto literal y conservan scroll horizontal y revisión manual vertical. Se comparte publish con ledger de otras familias.

Bug Lista/ABB reproducido: final->retroceso->operación nueva perdía stdout ya observado. Ledger separa current visible de emitted observado; cachev2. Harness con trazas auténticas PASS antes/después/replay/reset/reload y parcial sin anticipación. Prueba real navegador adicional Lista/ABB en preparación.

Hash y Sorting: operaciones reales exitosas pero backend devuelve stdout vacío; no se inventó salida. Sorting main contiene printf sin ejecución caller en estas rutas. Hueco pendiente explícito, no declarar toda consola cerrada. Presupuesto aleatorio de traza anterior inconcluso, no se modifican controles.

C/H docs/tads_C comparados con HEAD sin diferencias de contenido; layout adaptativo permanece. Ningún cambio de VPS, Docker5050 ni sesión Chrome del usuario.

## Diagnóstico adicional navegador Lista/ABB
Primera prueba nueva2fails: ABB normal no carga traza navegable (expectativa de toggle incorrecta); Lista expuso defecto de integración real: ConsoleHistory.render con trace=null ignoraba raw stdout normal. Reparación acotada pendiente de revalidación, sin alterar generadores C ni publicar.27pruebas anteriores no cubrían esta rama normal Lista.

Lista normal corregida conservando identidad de execution_trace recibida y último cursor en modo rápido; Chromium confirmó dos printf literales +reload/reset. Revalidación sintaxis secuencial1passed13.44s (7deselected). ChecksJS PASS. Fallo siguiente del harness pedía POST a Siguiente; en Lista se prepara mediante Ejecutar, se ajusta test sin tocar producto. Manual Lista/ABB aún esperando runfinal.

Lista prueba navegador completa PASS: normal y manual x2, prefijo, avance/retroceso, nuevaoperación, replay sin POST, recarga/reset. Captura ../syntax-evidence/console-lista-integrated.png revisada visualmente. ABB normalx2literal/reload/reset y manualpreparación/prefijovacío PASS; harness usó selector hier-sim-end eliminado por UIactual y se adapta a controles existentes. No defecto producto añadido confirmado.

## Cierre acotado local
ABB último run1passed1deselected15.22s usando Anterior/Siguiente existentes: normalx2literal y manualx2, retroceso/avance sin POST, reload/reset, errors[]. Lista caso completo PASS previo. Capturas console-abb-integrated.png y console-lista-integrated.png en ../syntax-evidence. Totalcasos distintos verificados29 (27conjuntos +2familias); después fixLista revalidaciónsyntaxseq1passed. No CIglobal ni desplegado. Pendientes backendHash/Sorting y presupuestorandomprevio mantienen clasificación separada.
