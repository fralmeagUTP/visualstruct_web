# Dieciséis mediciones focales de rendimiento: resultado y límites

Proyecto canónico: D:\MisProyectos\Web_VisualEstruct. Cambio audit-local-quality-and-unified-controls; operación audit.runtime15-sixteen-focal-plain-measurements; assignment coordination-runtime15-sixteen-focal20-low-20261005. Autorización y transcripción literal en runtime15-sixteen-focal20-low.md. Sol LOW; máximo20min desde22:49:33UTC. Medición finalizó dentro del plazo; sin optimización, cambios de producto ni nuevas familias funcionales.

Se intentaron las16 solicitudes algorítmicas una sola vez, secuencialmente:5Graph y11Sorting. BFS no se repitió; conserva su PASS previo11,728s para el caso30/29. Resultado nuevo:6PASS finitos,3FAIL medidos >15s,3ERROR MemoryError y4TIMEOUT operativos. Criterio18 debe permanecer retenido hasta dictamen independiente y tratamiento coordinado de estos fallos; no22/22 ni certificado universal. Checklist20/22 intacto;11/12/16 y cobertura/procedencia anteriores no se reabrieron.

| Algoritmo | Petición completa (s) | HTTP | Pasos lógicos | Resultado |
|---|---:|---:|---:|---|
| run_dfs | — | — | — | ERROR |
| run_bellman_ford | timeout60s | — | — | TIMEOUT |
| run_dijkstra | timeout60s | — | — | TIMEOUT |
| run_prim | timeout60s | — | — | TIMEOUT |
| run_kruskal | timeout60s | — | — | TIMEOUT |
| intercambio | 46.723 | 200 | 38248 | FAIL |
| seleccion | 14.891 | 200 | 12005 | PASS |
| insercion | 21.682 | 200 | 16444 | FAIL |
| burbuja | — | — | — | ERROR |
| shell | 6.127 | 200 | 4708 | PASS |
| quicksort | 4.417 | 200 | 2293 | PASS |
| mergesort | 15.941 | 200 | 5273 | FAIL |
| heapsort | — | — | — | ERROR |
| counting_sort | 4.434 | 200 | 1149 | PASS |
| binsort | 12.548 | 200 | 1152 | PASS |
| radixsort | 7.631 | 200 | 11408 | PASS |

## Protocolo y evidencia

Casos exactos en cases.json. Graph: cadena30v/29arcos unitarios, inicio1; dirigida para Bellman-Ford/Dijkstra con destino30, no dirigida para DFS/Prim/Kruskal. Sorting:80..1 salvo Radix,40INT_MIN y40INT_MAX alternados. Valores/dominios admitidos y contratos actuales conservados, sin UB ni C nativo nuevo.

Cliente Flask/WSGI privado del producto canónico, app.testing=True sólo para cliente/sesión privada; ningún allocator QA, monkeypatch, coverage, tracemalloc, profiler o concurrencia de casos. Preparación fuera del reloj mediante rutas reales:60POST Graph por caso y2POST Sorting por caso (322de preparación en total). Historia/estado antes de cada ejecución quedaron en preparation.json. Timer perf_counter antes delPOST hasta response.get_data completo: incluye cliente/validación/replay/algoritmo/construcción fiel de traza/historial/serialización y consumo del cuerpo. No mide espera humana del player ni latencia TCP/red del preview. Imports/preparación/JSONparse/gzip/verificación posteriores quedan fuera; el tiempo del proceso completo no sustituye el tiempo de petición.

Cada una de las9 respuestas completas conserva complete-response.json.gz, bytes ySHA raw, HTTP200/success=true, resultado correcto para la entrada, algoritmo solicitado/historial y traza. Verificación posterior deSHA ybytes delgzip coincide en las9. Inline se preserva entero; Counting/Bin/Radix mantienen transporte paginado vigente y además retained-complete-tape.json.gz con TODOS registros/checkpoints/source_code de la cinta existente, conteo lógico ySHA verificados. Esa captura ocurre después del reloj sin peticiones extra ni redispatch. No se expandieron/controlaron todos los frames ni se repitió la certificación C/browser; se reutiliza aceptación funcional/instruccional previa en sus alcances y sólo se comprueba que esta solicitud produjo el resultado/algoritmo/traza esperados.

212 fuentes app/*.py ydocs/tads_C/*.c/.h tienen SHA iguales antes/después, cero discrepancias. Herramienta/entorno/pid/entrada/request/secuencia/harnessSHA están en worker-start.json,request-start.json,plain-result.json,campaign-start/results/exit ycanonical-sources-before.json. summary.json contiene el contraste mínimo y los9 wire SHA; tape-preservation-checks.json verifica las3 cintas. Ninguna fuente/tests/C/H fue editada; no preview5051, servernuevo, commit/push/merge/deploy ni campaña funcional.

## Fallos y fronteras operativas

Intercambio46,723s, Inserción21,682s yMergeSort15,941s completaron y excedieron el presupuesto15 inclusivo. Selección14,891s está dentro en esta observación con margen pequeño; no demuestra estabilidad ni un máximo universal.

DFS,Burbuja,HeapSort produjeron MemoryError con límite decommit porproceso2GiB. Se conservan stderr/entrada/request-start/resultado de supervisor; no hubo respuesta completa, por lo que no se inventaHTTP, resultado, pasos ni duración de respuesta completa. Es un fallo observado bajo ese límite operacional, no prueba de fuga/ownership ni afirmación sobre un proceso sin límite. Los4algoritmos Graph restantes se detuvieron a60s desde marcador de inicio sin respuesta completa; se registra TIMEOUT60s, no una duración completada ni un resultado/traza ficticios. Límites extras:180s porproceso incluyendo setup/grabación,20min bloque. No se muestreó memoria para perfilar; el límite lo impuso unJobObject deWindows. Cierres deprocesos propios no tocaron preview. No se reintentó ningún caso.

Una muestra porentrada no agota densidades/pesos/formas/historias ni operaciones algorítmicas deotrosTAD/109opciones. Los16casos no son16tests pytest ni se suman a535. Los fallos requieren coordinación nueva y acotada si se desea optimizar; este bloque expresamente no cambia producto ni extiende campaña. QA debe dictaminar los datos conservados en review-runtime15-sixteen-focal-quality, con su before/after ybinding nuevo.
