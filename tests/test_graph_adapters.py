"""Unit tests for graph adapter operations and constraints."""

from __future__ import annotations

from app.adapters.graph_adapter import GraphAdapter


def test_create_directed_and_undirected_graph() -> None:
    """Adapter should recreate graph in both modes."""
    adapter = GraphAdapter()
    state = adapter.to_visual_state()
    assert state["directed"] is False

    adapter.execute("create_graph", {"directed": "true"})
    state = adapter.to_visual_state()
    assert state["directed"] is True


def test_insert_and_remove_vertex() -> None:
    """Vertex insertion and deletion should update metadata."""
    adapter = GraphAdapter()
    adapter.execute("insert_vertex", {"vertex": "1"})
    assert adapter.to_visual_state()["metadata"]["vertices_count"] == 1

    adapter.execute("remove_vertex", {"vertex": "1"})
    assert adapter.to_visual_state()["metadata"]["vertices_count"] == 0


def test_generate_random_graph_by_vertices_count() -> None:
    """Random graph generation should honor requested vertex count."""
    adapter = GraphAdapter()
    payload = {"vertices_count": "8"}
    result = adapter.execute("generate_random_graph", payload)
    state = adapter.to_visual_state()

    assert state["metadata"]["vertices_count"] == 8
    assert state["metadata"]["edges_count"] >= 7
    assert "seed" in payload
    assert result["result"]["vertices_count"] == 8


def test_insert_and_remove_edge() -> None:
    """Edge insertion and deletion should update metadata."""
    adapter = GraphAdapter()
    adapter.execute("insert_edge", {"origin": "1", "target": "2", "weight": "2"})
    assert adapter.to_visual_state()["metadata"]["edges_count"] == 1

    adapter.execute("remove_edge", {"origin": "1", "target": "2"})
    assert adapter.to_visual_state()["metadata"]["edges_count"] == 0


def test_queries_vertices_edges_neighbors_and_weight() -> None:
    """Query operations should return expected values."""
    adapter = GraphAdapter()
    adapter.execute("insert_edge", {"origin": "1", "target": "2", "weight": "3"})

    vertices = adapter.execute("list_vertices", {})["result"]
    edges = adapter.execute("list_edges", {})["result"]
    neighbors = adapter.execute("neighbors", {"vertex": "1"})["result"]
    weight = adapter.execute("edge_weight", {"origin": "1", "target": "2"})["result"]

    assert set(vertices) == {1, 2}
    assert len(edges) == 1
    assert neighbors == [2]
    assert weight == 3.0


def test_bfs_and_dfs_execution() -> None:
    """BFS and DFS should return traversal order from start vertex."""
    adapter = GraphAdapter()
    adapter.execute("insert_edge", {"origin": "1", "target": "2", "weight": "1"})
    adapter.execute("insert_edge", {"origin": "1", "target": "3", "weight": "1"})

    bfs = adapter.execute("run_bfs", {"start": "1"})["result"]
    dfs = adapter.execute("run_dfs", {"start": "1"})["result"]

    assert bfs[0] == 1
    assert dfs[0] == 1


def test_dijkstra_and_negative_weight_block() -> None:
    """Dijkstra should run on non-negative and fail on negative weights."""
    adapter = GraphAdapter()
    adapter.execute("insert_edge", {"origin": "1", "target": "2", "weight": "1"})
    result = adapter.execute("run_dijkstra", {"start": "1", "end": "2"})["result"]
    assert result["distances"][2] == 1.0
    assert result["path"] == [1, 2]
    assert result["distance_to_destination"] == 1.0

    adapter.execute("insert_edge", {"origin": "2", "target": "3", "weight": "-2"})
    try:
        adapter.execute("run_dijkstra", {"start": "1", "end": "3"})
        assert False, "Dijkstra debio bloquear pesos negativos"
    except Exception as error:  # noqa: BLE001
        assert "negativo" in str(error).lower()


def test_bellman_ford_execution() -> None:
    """Bellman-Ford should handle negative weights."""
    adapter = GraphAdapter()
    adapter.execute("create_graph", {"directed": "true"})
    adapter.execute("insert_edge", {"origin": "1", "target": "2", "weight": "4"})
    adapter.execute("insert_edge", {"origin": "2", "target": "3", "weight": "-1"})

    result = adapter.execute("run_bellman_ford", {"start": "1", "end": "3"})["result"]
    assert result["distances"][3] == 3.0
    assert result["has_negative_cycle"] is False
    assert result["path"] == [1, 2, 3]
    assert result["distance_to_destination"] == 3.0


def test_bellman_ford_undirected_uses_both_edge_directions() -> None:
    """In undirected graphs Bellman-Ford must relax both directions of each edge."""
    adapter = GraphAdapter()
    # Grafo no dirigido por defecto. Se agregan aristas en una orientacion
    # que no coincide con la ruta mas corta desde 1 hasta 4 si solo se relajara
    # la direccion cargada en `aristas()` deduplicada.
    adapter.execute("insert_edge", {"origin": "5", "target": "3", "weight": "1"})
    adapter.execute("insert_edge", {"origin": "1", "target": "3", "weight": "2"})
    adapter.execute("insert_edge", {"origin": "5", "target": "4", "weight": "5"})
    adapter.execute("insert_edge", {"origin": "1", "target": "2", "weight": "8"})
    adapter.execute("insert_edge", {"origin": "2", "target": "5", "weight": "13"})

    result = adapter.execute("run_bellman_ford", {"start": "1", "end": "4"})["result"]
    assert result["has_negative_cycle"] is False
    assert result["path"] == [1, 3, 5, 4]
    assert result["distance_to_destination"] == 8.0


def test_prim_and_kruskal_constraints_and_union_find_flag() -> None:
    """Prim/Kruskal must run only in undirected graphs and expose UF integration."""
    adapter = GraphAdapter()
    adapter.execute("insert_edge", {"origin": "1", "target": "2", "weight": "1"})
    adapter.execute("insert_edge", {"origin": "2", "target": "3", "weight": "2"})

    prim = adapter.execute("run_prim", {"start": "1"})["result"]
    kruskal = adapter.execute("run_kruskal", {})["result"]

    assert prim["total_weight"] >= 0
    assert kruskal["uses_union_find"] is True

    adapter.execute("create_graph", {"directed": "true"})
    adapter.execute("insert_edge", {"origin": "1", "target": "2", "weight": "1"})

    try:
        adapter.execute("run_prim", {"start": "1"})
        assert False, "Prim debio bloquearse para dirigido"
    except ValueError as error:
        assert "no dirigido" in str(error).lower()

    try:
        adapter.execute("run_kruskal", {})
        assert False, "Kruskal debio bloquearse para dirigido"
    except ValueError as error:
        assert "no dirigido" in str(error).lower()


def test_graph_rejects_non_integer_vertex() -> None:
    """Graph adapter should reject non-integer vertex input."""
    adapter = GraphAdapter()
    try:
        adapter.execute("insert_vertex", {"vertex": "A"})
        assert False, "Debe rechazar vertices no enteros"
    except ValueError as error:
        assert "entero" in str(error).lower()


def test_to_visual_state_contract() -> None:
    """Visual state should keep agreed serializable contract keys."""
    adapter = GraphAdapter()
    state = adapter.to_visual_state()

    assert state["structure"] == "graph"
    assert "nodes" in state
    assert "edges" in state
    assert "metadata" in state
    assert "last_operation" in state
