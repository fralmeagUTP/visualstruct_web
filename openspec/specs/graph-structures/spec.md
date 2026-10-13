# graph-structures Specification

## Purpose

Módulo del TAD Grafo (`graph`): construcción de grafos dirigidos/no dirigidos con
pesos, recorridos (BFS/DFS), caminos mínimos (Dijkstra/Bellman-Ford) y árboles de
expansión mínima (Prim/Kruskal), organizado en 4 fases didácticas.
## Requirements
### Requirement: Fases del módulo de grafos
El sistema MUST organizar el módulo en 4 fases accesibles vía
`GET /graph/<structure_id>/<phase>`: `construccion`, `recorridos`, `camino-minimo`
y `expansion-minima`. Cada fase MUST restringir los algoritmos disponibles:
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
El sistema MUST soportar `create_graph` (con tipo dirigido/no dirigido),
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
Los campos `vertex`, `origin`, `target`, `start` y `end` MUST validarse como enteros. Conforme a graph-approved-integer-dijkstra-contract-decision-low.md y su implementación aceptada, `weight` MUST ser finito, integral y representable en C int de32bits;2.0 se normaliza exactamente a2 y2.5 se rechaza sin truncamiento. Construcción MAY conservar pesos negativos para algoritmos que los admiten; Dijkstra MUST rechazar todo arco negativo, incluso desconectado, según sus reglas C aprobadas.

#### Scenario: peso decimal aceptado
- **GIVEN** un peso decimal integral2.0 dentro del dominio C int
- **WHEN** se inserta una arista
- **THEN** responde200 y almacena el peso entero2; el caso histórico de2.5aceptado queda sustituido por la decisión explícita de pesos enteros

#### Scenario: vértice no entero rechazado
- **WHEN** se ejecuta `insert_vertex` con `{"vertex": "a"}`
- **THEN** responde400 con el mensaje de entero inválido

#### Scenario: peso fraccionario no truncado
- **WHEN** se inserta una arista con peso2.5
- **THEN** responde400 sin aceptar un peso truncado ni alterar el estado/historial aceptados

#### Scenario: peso no finito o fuera de C int
- **WHEN** el peso es no finito o excede[-2147483648,2147483647]
- **THEN** se rechaza antes de invocar C o persistir una operación exitosa

### Requirement: Estado visual del grafo
El adapter de grafo MUST exponer un estado visual con `nodes`, `edges` (con
`weight`), flags `directed` y `weighted`, `metadata` (conteos de vértices/aristas y
vacío) y `last_operation`/`last_result` para la simulación.

#### Scenario: metadata coherente
- **GIVEN** un grafo con 3 vértices y 2 aristas
- **WHEN** se solicita el estado visual
- **THEN** `metadata.vertices_count=3`, `metadata.edges_count=2` e `is_empty=false`

### Requirement: Algoritmos de recorrido
El sistema MUST ejecutar `run_bfs` (anchura por capas con cola) y `run_dfs`
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
El sistema MUST ejecutar `run_dijkstra` (pesos no negativos) y `run_bellman_ford`
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
El sistema MUST ejecutar `run_prim` y `run_kruskal` sobre grafos no dirigidos,
devolviendo el conjunto de aristas del MST y resaltándolo en la traza.

#### Scenario: Prim y Kruskal coinciden en costo
- **GIVEN** un grafo no dirigido conexo con pesos
- **WHEN** se ejecutan `run_prim` y `run_kruskal`
- **THEN** ambos retornan un árbol de expansión con el mismo costo total mínimo

### Requirement: Reinicio del grafo
El sistema MUST soportar `POST /graph/<structure_id>/reset` (limpieza de historial
de sesión) y la operación `clear_graph` (grafo vacío conservando configuración),
con el contrato JSON común.

#### Scenario: reset deja el grafo vacío
- **GIVEN** un grafo con vértices y aristas
- **WHEN** se hace `POST /graph/graph/reset`
- **THEN** el estado visual queda sin nodos ni aristas e `history` es `[]`

### Requirement: Educational graph capacity of fifteen vertices
The application SHALL admit at most15distinct vertices for new operations,
including implicit endpoints and random generation, while preserving downloaded
C/H algorithms/signatures, faithful traces and coverage83/85. The capacity
counts distinct vertices and SHALL NOT constrain labels to the range1..15.

#### Scenario: Reject the sixteenth vertex transactionally
- GIVEN an existing graph with15vertices
- WHEN insertion or implicit endpoints would create vertex16, or generation requests16
- THEN HTTP400 SHALL preserve all graph state, previous result, history and RNG seed
- AND the trace SHALL explicitly mark application rejection with zero C executions
- AND the UI SHALL state the limit without silent truncation

#### Scenario: Preserve a previous larger session
- GIVEN a legitimate persisted history which reconstructs more than15vertices
- WHEN the user reloads, views, queries or downloads its caller
- THEN all existing data/history SHALL remain intact
- AND new insertion and algorithm execution SHALL be blocked while over15
- AND explicit removals, clear, type reset or generation<=15 MAY reduce the graph
- AND normal operations SHALL resume once the graph returns to15

#### Scenario: Verify only eight-node algorithm fixtures
- GIVEN graph-max15-only8-current-user-decision-low.md supersedes the prior30 maximum
- WHEN performing current algorithm functional and visual checks
- THEN only8-node algorithm fixtures SHALL execute, with15-admission/16-rejection checked through validation without full15/16 algorithm traces
- AND allowed15 SHALL NOT imply tested15 or a universal time/usability guarantee
- AND previous30/BF20 benchmarks SHALL remain historical unchanged
- AND visual preparation delay and any pending performance/fidelity criteria SHALL be disclosed without new optimization or invented PASS
