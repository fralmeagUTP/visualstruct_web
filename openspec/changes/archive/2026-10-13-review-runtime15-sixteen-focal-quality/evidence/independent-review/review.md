# QA independiente:16mediciones focales runtime15

**ACEPTAR los resultados conservados con límites. RETENER18. ACEPTAR19 como entrega parcial conjunta con fallos explícitos, sin cierre global.**

Canónico D:\MisProyectos\Web_VisualEstruct. Change review-runtime15-sixteen-focal-quality; operación audit.runtime15-sixteen-focal-independent-quality; task runtime15-sixteen-focal-independent-review; assignment coordination-runtime15-sixteen-focal-independent-qa-low-20261005. Índice/binding coinciden.346SHA coincidentes;212fuentes producto antes/después coinciden excluyendo UTC. Comprobaciones propias (evidencia local: `openspec/changes/archive/2026-10-13-review-runtime15-sixteen-focal-quality/evidence/independent-review/offline-checks.json`). Before/after propios acompañan el dictamen; no prueban cumplimiento funcional.

Se comprobaron16 entradas/setup/request: Graph cadena1..30,29arcos peso1,start1; Bellman/Dijkstra dirigidos,end30,restantes no dirigidos. Sorting80..1 salvo Radix40INT_MIN/40INT_MAX alternados.60POSTsetup porGraph y2porSorting,322totales fuera del reloj. Worker/requestPID coincide yrequest_count1. Los9cuerposgzip completos coinciden enbytes/SHA,HTTP200/successtrue y resultado ordenado exacto;3cintas retenidas coinciden enSHA/bytes ypasos1149/1152/11408. No se expandieron todos los frames ni repitió QA C/DOM.

|Resultado|Dictamen finito|
|---|---|
|6PASS|Selección14.8912436,Shell6.1267979,Quick4.4174337,Counting4.4342374,Bin12.5476024,Radix7.6314339segundos. Selección tiene sólo0.109s de margen; no acredita estabilidad.|
|3FAIL|Intercambio46.7228568,Inserción21.6815339,Merge15.9407608segundos completos. Incumplen15enesteentorno/entrada, con resultado correcto; no son fallos de equivalenciaC.|
|3ERROR|DFS,Burbuja,HeapSort:MemoryError bajo supervisor configurado2GiB, sin cuerpo completo. No inventarHTTP/pasos/duración terminada ni extrapolar proceso sincap.|
|4TIMEOUT|Bellman,Dijkstra,Prim,Kruskal detenidos tras60s desde detecciónrequest-start, sin respuesta.60noes tiempo completado; causa/fase indeterminada.|

## Entorno y artefactos de prueba

perf_counter rodea client.post yget_data:WSGI/replay/validación/algoritmo/traza/historial/serialización yconsumo completo del cuerpo. Imports/setup yposteriorparse/SHA/gzip fuera. Sincoverage/tracemalloc/profiler/allocatorQA. NoTCP/red,playerhumano ni todos losGETde páginas futuras. Counting/Bin/Radix se miden con transporte vigente y cinta completa construida; retenerla después del reloj no equivale a descargar todas las páginas durante el request. No se omitió traza para ganar15.

TESTING=True propaga excepciones:MemoryError no se convierte en unHTTP500 supuesto. La validaciónSorting que falló es incondicional y pertenece al producto, no es trabajo habilitado sólo porTESTING.

El JobObject limita commitporproceso2GiB,kill-on-close,request60s/proceso180s; no impone CPUlimit/affinity explícitos. Es seguridad de ensayo, no límite de memoria aprobado para uso educativo. Los MemoryError están condicionados por esecap; no prueban fuga/UB ni lo que ocurriría sin él. Tampoco aumentarRAM demuestra cumplimiento15. No hay pico/CPU/paging medido para atribuir lentitud a una causa única. Los3excesos completados son evidencia válida del entorno declarado, sin garantía del mismo tiempo enDesktop5051sinrestricción.

campaign-results registraPIDPopen distinto delPIDworker/request enlos16casos. UTC/algoritmo/secuencia concuerdan; es compatible conlauncher/worker y no prueba reruns. Falta árbol/provenienciaJobdelworker: aceptar código/intención de supervisor y MemoryError observado, sin certificar pico2GiB exacto. No requiere otra campaña ahora.

## Causas verificadas y candidato mínimo

Burbuja yHeapSort fallan en SortingAdapter.run:379→TraceEngine.validate_legacy_trace→LegacyTraceAdapter.round_trip→to_public→copy_value(original). TraceStep.from_legacy copia debug,stepcompleto,before/after;round_trip materializa listas semántica/proyectada completas, y normalize_steps vuelve a convertir. Son copias duplicadas reales durante validación; no se cuantificó su parte de tiempo/pico ni una fuga de memoria.

DFS sólo conservaMemoryError durante teardown deappcontext y otro al formar el diagnóstico; failure.json no existe porque su manejo también agotó memoria. No localizar por ello la primera asignación ni atribuirDFS al round_tripSorting. Los4Graph sólo tienen censura del supervisor, sinstack/perfil. Graphya valida concopy_valueidentity: eliminar deepcopySorting no es arreglo demostrado paraGraph. WireIntercambio154885953bytes confirma respuesta grande, pero no mide cuánto tiempo corresponde aserialización.

Corrección mínima candidata compartida: validar trazas inlineSorting de forma incremental/read-only con memoria acotada porpaso, evitando duplicar toda la traza para roundtrip/normalización. Preservar tipos,line/source,continuidad,before/after,final_state,console,extensiones,comparaciónroundtrip y consumidores que requieren copia independiente. No saltarvalidación ni eliminar eventos/C/algoritmos/precisión. Es candidato sustentado pordosstacktraces, no solución probada deIntercambio/Inserción/Merge niDFS/4Graph. PaginarotrosSorting/cambiocodec uoptimizarconstructoresGraph requieren alcance separado; no hay causa única verificada para todoslosfallos. Remitir escenario concreto acoordinación antes de implementar o repetir: esta QA no autoriza optimización ni ampliaciónrecursos.

## Criterios18/19

El diagnóstico«faltanmediciones»se sustituye por6PASS,3excesoscompletos y7sinrespuesta.18retenido: los3tiempos>15bastan aunque MemoryError/timeout estén condicionados porprueba. BFS11.728previo se conserva sinrerun; no sumar6PASSpara certificado universal o22/22.535/306/687/11/12/16 no se reabren.

user-delivery19-sixteen-focal.md incluye matriz/registro/diffs/QA/evidencia/instrucciones5051 ytodoslosfallos:19aceptado comoentregaparcial conjunta, cuando coordinación la entregue efectivamente; no checklist automático. Comunicar MemoryError bajo2GiB ytimeout sinrespuesta,3tiemposconcretos ycausasverificadas frente ahipótesis. Preview no comprobado/reiniciado.

Sin peticiones repetidas,nuevasmediciones,ampliaciónRAM,producto/tests/C/H,evidenciaautor,index/bindings,tasks,Git/red/deploy. Los resultados fallidos e históricos se conservan.

UTC 2026-10-05T23:14:34.877826+00:00.
