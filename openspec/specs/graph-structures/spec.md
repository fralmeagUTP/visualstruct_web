# graph-structures Specification

## Purpose

Módulo del TAD Grafo (`graph`): construcción de grafos dirigidos/no dirigidos con
pesos, recorridos (BFS/DFS), caminos mínimos (Dijkstra/Bellman-Ford) y árboles de
expansión mínima (Prim/Kruskal), organizado en 4 fases didácticas.

## Requirements

### Requirement: Fases del módulo de grafos
El sistema DEBE organizar el módulo en 4 fases accesibles vía
`GET /graph/<structure_id>/<phase>`: `construccion`, `recorridos`, `camino-minimo`
y `expansion-minima`. Cada fase DEBE restringir los algoritmos disponibles:
`recorridos` → BFS/DFS; `camino-minimo` → Dijkstra/Bellman-Ford; `expansion-minima`
→ Prim/Kruskal; `construccion` → modo operación sin algoritmo por defecto.

#### Scenario: fase de recorridos con algoritmo por defecto
- **WHEN** un cliente hace `GET /graph/graph/recorridos`
- **THEN** la página se renderiza con `run_bfs` como algoritmo por defecto y solo
  BFS/DFS disponibles

#### Scenario: fase desconocida
- **WHEN** un cliente hace `GET /graph/graph/fase_inventada`
- **THEN** responde `404`

### Requirement: Operaciones de construcción
El sistema DEBE soportar `create_graph` (con tipo dirigido/no dirigido),
`generate_random_graph`, `insert_vertex`, `remove_vertex`, `insert_edge`,
`remove_edge` y las consultas `exists_vertex`, `exists_edge`, `neighbors`,
`edge_weight`, `list_vertices` y `list_edges` a través de
`POST /graph/<structure_id>/operate` con el contrato JSON común.

#### Scenario: insertar arista en grafo no dirigido
- **GIVEN** un grafo no dirigido con vértices `1` y `2`
- **WHEN** se ejecuta `insert_edge` con `{"origin": 1, "target": 2, "weight": 5}`
- **THEN** la arista existe en ambos sentidos con peso `5`

#### Scenario: eliminar vértice elimina aristas incidentes
- **GIVEN** un grafo con la arista `(1,2)`
- **WHEN** se ejecuta `remove_vertex` con `{"vertex": 1}`
- **THEN** el vértice `1` y la arista `(1,2)` desaparecen del estado visual

#### Scenario: generación aleatoria conectada
- **WHEN** se ejecuta `generate_random_graph` con 6 vértices
- **THEN** el grafo resultante contiene 6 vértices con conectividad base y pesos positivos

### Requirement: Validación de entradas de grafo
Los campos `vertex`, `origin`, `target`, `start` y `end` DEBEN validarse como
enteros y `weight` DEBE aceptar valores numéricos (entero o decimal).

#### Scenario: peso decimal aceptado
- **WHEN** se inserta una arista con `{"origin": 1, "target": 2, "weight": 2.5}`
- **THEN** responde `200` y el peso almacenado es `2.5`

#### Scenario: vértice no entero rechazado
- **WHEN** se ejecuta `insert_vertex` con `{"vertex": "a"}`
- **THEN** responde `400` con el mensaje de entero inválido

### Requirement: Estado visual del grafo
El adapter de grafo DEBE exponer un estado visual con `nodes`, `edges` (con
`weight`), flags `directed` y `weighted`, `metadata` (conteos de vértices/aristas y
vacío) y `last_operation`/`last_result` para la simulación.

#### Scenario: metadata coherente
- **GIVEN** un grafo con 3 vértices y 2 aristas
- **WHEN** se solicita el estado visual
- **THEN** `metadata.vertices_count=3`, `metadata.edges_count=2` e `is_empty=false`

### Requirement: Algoritmos de recorrido
El sistema DEBE ejecutar `run_bfs` (anchura por capas con cola) y `run_dfs`
(profundidad con subrutina recursiva) desde un vértice inicial entero, devolviendo
el orden de visita en `result` y una traza que resalte nodos/aristas visitados.

#### Scenario: BFS visita por capas
- **GIVEN** un grafo con aristas `(1,2)`, `(1,3)`, `(2,4)`
- **WHEN** se ejecuta `run_bfs` desde `1`
- **THEN** el resultado es `[1, 2, 3, 4]`

#### Scenario: DFS explora en profundidad
- **GIVEN** el mismo grafo
- **WHEN** se ejecuta `run_dfs` desde `1`
- **THEN** el resultado es un orden de visita en profundidad válido (`1,2,4,3` o
  `1,3,2,4` según orden de adyacencia)

### Requirement: Algoritmos de camino mínimo
El sistema DEBE ejecutar `run_dijkstra` (pesos no negativos) y `run_bellman_ford`
(con detección de ciclos negativos) entre vértices `start`/`end`, devolviendo el
camino y su costo, y resaltando el camino resultante en la traza.

#### Scenario: Dijkstra encuentra el camino mínimo
- **GIVEN** un grafo con `(1,2,w=4)`, `(1,3,w=1)`, `(3,2,w=1)`
- **WHEN** se ejecuta `run_dijkstra` de `1` a `2`
- **THEN** el camino retornado es `[1, 3, 2]` con costo `2`

#### Scenario: Bellman-Ford detecta ciclo negativo
- **GIVEN** un grafo dirigido con un ciclo de peso total negativo alcanzable
- **WHEN** se ejecuta `run_bellman_ford`
- **THEN** responde con error indicando la presencia del ciclo negativo

### Requirement: Árbol de expansión mínima
El sistema DEBE ejecutar `run_prim` y `run_kruskal` sobre grafos no dirigidos,
devolviendo el conjunto de aristas del MST y resaltándolo en la traza.

#### Scenario: Prim y Kruskal coinciden en costo
- **GIVEN** un grafo no dirigido conexo con pesos
- **WHEN** se ejecutan `run_prim` y `run_kruskal`
- **THEN** ambos retornan un árbol de expansión con el mismo costo total mínimo

### Requirement: Reinicio del grafo
El sistema DEBE soportar `POST /graph/<structure_id>/reset` (limpieza de historial
de sesión) y la operación `clear_graph` (grafo vacío conservando configuración),
con el contrato JSON común.

#### Scenario: reset deja el grafo vacío
- **GIVEN** un grafo con vértices y aristas
- **WHEN** se hace `POST /graph/graph/reset`
- **THEN** el estado visual queda sin nodos ni aristas e `history` es `[]`
