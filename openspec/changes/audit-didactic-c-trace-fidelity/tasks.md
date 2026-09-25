# Tareas

## 1. Inventario y trazabilidad

- [x] 1.1 Generar el inventario de estructuras, operaciones, mapas a función C, endpoints y modos de ejecución.
- [x] 1.2 Detectar operaciones sin función C, funciones C sin operación pública y fallbacks a pseudocódigo.
- [x] 1.3 Crear una matriz de cobertura que relacione operación, fuente C, adapter, estrategia de traza, renderer y pruebas existentes.
- [x] 1.4 Congelar el protocolo y formato versionado de resultados de auditoría.

## 2. Oráculo C instrumentado

- [ ] 2.1 Extender los harnesses de los 13 TAD para emitir eventos por instrucción relevante y estados canónicos intermedios.
  - [x] Definir el canal NDJSON opt-in `didactic-c-event/v1` sin alterar el estado canónico por `stdout`.
  - [x] Integrar eventos de ciclo de vida, argumentos y errores en los 13 harnesses.
  - [x] Añadir eventos de operación, condición, retorno, enlace y liberación a los seis TAD secuenciales.
  - [x] Añadir eventos observables de operación, llamadas, rebalanceo, sift, enlaces, rehash y liberación a árboles, heap, grafo, hash y ordenamiento.
  - [x] Emitir y validar snapshots canónicos ordenados después de cada operación en los 13 harnesses.
  - [ ] Añadir eventos semánticos y estados intermedios específicos de cada familia.
- [x] 2.2 Instrumentar condiciones, ramas, ciclos, llamadas recursivas, retornos y `switch` presentes en las fuentes.
  - [x] Instrumentar condiciones y límites observables en los wrappers de los 13 TAD.
  - [x] Observar dentro de las fuentes líneas, funciones, llamadas, condiciones y ramas mediante instrumentación `gcov` sin cambiar la lógica C.
- [ ] 2.3 Instrumentar identidad lógica, enlaces de punteros, reservas, reasignaciones y liberaciones sin exponer direcciones como contrato.
  - [x] Registrar semántica de enlaces y liberación sin direcciones físicas en las 13 ejecuciones representativas.
  - [x] Asignar identidades lógicas estables entre snapshots sin exponer direcciones físicas.
  - [ ] Registrar cada reserva/reasignación/liberación intermedia.
- [ ] 2.4 Capturar `printf`, valores de retorno, errores y estado final con un protocolo JSON reproducible.
  - [x] Capturar argumentos, errores y cierre exitoso con secuencia determinista.
  - [x] Capturar valores retornados concretos, salidas `printf` y estados canónicos por operación.
- [ ] 2.5 Compilar y ejecutar los harnesses con C17 estricto, ASan y UBSan.
  - [x] Compilar y ejecutar los 13 harnesses instrumentados con C17 y warnings como error.
  - [ ] Repetir la matriz instrumentada con ASan y UBSan en Linux.

## 3. Matriz de casos secuenciales

- [x] 3.1 Auditar pila: `apilar`, `desapilar`, consultas de cima/estado y `limpiar`.
- [x] 3.2 Auditar cola: `encolar`, `desencolar`, frente, final y `limpiar`.
- [x] 3.3 Auditar cola de prioridad, incluyendo prioridades iguales, extremos y orden de desempate.
- [x] 3.4 Auditar lista enlazada: inserciones, eliminaciones, búsquedas, inversión, cabeza, cola y enlaces.
- [x] 3.5 Auditar lista circular: inserciones, eliminación, búsquedas, inversión y cierre último→primero.
- [x] 3.6 Auditar sublista: padres, hijos, eliminaciones, consultas y enlaces jerárquicos.

## 4. Matriz de casos jerárquicos

- [x] 4.1 Auditar ABB: inserción, búsqueda, recorridos, extremos y eliminación hoja/un hijo/dos hijos.
- [x] 4.2 Auditar AVL: inserción/eliminación y rotaciones LL, RR, LR y RL con alturas y factores intermedios.
- [x] 4.3 Auditar rojo-negro: inserción, recoloreos, rotaciones, casos de fix-up, colores y black-height.
- [x] 4.4 Auditar montículo binario: inserción, consulta/extracción de raíz, sift-up, sift-down y arreglo/árbol.

