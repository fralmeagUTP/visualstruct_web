# Tareas

## 1. Congelar contratos y regresiones

- [x] 1.1 Importar los 29 fixtures mínimos y convertir cada `case_id` en una prueba de regresión que falle por la discrepancia exacta.
- [x] 1.2 Documentar la decisión C/Python/UI para dirección y pesos de grafo, claves y rehash hash, prioridad estable y operaciones secuenciales faltantes.
- [x] 1.3 Versionar los contratos afectados y definir migración o rechazo explícito de sesiones antiguas.
- [x] 1.4 Establecer gates por lote: C17 estricto, ASan/UBSan, unidad, integración, reproducción y UI.

## 2. P0: eliminar comportamiento indefinido

- [x] 2.1 Corregir `SORT-003` para ordenar `INT_MIN` sin negación con overflow ni pérdida de valores.
- [x] 2.2 Añadir pruebas C y Python con `INT_MIN`, `INT_MAX`, negativos, cero, duplicados y arreglos unitarios/vacíos.
- [x] 2.3 Ejecutar Radix Sort bajo UBSan/ASan y verificar multiconjunto, orden y equivalencia rápido/paso a paso.

## 3. P1: contratos de grafos

- [x] 3.1 Corregir `GRAPH-001` y `GRAPH-002`: extremos, duplicados, dirección y representación exacta del tipo de peso.
- [x] 3.2 Corregir `GRAPH-003`: unificar el orden observable de BFS/DFS con el retorno real del C.
- [x] 3.3 Corregir `GRAPH-004`: aplicar una única política para pesos negativos en Dijkstra.
- [x] 3.4 Corregir `GRAPH-006`: distinguir MST de bosque, conectividad y restricciones de grafos dirigidos.
- [x] 3.5 Añadir regresiones de grafos dirigidos/no dirigidos, decimales o rechazo tipado, desconectados, duplicados y extremos ausentes.

## 4. P1: hash y estructuras secuenciales

- [x] 4.1 Corregir `HASH-001`: implementar y trazar rehash en C o retirar el rehash del contrato ejecutable.
- [x] 4.2 Corregir `HASH-002`: usar el mismo dominio de claves y función hash determinista en C, backend y UI.
- [x] 4.3 Corregir `LINKED-001`: implementar/mapear las operaciones faltantes o retirarlas del contrato público.
- [x] 4.4 Corregir `PRIORITY-001` y `PRIORITY-002`: algoritmo, desempate y consulta de frente idénticos al C.
- [x] 4.5 Corregir `QUEUE-001`, `STACK-001`: todos los snippets mostrados deben compilar y corresponder a funciones reales.
- [x] 4.6 Ejecutar regresiones de colisiones, rehash, reinicio de proceso, duplicados, estructuras vacías y prioridades iguales.

## 5. P1: rojo-negro y límites de ordenamiento

- [x] 5.1 Corregir `RBT-002` con un planificador de eliminación basado en eventos reales y snapshots del fix-up.
- [x] 5.2 Corregir `SORT-004` validando la amplitud antes de cualquier reserva C o Python.
- [x] 5.3 Probar eliminaciones RN hoja/un hijo/dos hijos y todos los casos de hermano del fix-up.
- [x] 5.4 Probar límites aceptados/rechazados de Counting y Bin Sort y verificar un error reproducible sin reserva excesiva.

## 6. P2: estados intermedios de TAD

- [x] 6.1 Corregir `ABB-001`: mostrar copia del sucesor y eliminación como estados causales separados.
- [x] 6.2 Corregir `AVL-001`: mostrar ambas rotaciones de LR/RL con enlaces, alturas y factores intermedios.
- [x] 6.3 Corregir `RBT-001`: aplicar recoloreos y rotaciones únicamente en su asignación C.
- [x] 6.4 Corregir `HEAP-001`: mostrar append, comparaciones y swaps de sift-up/sift-down.
- [x] 6.5 Corregir `STACK-002`: visualizar nodo temporal, valor y enlace antes de incorporarlo a la pila.
- [x] 6.6 Corregir `CIRCULAR-001`: representar el autoenlace del nodo único.
- [x] 6.7 Corregir `SUBLIST-001` y `SUBLIST-002`: preservar padres duplicados por identidad y trazar liberaciones hijo-a-padre.

## 7. P2: algoritmos, consola y contrato de traza

- [x] 7.1 Corregir `GRAPH-005`: visualizar inicialización, selección, relajaciones, distancias, predecesores y visitados.
- [x] 7.2 Corregir `SORT-001`: emitir toda evaluación de condición de Quicksort, incluidas las falsas.
- [x] 7.3 Corregir `SORT-002`: cargar auxiliares transitivos y mapear cada frame Merge/Bin Sort a su línea C.
- [x] 7.4 Corregir `TRACE-001`: transportar y reproducir consola desde eventos, sin inferir `printf` desde el código.
- [x] 7.5 Corregir `TRACE-002`: validar continuidad profunda `after[i] == before[i+1]` o exigir `rebase` explícito.
- [x] 7.6 Corregir `TRACE-003`: validar rango y texto normalizado de la línea resaltada.

## 8. Integración visual y reproducción

- [x] 8.1 Verificar para los 13 TAD que cada frame aparece sólo después de la instrucción C causal.
- [x] 8.2 Verificar temporales, identidades, enlaces, colores, rangos activos y estructuras auxiliares con valores duplicados.
- [x] 8.3 Probar avanzar, retroceder, pausar, reproducir, reiniciar y repetir sin deriva.
- [x] 8.4 Confirmar equivalencia entre modo rápido, paso a paso, backend y estado final C.
- [x] 8.5 Medir tamaño/latencia de trazas y conservar límites de sesión y respuesta.

## 9. Cierre y publicación

- [x] 9.1 Ejecutar las 29 regresiones y comprobar que cada discrepancia original quedó corregida sin debilitar el oráculo.
- [x] 9.2 Repetir las 5.000 secuencias deterministas y reducir/publicar cualquier divergencia nueva.
- [x] 9.3 Ejecutar los 13 harnesses con C17 estricto y la matriz Linux ASan/UBSan.
- [x] 9.4 Ejecutar la suite backend/frontend completa y pruebas UI frame por frame.
- [x] 9.5 Actualizar inventario, resultados QA, documentación de contratos y matriz de compatibilidad.
- [x] 9.6 Validar OpenSpec en modo estricto y publicar evidencia de cierre por `case_id`.
