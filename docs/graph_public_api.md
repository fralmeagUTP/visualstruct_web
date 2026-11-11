# Uso educativo del TAD grafo

Las funciones públicas reciben solo el grafo y los datos de la operación. No hay que declarar ni pasar `GrafoEstado`.

```c
Grafo g = grafo_crear();
g = grafo_insertar_vertice(g, 1);
g = grafo_insertar_vertice(g, 2);
g = grafo_insertar_arco(g, 1, 2, 7);
ListaVertice recorrido = grafo_bfs(g, 1);
grafo_liberar_vertices(&recorrido);
ListaArco camino = grafo_dijkstra(g, 1, 2);
grafo_liberar_arcos(&camino);
grafo_destruir(&g);
```

## Firmas

- Inserción: `grafo_insertar_vertice(g, dato)`, `grafo_insertar_arco(g, origen, destino, peso)`.
- Vecinos: `grafo_sucesores(g, vertice)`, `grafo_predecesores(g, vertice)`.
- Recorridos: `grafo_bfs(g, inicio)`, `grafo_dfs(g, inicio)`.
- Caminos: `grafo_dijkstra(g, inicio, llegada)`, `grafo_bellman_ford(g, inicio, llegada)`.
- Expansión mínima: `grafo_prim(g, inicio)`, `grafo_kruskal(g)`.

Las demás funciones conservan sus entradas propias. `grafo_costo_arco` sigue devolviendo 0/1 y entrega el peso por `int *salida`: ese parámetro es el resultado solicitado, no un estado auxiliar.

## Resultados y memoria

Las inserciones devuelven el grafo actualizado. Si falla una reserva, conservan el grafo previo. Las listas de vecinos, recorridos, caminos y árboles son propias y deben liberarse. Las listas de `grafo_vertices` y `grafo_arcos` son prestadas y no se liberan por separado.

Una lista nula puede significar ausencia de resultado, error o un resultado válido sin arcos (por ejemplo, un camino de un vértice a sí mismo). El programa educativo no debe inferir una causa solo a partir de NULL. En VisualStruct, el diagnóstico detallado se obtiene de la ejecución real y se muestra por separado: no exige una variable ni un argumento adicional al estudiante.

El código C mantiene las comprobaciones internas de memoria, conectividad, pesos y desbordamiento. El intérprete observa el diagnóstico local antes de finalizar la función; no usa un parámetro público oculto ni sustituye la ejecución por un algoritmo Python.

## Compatibilidad

Los programas antiguos deben retirar el argumento `&estado` de las diez funciones simplificadas y las impresiones de dicho estado. No se conserva la firma antigua mediante macros o argumentos opcionales. El historial de operaciones de la aplicación sigue siendo válido porque conserva entradas de dominio, no argumentos de salida C.

En Prim y Kruskal, los arcos seleccionados se muestran en amarillo; los demás permanecen azules. La leyenda identifica explícitamente el árbol de expansión mínima.

## Práctica para estudiantes

La [guía de grafos](GUIA_ESTUDIANTES_GRAFOS.md) desarrolla un ejemplo completo compilable y explica capacidad, visualización y memoria.
