# Diseño: auditoría de fidelidad C y visualización didáctica

## Principio de comparación

La auditoría usa seis capas observables:

1. **C real:** instrucciones y estado obtenidos de `docs/tads_C/` mediante harness instrumentado.
2. **Backend:** estado del dominio Python y estado visual serializado por el adapter.
3. **Traza:** `execution_trace`, incluyendo línea, evento, etapa, before/after y metadata.
4. **Historial técnico:** operaciones mutantes persistidas y replay efectivo.
5. **Consola:** salidas que representan los `printf` realmente alcanzados.
6. **Frontend:** estado renderizado, resaltado de código y controles de reproducción.

El código C es el oráculo semántico. Una adaptación visual puede abstraer direcciones de memoria,
pero debe preservar identidad, enlaces, orden, ramas, mutaciones, retornos e invariantes.

## Principio de causalidad visual

La visualización de un TAD no es una animación decorativa del resultado final: es una proyección
del estado alcanzado por el código C en el cursor actual. Por tanto:

- una asignación, enlace, intercambio, recoloreo, rotación, inserción o eliminación sólo aparece
  después de ejecutar la instrucción C que la causa;
- los estados anteriores permanecen visibles hasta que el C efectúe la mutación correspondiente;
- nodos auxiliares, punteros, arreglos temporales, colas, pilas y conjuntos de trabajo siguen su
  ciclo de vida real dentro de la función interpretada;
- el resaltado de línea, el cambio visual, la consola y el estado técnico pertenecen al mismo
  evento causal;
- si una instrucción no se ejecuta, ningún efecto exclusivo de ella puede aparecer en pantalla;
- avanzar, retroceder o reproducir reconstruye la misma proyección determinista del evento C.

La prueba principal compara el DOM normalizado de cada frame contra el `after_state` derivado del
evento C correspondiente, no solamente contra el estado final retornado por el backend.

## Inventario mínimo

| Familia | Elementos auditados |
|---|---|
| Secuenciales | pila, cola, cola de prioridad, lista enlazada, lista circular y sublista; todas sus mutaciones, consultas, búsquedas, inversiones y limpiezas |
| Jerárquicas | ABB, AVL, rojo-negro y montículo binario; inserción, eliminación cuando exista, búsqueda, recorridos, extremos, altura, validación y limpieza |
| Grafos | construcción, eliminación, consultas, BFS, DFS, Dijkstra, Bellman-Ford, Prim y Kruskal |
| Hash | creación, inserción/actualización, búsqueda, pertenencia, eliminación, enumeraciones, estadísticas, colisiones, rehash y limpieza |
| Ordenamiento | los once algoritmos, incluyendo comparaciones, movimientos, swaps, pivotes, particiones, recursión y arreglos auxiliares |

La matriz final se genera desde `get_supported_operations()` y los mapas C para detectar tanto
operaciones no auditadas como mapeos huérfanos.

## Diseño de casos

Cada operación tendrá, cuando aplique:

- caso nominal mínimo y caso nominal con estado previo;
- estructura vacía y estructura de un elemento;
- valores duplicados, negativos, cero y extremos admitidos;
- capacidad, factor de carga, colisión o rebalanceo en el umbral;
- entrada ausente, tipo inválido, identificador inexistente y operación no soportada;
- rutas alternativas de `if/else`, cero/una/múltiples iteraciones y retorno anticipado;
- recursión con caso base, un nivel y varios niveles;
- reserva, reasignación y liberación de memoria cuando el C las utilice.

Los escenarios generados conservarán semilla, entrada completa y caso reducido ante fallo.

## Eventos observables

Los harnesses de auditoría emitirán un protocolo versionado con:

- archivo, función y línea C;
- tipo de evento: condición, rama, iteración, llamada, retorno, asignación, reserva, liberación,
  enlace de puntero, comparación, intercambio o salida;
- identificadores lógicos estables para nodos/bloques, nunca direcciones crudas como contrato;
- estado canónico anterior y posterior;
- variables y estructuras temporales didácticamente relevantes;
- texto de consola y valor retornado.

La comparación admitirá únicamente abstracciones declaradas, por ejemplo omitir una dirección
física pero no el cambio de enlace que esa asignación produce.

## Oráculos e invariantes

- Pila: extracción inversa al orden de inserción y tope coherente.
- Cola: extracción en orden FIFO y frente/final coherentes.
- Cola de prioridad: orden definido por prioridad y regla estable de desempate del C.
- Listas: identidad y enlaces `next`, cabeza/cola, tamaño y cierre circular cuando corresponda.
- ABB: inorden ordenado y casos de eliminación hoja/un hijo/dos hijos.
- AVL: propiedad ABB, alturas, `|FE| <= 1` y rotaciones LL/RR/LR/RL.
- Rojo-negro: raíz negra, ausencia de rojo-rojo, black-height uniforme y fix-up correcto.
- Heap: forma casi completa, correspondencia arreglo/árbol y propiedad min-heap.
- Grafo: dirección, pesos, aristas incidentes, orden válido de recorridos, relajaciones, caminos y
  costo mínimo, detección de ciclo negativo y MST de costo mínimo.
- Hash: índice calculado por el C, cadenas de colisión, actualización, eliminación, carga y rehash.
- Ordenamiento: multiconjunto preservado, prefijos/rangos parciales correctos y salida ordenada.

## Reproducción UI

Para cada traza se probarán secuencias de controles: avanzar hasta el final, retroceder y volver a
avanzar, pausa/reproducción, reinicio a origen y ejecución rápida. En cada cursor se comparará el
DOM normalizado con `after_state`, la línea resaltada con el evento C y la consola acumulada con
las salidas alcanzadas. El estado final de todas las rutas de reproducción debe ser idéntico.

## Clasificación de hallazgos

- **Crítica:** corrupción, caída, error de memoria o enseñanza de un algoritmo/invariante
  fundamentalmente falso sin advertencia.
- **Alta:** rama inventada/omitida, estado visual falso, resultado incorrecto o divergencia final
  entre modo rápido y paso a paso.
- **Media:** estado temporal, puntero, consola, historial o resaltado incorrecto que no altera el
  resultado final pero degrada la explicación.
- **Baja:** texto, etiqueta, timing o detalle visual menor sin ambigüedad semántica.

## Artefactos de salida

- `docs/qa/didactic-c-trace-audit.md`: informe humano consolidado.
- `docs/qa/didactic-c-trace-results.json`: resultados estructurados y reproducibles.
- fixtures minimizados de cada fallo bajo `tests/qa/fixtures/`.
- pruebas propuestas o implementadas bajo `tests/qa/`, diferenciando claramente las que aún
  fallan por defecto conocido.

Cada registro contendrá operación, entrada, precondición, estados esperados y observados por capa,
resultado, discrepancia, severidad, causa probable, archivo/función, prueba recomendada y
corrección sugerida.

## Restricción de cambios

Durante esta propuesta se permite crear harnesses, pruebas de caracterización y documentos de QA.
No se cambia la lógica productiva para corregir hallazgos hasta recibir una solicitud explícita.
