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
