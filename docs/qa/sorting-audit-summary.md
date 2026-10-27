# Auditoría didáctica de algoritmos de ordenamiento

Se ejecutaron los once algoritmos C sobre negativos, cero, duplicados y datos
desordenados. También se compararon los modos rápido y paso a paso, preservación
del multiconjunto, orden final, comparaciones, movimientos, rangos y auxiliares.

| Grupo | Resultado |
|---|---|
| Intercambio, selección, inserción y burbuja | Estado final y multiconjunto aprobados |
| Shell y HeapSort | Estado final, gaps, heapify y extracciones aprobados |
| QuickSort | Comparaciones falsas omitidas (`SORT-001`, alta) |
| MergeSort | Subrutinas/líneas C no sincronizadas (`SORT-002`, alta) |
| Counting Sort y Binsort | Rango sin límite (`SORT-004`, alta) |
| Binsort | Frames delegados sin línea C (`SORT-002`, alta) |
| Radix Sort | Desbordamiento C con `INT_MIN` (`SORT-003`, crítica) |
| Rápido frente a paso a paso, 11 algoritmos | Mismo estado final y multiconjunto |

El harness C17 ejecuta ahora los once métodos y comprueba orden final; para los
cuatro que retornan estado también exige `ORDENAMIENTO_OK`. Los defectos quedan
documentados sin modificar la implementación productiva.


## Ordenamientos: baseline C y límites actuales
Hay once métodos:intercambio,seleccion,insercion,burbuja,shell,quicksort,
mergesort,heapsort,counting_sort,binsort,radixsort. Todos trabajan sobre int;
API admite1..80elementos int32 yrechaza vacío antes del algoritmo. Cvoid
ignora NULL/n0;Merge/Counting/Bin/Radix retornan ERROR en esa entrada. Counting
usa k=max-min+1 computado enlong long,limita k a1000000 antes de reservar;
Binsort delega exactamente. Radix usa magnitudes uint32_t yprotege INT_MIN:
no se reproduce el desbordamiento histórico enel C actual de QA.

Inserción/burbuja/mezcla son estables por comparaciones estrictas/elección
izquierda;intercambio,selección,Shell,Quick,Heap no garantizan estabilidad.
Counting/Bin reconstruyen frecuencias,sinidentidad de registros iguales;
Radix tiene pasadas estables pero revierte elgrupo negativo completo: no
prometer estabilidad general de registros negativos iguales. Un array int
con duplicados sólo prueba resultado/multiconjunto, no identidad estable.

Heap usa stack O(log n) por heapify recursivo;Quick pila O(log n) promedio y
O(n) peor;Merge auxiliar O(n). Los restantes directos sonO(n²) peor,Shelldepende
de gaps;Counting/Bin O(n+k),Radix base10 O(d(n+10)). Las notasC/H concretan
cada contrato;no confundir cota teórica con métricas observadas o tiempo real.

Las ejecuciones exitosas se conservan con efecto de arreglo validado:GET
restaura resultado sin volver a ordenar;repetir Ejecutar ordena el estado
actual. Fallos no seagregan. APIstep reconstruye la última traza desde su
entrada original;UI usa la traza local. Historiales antiguos sin efecto no
pueden recuperar ejecuciones perdidas. No existe main de historial en laUI
actual:es un faltante,los callers equivalentes nativos deQA no lo sustituyen.
Fidelidad por instrucción permanece abierta ylos numéricos deGrafos pendientes.


## Binsort MEDIUM checkpoint before method closure

2026-10-02T21:21:22.522603+00:00 — coordination-sorting-binsort-medium-20261002 / sorting.binsort-instructions.13fallos resueltos,60IDs únicos vigentes(32originales intactos+28nuevos),4341eventos éxito y462ERROR C/API iguales. TapeBin wrapperCount sincutoff, parámetros suspendidos/alias/source/scopes/free, /step/pages/reload/export sinredispatch. UI5probes+2errores adicionales/0POSTextra/JSerrors/5secciones;80/k1m conserva3000912pasos en1231records/12744946bytescontenedores/DOM64.4callers exactosreusados+1nuevo C17/Doxygen0/1alloc1free0vivos. C/H/nueve cierres/commonruntime/originaltestSHA intactos. Evidencia evidence/visible-sorting-binsort-instructions ysorting-binsort-instructions-checkpoint-medium.md. Binsort NOcerrado: revisiónLOWpendiente antes de10/11;Radixnoiniciado. Límites int32/size_t64/noexhaustividad/fingerprints/noOOMreal/fixtureNULLrotulada/memoriaretendida noRSS. Global13/22,ledger121/208 sin incremento. Previewpropio5051actualizado;afterinforma,sinpush/merge/deploy.


## Estado vigente tras consolidación LOW de Radix

Los bloques anteriores son fotografías históricas: la tabla inicial y afirmaciones de ausencia de historial/fidelidad no describen el estado vigente. Once métodos deSorting consolidados dentro de sus alcances/límites registrados en openspec/changes/audit-local-quality-and-unified-controls/. Radix: sorting-radix-consolidated-closure-decision.md;48IDsaprobados,mismoIDfortalecido,UI1..80int32/C-equivalenteuint32,size_t64,mallocNULLQA/noOOMreal. Historial/main,step/pages/reload/export sinredispatch verificados. Cota11564eventos,delta/checkpoint/page;retenciónobservada49.3MB/build9.09s,densoJSON23.21MB,noSLA/fluidez/RSSuniversal. No cierra auditoríaglobal13/22/docs121/208;errores/performance/otrasplataformas límites explícitos.
