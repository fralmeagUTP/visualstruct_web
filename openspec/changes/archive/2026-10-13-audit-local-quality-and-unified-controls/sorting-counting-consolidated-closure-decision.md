# Counting: revisión consolidada y cierre acotado

Fecha 2026-10-02T20:08:31.886208+00:00. Proyecto D:\MisProyectos\Web_VisualEstruct. Asignación coordination-sorting-counting-consolidated-review-low-20261002; operación sorting.counting-expanded-fidelity. Instrucción vigente sorting-counting-consolidated-review-authorized-low.md. No cambios productivos, C/H ni reapertura de los otros ocho métodos.

## Decisión y criterio

Counting queda verificado como noveno método de once para el dominio UI vigente en el entorno observado Windows/int32/size_t64: n1..80, enteros int32, éxito con k=max-min+1<=1000000; rechazo de rango superior y reservaNULL controlada. Se cierra la fidelidad ampliada mediante equivalencia estructural de la representación más oráculos independientes y observación API/UI. El criterio exige dispatch único sin cutoff de fixtures, restauración de cada evento lógico/scopes/source/condición, cero implícito exacto/calloc-free, guards/ERROR/retirada sin mutar estado aceptado, replay/ownership acotados y caller/documentación coherentes. No exige enumerar todas las entradas ni ejecutar UB o agotar RAM real.

Estos gates están satisfechos. La antigua conclusión PARCIAL por cutoff n4/k4 y después por ausencia de traza de error queda superada por código/evidencia actuales; no se borra esa historia. No se detectó un hueco funcional pendiente en este alcance que justifique otro bloque Counting. Nueve de once es estado de métodos bajo criterios/casos explícitos, no cierre global de auditoría ni porcentaje de tiempo.

## Trazabilidad requisito → código → evidencia

| Gate | Código/regla revisada | Evidencia canónica reutilizada |
|---|---|---|
| Dominio y mismo intérprete | SortingAdapter valida1..80/int32; SortingInterpreter despacha siempre run_counting_sparse_trace para Counting, sin n4/k4; rango se verifica antes de contar | source-review.json; cinco expanded reproducers dentro de59IDs; casos n5/k5,n2/k6,n8/k17,n80/k1,n80/k80,nearMin/Max,n2/k1001 |
| Instrucción/C/contexto | counting_sparse_instructions emite controles/scopes tipados, aliases helper, variables anteriores/cambios, array_write y count_write separados, free y retorno; renderer sólo cambia transporte | seis oráculos C congelados416eventos, ocho oráculos fuera4 completos5504eventos; tests permanentes vigentes en59IDs |
| Compresión exacta y límites | SparseCounts defaults0 y<=n buckets ocupados. append_zero rechaza cualquier bucket ocupado y representa por posición exactamente rebuild_test=true,bucket_test=false,rebuild_increment; _zero restaura i/previous/changed. Deltas/checkpoints32registros y búsqueda por prefijos conservan posición lógica | revisión de counting_sparse_tape.py; pruebas de páginas/inmutabilidad/ventanas; streams3.000.051/3.000.909 y muestras de fronteras/centro; no inferir exactitud sólo del digest |
| Recursos y transporte | registros físicos O(n), estados sparse O(n), copias cambiantes O(n²) con n<=80; cero spans no crecen por k. Dense elegido por presupuesto, no semántica. GET<=128frames, UI64buckets, caché4páginas64+seed16, almacen32trazas/128MiBcontabilizados/TTL900s/FIFO y2builders | visible-sorting-counting-integration/summary.json y browser-final; n80/rango1m inicial126713bytes/DOM1820/window64, páginas acotadas; medidas históricas fechadas, no RAMglobal/concurrencia exhaustiva |
| Errores sin aceptar operación | rango corta SIZE_MAX si firstORtrue; callocNULL muestra ptrNULL inicializado, allocations/frees0, guard true, ERROR0 yscope vacío. Estado aceptado capturado antes de selección provisional, incluida last_operation | cuatro oráculos450eventos;13IDs deerror; errors-final.log conserva defecto previo, regressions-final.log prueba corrección; 3probes browser150restauraciones |
| Replay y ownership | source inmutable por sesión, GET no renuevaTTL/noSort; navgeneration descarta obsoletos, transient retry conserva desired; failedtrace separa modelo aceptado e intento; export conserva tape y ambos estados |59IDs, browser-fault-after y browser-report de errores; dos reloads preview reales de rango; TESTINGfixtureNULL rotulada no afirma reload del preview |
| Historial/main/C/H/doc | run aceptado produce un efecto y llamada; fallos no se agregan; reconstrucción sin ejecutar C/Pythonsort. Fuente/doc preservada | callers/downloads y C17/Doxygen previos; dos callers de rechazos reales C17/Doxygen0/cero alloc-free-vivos; protected-hashes actual coincide |

## Vigencia y regresión mínima

source-review.json compara los diez hashes productivos actuales con la última ejecución final de59IDs: todos iguales. C/H, runtime común y ocho módulos cerrados también iguales. Lista de IDs coincide con collected-ids.log:59únicos=46previos+13errores. No sumar41/35/46/58/59ni restauraciones/callers: son vistas y subconjuntos de evidencia superpuesta.

Sin código nuevo, no se repitieron suites largas/oráculos/browser. Se ejecutaron sólo tres IDs existentes sensibles a la última corrección: last_operation con run previo, rotulado MemoryError del modelo y página máxima primera/medio/final. Pasaron3/3 en2.19s; son subconjunto de59, no62IDs. Preview18188/14756 canónico permanece en127.0.0.1:5051, sin reinicio ni probes activos al terminar.

## Límites y huecos

Huecos funcionales abiertos detectados en el alcance de Counting revisado: ninguno. El soporte/cierre se limita al entorno int32/size_t64 observado y al dominio UI. SIZE_MAX=true es inalcanzable bajo k<=1m en ese entorno; ABI32bit y fullspan inseguro no se ejecutaron ni certificaron. Las guardasNULL/n0/helperNULL nativas existen como probes separados fuera del dominio UI, que rechaza vacío/invalidantes antes del algoritmo.

Los digests cubren todos los registros escalares ordenados, pero fingerprints de arrays/frecuencias pueden colisionar: no equivalen a snapshots completos de cada celda grande ni prueba exhaustiva. La equivalencia de spans procede de las reglas revisadas y oráculos completos; los digests sólo refuerzan la cobertura del recorrido máximo.

callocNULL es inyección segura en Cobservador y en appTESTING, no OOM real. La traza productiva es un modelo C-equivalente con real_c_execution=false; MemoryError del modelo y fallo de transporte son distintos. La fixture Chromium simula respuesta de appTESTING y se rotula; sólo los dos errores de rango se ejecutan realmente en preview. No certificación de recuperación ante OOMglobal. Tampoco se atribuye QA a controles de práctica/comparación ausentes en template, otras plataformas o QA global móvil.

## Continuación preparada

sorting-binsort-baseline-plan-low.md define el siguiente baseline LOW. El C canónico ordenar_binsort delega exactamente en ordenar_counting_sort; por tanto el baseline debe observar wrapper/call/retorno y contrato heredado, no inventar buckets independientes ni repetir una suite standalone del Counting cerrado. No implementación ni ejecución Binsort en esta revisión; necesita su asignación vigente y guarda before. Radix también pendiente. Global13/22 y ledger121/208 permanecen; sin commit/push/merge/deploy/red.
