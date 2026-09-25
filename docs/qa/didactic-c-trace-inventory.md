# Inventario QA de fidelidad didáctica C

Esquema: `didactic-qa-inventory/v1`.
Cobertura descubierta: **13 estructuras** y **120 operaciones/algoritmos**.

| Familia | TAD | Operación/algoritmo | Mutación | Función C | Fuente didáctica | Estrategia | Renderer | Tests existentes |
|---|---|---|---:|---|---|---|---|---:|
| sequential | `stack` | `apilar` | sí | `pila_apilar` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 19 |
| sequential | `stack` | `desapilar` | sí | `pila_desapilar` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 9 |
| sequential | `stack` | `limpiar` | sí | `SIN_MAPEO` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 7 |
| sequential | `queue` | `encolar` | sí | `cola_encolar` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 15 |
| sequential | `queue` | `desencolar` | sí | `cola_desencolar` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 10 |
| sequential | `queue` | `limpiar` | sí | `SIN_MAPEO` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 6 |
| sequential | `priority_queue` | `encolar` | sí | `cp_encolar` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 11 |
| sequential | `priority_queue` | `desencolar` | sí | `cp_desencolar` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 7 |
| sequential | `priority_queue` | `frente` | no | `cp_frente` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 6 |
| sequential | `priority_queue` | `limpiar` | sí | `SIN_MAPEO` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 5 |
| sequential | `linked_list` | `insertar_inicio` | sí | `lista_insertar_inicio` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 7 |
| sequential | `linked_list` | `insertar_final` | sí | `lista_insertar_final` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 7 |
| sequential | `linked_list` | `lista_insertar_elemento` | sí | `lista_insertar_elemento` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 4 |
| sequential | `linked_list` | `eliminar_elemento` | sí | `lista_eliminar_elemento` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 1 |
| sequential | `linked_list` | `eliminar_repetidos` | sí | `lista_eliminar_repetidos` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 2 |
| sequential | `linked_list` | `buscar_elemento` | no | `lista_buscar_elemento` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 1 |
| sequential | `linked_list` | `mostrar` | no | `lista_mostrar` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 0 |
| sequential | `linked_list` | `limpiar` | sí | `SIN_MAPEO` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 4 |
| sequential | `linked_list` | `insertar_posicion` | sí | `lista_insertar_elemento` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 2 |
| sequential | `linked_list` | `insertar_elemento` | sí | `lista_insertar_elemento` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 5 |
| sequential | `linked_list` | `eliminar_primero` | sí | `lista_eliminar_inicio` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 4 |
| sequential | `linked_list` | `buscar_posiciones` | no | `lista_buscar_elemento` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 5 |
| sequential | `linked_list` | `eliminar_inicio` | sí | `lista_eliminar_inicio` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 1 |
| sequential | `linked_list` | `eliminar_final` | sí | `lista_eliminar_final` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 1 |
| sequential | `linked_list` | `eliminar_posicion` | sí | `lista_eliminar_posicion` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 4 |
| sequential | `linked_list` | `invertir` | sí | `lista_invertir` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 6 |
| sequential | `linked_list` | `primero` | no | `lista_primero` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 6 |
| sequential | `linked_list` | `ultimo` | no | `lista_ultimo` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 2 |
| sequential | `circular_list` | `insertar_inicio` | sí | `lcir_insertar_inicio` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 6 |
| sequential | `circular_list` | `insertar_final` | sí | `lcir_insertar_final` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 6 |
| sequential | `circular_list` | `eliminar_inicio` | sí | `SIN_MAPEO` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 1 |
| sequential | `circular_list` | `eliminar_primero` | sí | `lcir_eliminar_primero` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 4 |
| sequential | `circular_list` | `buscar_posiciones` | no | `lcir_buscar_posiciones` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 5 |
| sequential | `circular_list` | `invertir` | sí | `lcir_invertir` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 4 |
| sequential | `circular_list` | `limpiar` | sí | `SIN_MAPEO` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 3 |
| sequential | `sublist` | `insertar_padre` | sí | `sublista_insertar_padre_final` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 14 |
| sequential | `sublist` | `insertar_hijo` | sí | `sublista_insertar_hijo_final` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 10 |
| sequential | `sublist` | `eliminar_padre` | sí | `sublista_eliminar_padre_primero` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 7 |
| sequential | `sublist` | `eliminar_hijo` | sí | `sublista_eliminar_hijo_primero` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 8 |
| sequential | `sublist` | `hijos_de` | no | `SIN_MAPEO` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 7 |
| sequential | `sublist` | `limpiar` | sí | `SIN_MAPEO` | `c` | `SequentialTraceStrategy` | `renderVisualState` | 7 |
| hierarchical | `abb` | `insertar` | sí | `abb_insertar` | `c` | `TreeTraceStrategy` | `renderHierState` | 18 |
| hierarchical | `abb` | `eliminar` | sí | `abb_eliminar` | `c` | `TreeTraceStrategy` | `renderHierState` | 9 |
| hierarchical | `abb` | `buscar` | no | `abb_buscar` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `abb` | `minimo` | no | `abb_encontrarMinimo` | `c` | `TreeTraceStrategy` | `renderHierState` | 5 |
| hierarchical | `abb` | `maximo` | no | `abb_encontrarMaximo` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `abb` | `altura` | no | `abb_altura` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `abb` | `contar_hojas` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 3 |
| hierarchical | `abb` | `inorden` | no | `abb_inorden` | `c` | `TreeTraceStrategy` | `renderHierState` | 5 |
| hierarchical | `abb` | `preorden` | no | `abb_preorden` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `abb` | `postorden` | no | `abb_postorden` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `abb` | `validar` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 5 |
| hierarchical | `abb` | `limpiar` | sí | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 7 |
| hierarchical | `avl` | `insertar` | sí | `avl_insertar` | `c` | `TreeTraceStrategy` | `renderHierState` | 16 |
| hierarchical | `avl` | `eliminar` | sí | `avl_eliminar` | `c` | `TreeTraceStrategy` | `renderHierState` | 9 |
| hierarchical | `avl` | `buscar` | no | `avl_buscar` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `avl` | `minimo` | no | `avl_minimo` | `c` | `TreeTraceStrategy` | `renderHierState` | 5 |
| hierarchical | `avl` | `maximo` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `avl` | `altura` | no | `avl_altura` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `avl` | `inorden` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 6 |
| hierarchical | `avl` | `validar` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 5 |
| hierarchical | `avl` | `limpiar` | sí | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 7 |
| hierarchical | `red_black` | `insertar` | sí | `rbt_insertar` | `c` | `TreeTraceStrategy` | `renderHierState` | 17 |
| hierarchical | `red_black` | `eliminar` | sí | `rbt_eliminar` | `c` | `TreeTraceStrategy` | `renderHierState` | 9 |
| hierarchical | `red_black` | `buscar` | no | `rbt_buscar` | `c` | `TreeTraceStrategy` | `renderHierState` | 3 |
| hierarchical | `red_black` | `inorden` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 5 |
| hierarchical | `red_black` | `altura` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 3 |
| hierarchical | `red_black` | `validar` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `red_black` | `limpiar` | sí | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 6 |
| hierarchical | `binary_heap` | `insertar` | sí | `monticulo_insertar` | `c` | `TreeTraceStrategy` | `renderHierState` | 9 |
| hierarchical | `binary_heap` | `extraer_raiz` | sí | `monticulo_extraer_raiz` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `binary_heap` | `raiz` | no | `monticulo_raiz` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| hierarchical | `binary_heap` | `a_lista` | no | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 1 |
| hierarchical | `binary_heap` | `limpiar` | sí | `SIN_MAPEO` | `c` | `TreeTraceStrategy` | `renderHierState` | 4 |
| graph | `graph` | `create_graph` | sí | `SIN_MAPEO` | `c` | `GraphTraceStrategy` | `renderGraphState` | 12 |
| graph | `graph` | `generate_random_graph` | sí | `SIN_MAPEO` | `fallback_or_derived` | `GraphTraceStrategy` | `renderGraphState` | 5 |
| graph | `graph` | `insert_vertex` | sí | `grafo_insertar_vertice` | `c` | `GraphTraceStrategy` | `renderGraphState` | 12 |
| graph | `graph` | `remove_vertex` | sí | `grafo_eliminar_vertice` | `c` | `GraphTraceStrategy` | `renderGraphState` | 3 |
| graph | `graph` | `insert_edge` | sí | `grafo_insertar_arco` | `c` | `GraphTraceStrategy` | `renderGraphState` | 13 |
| graph | `graph` | `remove_edge` | sí | `grafo_eliminar_arco` | `c` | `GraphTraceStrategy` | `renderGraphState` | 3 |
| graph | `graph` | `exists_vertex` | no | `grafo_existe_vertice` | `c` | `GraphTraceStrategy` | `renderGraphState` | 1 |
| graph | `graph` | `exists_edge` | no | `grafo_existe_arco` | `c` | `GraphTraceStrategy` | `renderGraphState` | 1 |
| graph | `graph` | `list_vertices` | no | `grafo_vertices` | `c` | `GraphTraceStrategy` | `renderGraphState` | 2 |
| graph | `graph` | `list_edges` | no | `grafo_arcos` | `c` | `GraphTraceStrategy` | `renderGraphState` | 2 |
| graph | `graph` | `neighbors` | no | `grafo_sucesores` | `c` | `GraphTraceStrategy` | `renderGraphState` | 3 |
| graph | `graph` | `edge_weight` | no | `grafo_costo_arco` | `c` | `GraphTraceStrategy` | `renderGraphState` | 3 |
| graph | `graph` | `run_bfs` | no | `grafo_bfs` | `c` | `GraphTraceStrategy` | `renderGraphState` | 9 |
| graph | `graph` | `run_dfs` | no | `grafo_dfs` | `c` | `GraphTraceStrategy` | `renderGraphState` | 7 |
| graph | `graph` | `run_dijkstra` | no | `grafo_dijkstra` | `c` | `GraphTraceStrategy` | `renderGraphState` | 9 |
| graph | `graph` | `run_bellman_ford` | no | `grafo_bellman_ford` | `c` | `GraphTraceStrategy` | `renderGraphState` | 6 |
| graph | `graph` | `run_prim` | no | `grafo_prim` | `c` | `GraphTraceStrategy` | `renderGraphState` | 6 |
| graph | `graph` | `run_kruskal` | no | `grafo_kruskal` | `c` | `GraphTraceStrategy` | `renderGraphState` | 5 |
| graph | `graph` | `clear_graph` | sí | `SIN_MAPEO` | `c` | `GraphTraceStrategy` | `renderGraphState` | 0 |
| hash | `hash_table` | `create_table` | sí | `th_inicializar` | `c` | `HashTraceStrategy` | `renderHashState` | 7 |
| hash | `hash_table` | `insert` | sí | `th_insertar` | `c` | `HashTraceStrategy` | `renderHashState` | 16 |
| hash | `hash_table` | `get` | no | `th_buscar` | `c` | `HashTraceStrategy` | `renderHashState` | 16 |
| hash | `hash_table` | `contains` | no | `th_contiene` | `c` | `HashTraceStrategy` | `renderHashState` | 6 |
| hash | `hash_table` | `remove` | sí | `th_eliminar` | `c` | `HashTraceStrategy` | `renderHashState` | 6 |
| hash | `hash_table` | `keys` | no | `SIN_MAPEO` | `c` | `HashTraceStrategy` | `renderHashState` | 5 |
| hash | `hash_table` | `values` | no | `SIN_MAPEO` | `c` | `HashTraceStrategy` | `renderHashState` | 8 |
| hash | `hash_table` | `items` | no | `SIN_MAPEO` | `c` | `HashTraceStrategy` | `renderHashState` | 9 |
| hash | `hash_table` | `stats` | no | `SIN_MAPEO` | `c` | `HashTraceStrategy` | `renderHashState` | 3 |
| hash | `hash_table` | `clear` | sí | `th_vaciar` | `c` | `HashTraceStrategy` | `renderHashState` | 3 |
| sorting | `sorting_array` | `create_array` | sí | `SIN_MAPEO` | `fallback_or_derived` | `SortingTraceStrategy` | `renderSortingVisualState` | 4 |
| sorting | `sorting_array` | `generate_random_array` | sí | `SIN_MAPEO` | `fallback_or_derived` | `SortingTraceStrategy` | `renderSortingVisualState` | 0 |
| sorting | `sorting_array` | `select_algorithm` | sí | `SIN_MAPEO` | `fallback_or_derived` | `SortingTraceStrategy` | `renderSortingVisualState` | 4 |
| sorting | `sorting_array` | `run` | sí | `SIN_MAPEO` | `fallback_or_derived` | `SortingTraceStrategy` | `renderSortingVisualState` | 5 |
| sorting | `sorting_array` | `step` | no | `SIN_MAPEO` | `fallback_or_derived` | `SortingTraceStrategy` | `renderSortingVisualState` | 6 |
| sorting | `sorting_array` | `reset` | sí | `SIN_MAPEO` | `fallback_or_derived` | `SortingTraceStrategy` | `renderSortingVisualState` | 4 |
| sorting | `sorting_array` | `intercambio` | sí | `ordenar_intercambio` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 1 |
| sorting | `sorting_array` | `seleccion` | sí | `ordenar_seleccion` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 1 |
| sorting | `sorting_array` | `insercion` | sí | `ordenar_insercion` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 5 |
| sorting | `sorting_array` | `burbuja` | sí | `ordenar_burbuja` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 5 |
| sorting | `sorting_array` | `shell` | sí | `ordenar_shell` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 2 |
| sorting | `sorting_array` | `quicksort` | sí | `ordenar_quicksort` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 7 |
| sorting | `sorting_array` | `mergesort` | sí | `ordenar_mergesort` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 4 |
| sorting | `sorting_array` | `heapsort` | sí | `ordenar_heapsort` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 1 |
| sorting | `sorting_array` | `counting_sort` | sí | `ordenar_counting_sort` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 3 |
| sorting | `sorting_array` | `binsort` | sí | `ordenar_binsort` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 4 |
| sorting | `sorting_array` | `radixsort` | sí | `ordenar_radixsort` | `c` | `SortingTraceStrategy` | `renderSortingVisualState` | 5 |

## Huecos detectados

Operaciones públicas sin mapeo C: `stack::limpiar`, `queue::limpiar`, `priority_queue::limpiar`, `linked_list::limpiar`, `circular_list::eliminar_inicio`, `circular_list::limpiar`, `sublist::hijos_de`, `sublist::limpiar`, `abb::contar_hojas`, `abb::validar`, `abb::limpiar`, `avl::maximo`, `avl::inorden`, `avl::validar`, `avl::limpiar`, `red_black::inorden`, `red_black::altura`, `red_black::validar`, `red_black::limpiar`, `binary_heap::a_lista`, `binary_heap::limpiar`, `graph::create_graph`, `graph::generate_random_graph`, `graph::clear_graph`, `hash_table::keys`, `hash_table::values`, `hash_table::items`, `hash_table::stats`, `sorting_array::create_array`, `sorting_array::generate_random_array`, `sorting_array::select_algorithm`, `sorting_array::run`, `sorting_array::step`, `sorting_array::reset`

Los mapeos C huérfanos se conservan en el JSON para revisión y clasificación explícita.