## 5. Matriz de grafos y hash

- [x] 5.1 Auditar construcción y consultas de grafos dirigidos/no dirigidos, ponderados, vacíos y desconectados.
- [x] 5.2 Auditar BFS y DFS, incluyendo cola, recursión, visitados y orden de adyacencia.
- [x] 5.3 Auditar Dijkstra y Bellman-Ford, incluyendo relajaciones, inalcanzables, pesos inválidos y ciclos negativos.
- [x] 5.4 Auditar Prim y Kruskal, incluyendo candidatos, union-find, grafos desconectados y costo del MST.
- [x] 5.5 Auditar hash: función de índice, colisiones, actualización, búsqueda, eliminación, estadísticas y rehash.

## 6. Matriz de ordenamiento

- [x] 6.1 Auditar intercambio, selección, inserción y burbuja con comparaciones y swaps exactos.
- [x] 6.2 Auditar Shell y heapsort con brechas, heapificación y estados parciales.
- [x] 6.3 Auditar quicksort y mergesort con pivote, particiones, recursión y arreglos auxiliares.
- [x] 6.4 Auditar counting sort, binsort y radixsort con conteos/bins/dígitos, duplicados y rangos admitidos.
- [x] 6.5 Confirmar para los once algoritmos preservación del multiconjunto, orden final y equivalencia rápido/paso a paso.

## 7. Fidelidad de traza y frontend

- [x] 7.1 Comparar por evento código C, backend, before/after de traza, historial técnico y consola.
- [x] 7.2 Verificar que sólo aparezcan ramas e iteraciones ejecutadas y que recursión/retornos mantengan su pila lógica.
- [x] 7.3 Verificar temporales, nodos auxiliares, punteros, comparaciones, intercambios y rangos activos.
- [x] 7.4 Verificar correspondencia entre línea C resaltada, mutación visual y `printf` acumulado.
- [x] 7.5 Probar avanzar, retroceder, reproducir, pausar, reiniciar y repetir sin deriva de estado.
- [x] 7.6 Comparar el estado final del modo rápido con cada ruta de reproducción paso a paso.
- [x] 7.7 Verificar frame por frame que cada cambio visual ocurra únicamente al ejecutarse la instrucción C que lo causa.
- [x] 7.8 Detectar efectos visuales anticipados, retrasados, omitidos o inventados aunque el estado final sea correcto.
- [x] 7.9 Verificar por TAD que identidad, enlaces, posiciones, colores y estructuras temporales sigan el ciclo de vida real del C.

## 8. Casos generados y regresión

- [x] 8.1 Ejecutar casos normales, límites e inválidos deterministas para cada operación.
- [x] 8.2 Ejecutar al menos 1.000 secuencias generadas por familia con semillas registradas.
- [x] 8.3 Reducir automáticamente cada divergencia al caso mínimo reproducible.
- [x] 8.4 Proponer una prueba automatizada específica para cada hallazgo y ejecutar las pruebas de caracterización seguras.
- [x] 8.5 Confirmar que la auditoría no introduce cambios en la lógica productiva.

## 9. Informe y cierre

- [x] 9.1 Generar el informe estructurado con una fila por operación/caso y evidencia esperada/observada.
- [x] 9.2 Clasificar cada discrepancia como crítica, alta, media o baja y documentar causa probable y localización.
- [x] 9.3 Documentar la prueba recomendada y la corrección sugerida sin aplicar la corrección.
- [x] 9.4 Priorizar divergencias semánticas, estados falsos, ramas incorrectas y diferencias rápido/paso a paso.
- [x] 9.5 Revisar que no haya operaciones sin resultado ni hallazgos sin evidencia reproducible.
- [x] 9.6 Validar OpenSpec, publicar los artefactos QA y presentar el backlog de correcciones para autorización.
