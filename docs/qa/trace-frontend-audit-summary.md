# Auditoría transversal de fidelidad de traza y frontend

Se contrastaron código C, backend, estados before/after, historial, consola y
renderers. También se revisaron avance, retroceso, reproducción, pausa, reinicio
y repetición desde el comienzo.

| Tarea | Resultado |
|---|---|
| 7.1 Capas C/backend/traza/historial/consola | Auditada; divergencias catalogadas |
| 7.2 Ramas, ciclos, recursión y retornos | Fallos en RN y ordenamiento (`RBT-002`, `SORT-001`) |
| 7.3 Temporales, punteros, comparaciones y rangos | Omisiones en pila, AVL, grafos y sorting |
| 7.4 Línea C, mutación y printf | Fallos `TRACE-001`, `TRACE-003` y hallazgos por TAD |
| 7.5 Controles del reproductor | Aprobado el contrato de avanzar/volver/pausar/resetear |
| 7.6 Estado final rápido/paso a paso | Aprobado en matrices existentes y los 11 sorts |
| 7.7 Cambio visual sólo en instrucción causal | Fallos de anticipación/omisión catalogados |
| 7.8 Efectos anticipados/retrasados/inventados | Fallos ABB/AVL/RN/heap/grafo/sorting catalogados |
| 7.9 Identidad, enlaces, posiciones, colores y temporales | Auditada por las 13 familias |

## Matriz por TAD

| TAD | Evidencia transversal principal |
|---|---|
| Pila | `STACK-001`, `STACK-002`: código inexistente y temporal omitido |
| Cola | `QUEUE-001`: consultas no fieles al C |
| Cola de prioridad | `PRIORITY-001/002`: orden y frente divergentes |
| Lista enlazada | `LINKED-001`: operaciones Python sin C |
| Lista circular | `CIRCULAR-001`: autoenlace de un nodo no dibujado |
| Sublista | `SUBLIST-001/002`: identidad duplicada y destrucción omitida |
| ABB | `ABB-001`: copia temporal del sucesor omitida |
| AVL | `AVL-001`: primera mitad de rotación doble omitida |
| Rojo-negro | `RBT-001/002`: recoloreo anticipado y ramas de borrado falsas |
| Montículo | `HEAP-001`: estados sift omitidos |
| Grafo | `GRAPH-001`–`006`: contrato, recorridos, temporales y MST divergentes |
| Hash | `HASH-001/002`: rehash y función hash incompatibles |
| Ordenamiento | `SORT-001`–`004`: comparaciones, líneas, overflow y rango |

## Controles y consistencia global

`createTracePlayer` restaura el snapshot inicial en reset, aplica `state_after`
al avanzar y el `state_after` anterior al retroceder. Las pruebas E2E existentes
cubren controles secuenciales y hash, reproducción jerárquica y modo rápido de
grafos. El riesgo restante es contractual: una traza discontinua o con línea
fuente falsa todavía es aceptada (`TRACE-002/003`).

La fase queda auditada; “completada” significa cobertura y evidencia cerradas,
no que los defectos funcionales hayan sido corregidos.
