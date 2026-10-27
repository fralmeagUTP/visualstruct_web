# Counting sort: diagnóstico de alcance y estado parcial

Instrucción nueva coordination-sorting-counting-scope-review-low-20261002 / sorting.counting-scope-review-low. Corrige interpretación del cierre anterior; no reejecuta los ocho métodos ni los seis casos ya verificados. Proyecto canónico D:\MisProyectos\Web_VisualEstruct, after es informe solamente.

Counting es PARCIAL para el objetivo de fidelidad en entradas admitidas. La evidencia previa41tests/416eventos/832restauraciones de seis casos pequeños sigue válida como fotografía; no prueba completitud del método. El corte nuevo n<=4/k<=4 cambió calidad de traza de entradas admitidas, aunque no cambió resultado ni aceptación. La decisión sorting-counting-resource-bound-decision.md queda superada en cuanto a usar ese corte como solución suficiente del objetivo. El guard sigue presente hasta corrección coordinada; este diagnóstico no implementa solución compleja.

Por qué se introdujo: nuevo emit copia arreglo yconteo, evento debug vuelve a copiar conteo ycontexto crea kobjetosbucket por evento. El for de reconstrucción ejecuta controles aun en frecuencias cero, O(k)eventos; conservar kfrecuencias completas por evento provoca O(k²)estado, además del JSON antes/después yDOM. A k=1000000, solo producto de ~3kcontroles vacíos por kfrecuencias es del orden3*10^12celdas, sin contar objetos/JSON. Es estimación estática, no consumo medido ni prueba ejecutada. El corte4 fue una protección temporal demasiado ligada a fixtures; no corresponde al contrato ni a un límiteUI existente. Quitar guard sin cambiar almacenamiento expondría agotamiento memoria/latencia/HTTP/bloqueoDOM; mantenerlo como final deja fidelidad incompleta.

Inspección AST de SortingInterpreter.run y módulos (dispatch-inventory.json):

| Implementación | Corte adicional por tamaño/rango de fixture | Límite existente y estado |
|---|---|---|
| Intercambio | ninguno encontrado | app1..80int32; siempre run_intercambio_trace |
| Selección | ninguno encontrado | app1..80int32; siempre run_seleccion_trace |
| Inserción | ninguno encontrado | app1..80int32; siempre run_insercion_trace |
| Burbuja | ninguno encontrado | app1..80int32; siempre run_burbuja_trace |
| Shell | ninguno encontrado | app1..80int32; siempre run_shell_trace |
| Quick sort | ninguno encontrado | app1..80int32; siempre run_quicksort_trace |
| Merge sort | ninguno encontrado | app1..80int32; siempre run_mergesort_trace |
| Heap sort | ninguno encontrado | app1..80int32; siempre run_heapsort_trace |
| Counting sort | n<=4 yk<=4 | entradaapp1..80int32/k<=1000000, fuera del corte ruta agregada |

Controles n1, intervalo/raíces/basesrecursivas en los ocho son flujo C, no cortes para cambiar calidad de traza. No se ejecutaron esos métodos. También materializan snapshots por evento: costo O(n*E) yMerge añadeauxiliarO(n), HeapnodosO(n); no se encontró presupuesto debytes/eventos/paginación que garantice respuesta práctica en todoel dominio. Sus cierres previos son finitos y sepreservan, no se recertifican como universales.

Límites reales: SortingAdapter._MAX_SIZE80 yint32 para creacionesmanuales/aleatorias; templates/sorting/structure.html muestraCantidad max80 yMáximotécnico80. Manual estexto, backendimpone80. CountingC/backend rango<=1000000; no existe límiteUI de cuatro ni condiciónn4/k4 en contrato. El guard estáenrunline136. Adapter materializa rawsteps, before/after/pedagogy/debug ydevuelve JSONcompleto; playeractual consume stepsmaterializados. No hay soporte lazy/paginado para Counting. El historial guarda efectodearreglo, no un repositorio existente de trazas inmutables paginadas: ese componente debe diseñarse explícitamente, no asumirlo.

Cuatro probes nuevos fuera del corte, sin browser/compilación/suitesmasivas (outside-scope-probes.json): [5,4,3,2,1] n5/k5->14frames;[0,5]n2/k6->8;[0,1000]n2/k1001->8;80repetidos[2]n80/k1->164. Todos aceptados/resultadoordenadocorrecto/métricasLOW; todos0instruction_event,0helpersminmax,0freeexplícito/0contextoCounting. JSON44582,27542,57515,540069bytesrespectivamente. Son evidencia diagnóstica de pérdida de fidelidad; no cierreC/UI ni nuevoscasos añadidos a41testshistóricos. No capmillóntrace ejecutado.

Solución recomendada: mismo intérprete semántico para todaentradaCounting admitida, cambiar representación/transporte a frecuencias sparse(densecalloc lógico condefault0), deltas yestados inmutables; para rangograndes, manifest/páginas yspans lossless deeventoscontrolesceros que seexpandenen cada paso. UIbucketsvirtualizados con acceso a cualquier índice válido. Nunca fallbackagregado según tamaño; formato puede cambiar por presupuesto explícito de transporte sin perder eventos. No bajar80/rango1000000 ni rechazarentradas válidas ni omitircontroles/sufijos/ceros. Otrasocho rutas/player quedanintactos; adaptación opt-inCounting. Plan siguiente sorting-counting-expanded-fidelity-plan.md exige nueva asignación/guardas yrevisión del protocolo antes de implementarcomplejo.

size_t64/Cint32 permanecen explícitos; fullspan32bit potencialmenteinseguro ySIZE_MAXtruebranch noejecutados/verificados. C/H yproducción no modificados en esteLOW. Preview4716/21140D/run.py127.0.0.1:5051 conservado. Global13/22/docs121/208 sinavance; ocho cierres finitos previos,Countingparcial,Binsort/Radixpendientes. No pasar aBinsort antes decoordinar correcciónCounting.
