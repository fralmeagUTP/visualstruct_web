"""Integration tests for graph routes."""

from __future__ import annotations


def test_graph_module_page_loads(client) -> None:
    """Graph module index should be reachable."""
    response = client.get("/graph/")
    assert response.status_code == 200
    assert "Módulo de Grafos".encode("utf-8") in response.data


def test_graph_structure_page_loads(client) -> None:
    """Graph structure page should load."""
    response = client.get("/graph/graph")
    assert response.status_code == 200
    assert b"Estado visual" in response.data
    assert "Codigo C:".encode("utf-8") in response.data
    assert "grafo_insertar_vertice".encode("utf-8") in response.data


def test_graph_phase_pages_load(client) -> None:
    """Each graph learning phase should render in its own route."""
    for phase in ("construccion", "recorridos", "camino-minimo", "expansion-minima"):
        response = client.get(f"/graph/graph/{phase}")
        assert response.status_code == 200
        assert b"Estado visual" in response.data


def test_graph_phase_didactic_notes_are_specific(client) -> None:
    """Didactic note should change per graph phase."""
    expected = {
        "construccion": "Construccion del grafo",
        "recorridos": "Recorridos: exploran el grafo",
        "camino-minimo": "Camino minimo",
        "expansion-minima": "Arbol de expansion minima",
    }
    for phase, fragment in expected.items():
        response = client.get(f"/graph/graph/{phase}")
        assert response.status_code == 200
        assert fragment.encode("utf-8") in response.data


def test_create_directed_and_undirected_via_route(client) -> None:
    """Route should create graph in both modes."""
    undirected = client.post(
        "/graph/graph/operate",
        json={"operation": "create_graph", "payload": {"directed": "false"}},
    )
    assert undirected.status_code == 200
    assert undirected.get_json()["visual_state"]["directed"] is False

    directed = client.post(
        "/graph/graph/operate",
        json={"operation": "create_graph", "payload": {"directed": "true"}},
    )
    assert directed.status_code == 200
    assert directed.get_json()["visual_state"]["directed"] is True


def test_insert_remove_vertex_and_edge_via_route(client) -> None:
    """Route should mutate vertices and edges."""
    insert_vertex = client.post(
        "/graph/graph/operate",
        json={"operation": "insert_vertex", "payload": {"vertex": "1"}},
    )
    assert insert_vertex.status_code == 200

    insert_edge = client.post(
        "/graph/graph/operate",
        json={"operation": "insert_edge", "payload": {"origin": "1", "target": "2", "weight": "2"}},
    )
    assert insert_edge.status_code == 200
    assert insert_edge.get_json()["visual_state"]["metadata"]["edges_count"] == 1

    remove_edge = client.post(
        "/graph/graph/operate",
        json={"operation": "remove_edge", "payload": {"origin": "1", "target": "2"}},
    )
    assert remove_edge.status_code == 200

    remove_vertex = client.post(
        "/graph/graph/operate",
        json={"operation": "remove_vertex", "payload": {"vertex": "1"}},
    )
    assert remove_vertex.status_code == 200


def test_generate_random_graph_via_route(client) -> None:
    """Route should build a random graph from vertex count only."""
    response = client.post(
        "/graph/graph/operate",
        json={"operation": "generate_random_graph", "payload": {"vertices_count": "7"}},
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["visual_state"]["metadata"]["vertices_count"] == 7
    assert data["visual_state"]["metadata"]["edges_count"] >= 6


def test_queries_and_algorithms_via_route(client) -> None:
    """Route should expose queries and graph algorithms."""
    client.post(
        "/graph/graph/operate",
        json={"operation": "create_graph", "payload": {"directed": "false"}},
    )
    client.post(
        "/graph/graph/operate",
        json={"operation": "insert_edge", "payload": {"origin": "1", "target": "2", "weight": "1"}},
    )
    client.post(
        "/graph/graph/operate",
        json={"operation": "insert_edge", "payload": {"origin": "2", "target": "3", "weight": "2"}},
    )

    vertices = client.post("/graph/graph/operate", json={"operation": "list_vertices", "payload": {}})
    edges = client.post("/graph/graph/operate", json={"operation": "list_edges", "payload": {}})
    neighbors = client.post(
        "/graph/graph/operate",
        json={"operation": "neighbors", "payload": {"vertex": "2"}},
    )
    weight = client.post(
        "/graph/graph/operate",
        json={"operation": "edge_weight", "payload": {"origin": "1", "target": "2"}},
    )
    bfs = client.post("/graph/graph/operate", json={"operation": "run_bfs", "payload": {"start": "1"}})
    dfs = client.post("/graph/graph/operate", json={"operation": "run_dfs", "payload": {"start": "1"}})
    dijkstra = client.post(
        "/graph/graph/operate",
        json={"operation": "run_dijkstra", "payload": {"start": "1", "end": "3"}},
    )
    bellman = client.post(
        "/graph/graph/operate",
        json={"operation": "run_bellman_ford", "payload": {"start": "1", "end": "3"}},
    )
    prim = client.post("/graph/graph/operate", json={"operation": "run_prim", "payload": {"start": "1"}})
    kruskal = client.post("/graph/graph/operate", json={"operation": "run_kruskal", "payload": {}})

    assert vertices.status_code == 200
    assert edges.status_code == 200
    assert neighbors.status_code == 200
    assert weight.status_code == 200
    assert bfs.status_code == 200
    assert dfs.status_code == 200
    assert dijkstra.status_code == 200
    assert dijkstra.get_json()["result"]["path"] == [1, 2, 3]
    assert bellman.status_code == 200
    assert bellman.get_json()["result"]["path"] == [1, 2, 3]
    assert prim.status_code == 200
    assert kruskal.status_code == 200
    assert kruskal.get_json()["result"]["uses_union_find"] is True


def test_dijkstra_negative_weight_block_via_route(client) -> None:
    """Route should return didactic block for Dijkstra with negative weights."""
    client.post(
        "/graph/graph/operate",
        json={"operation": "create_graph", "payload": {"directed": "false"}},
    )
    client.post(
        "/graph/graph/operate",
        json={"operation": "insert_edge", "payload": {"origin": "1", "target": "2", "weight": "-1"}},
    )

    response = client.post(
        "/graph/graph/operate",
        json={"operation": "run_dijkstra", "payload": {"start": "1", "end": "2"}},
    )
    assert response.status_code == 400
    assert "Dijkstra" in response.get_json()["message"]


def test_prim_and_kruskal_directed_block_via_route(client) -> None:
    """Prim and Kruskal should fail didactically on directed graphs."""
    client.post(
        "/graph/graph/operate",
        json={"operation": "create_graph", "payload": {"directed": "true"}},
    )
    client.post(
        "/graph/graph/operate",
        json={"operation": "insert_edge", "payload": {"origin": "1", "target": "2", "weight": "1"}},
    )

    prim = client.post(
        "/graph/graph/operate",
        json={"operation": "run_prim", "payload": {"start": "1"}},
    )
    kruskal = client.post("/graph/graph/operate", json={"operation": "run_kruskal", "payload": {}})

    assert prim.status_code == 400
    assert "no dirigidos" in prim.get_json()["message"]
    assert kruskal.status_code == 400
    assert "no dirigidos" in kruskal.get_json()["message"]


def test_graph_session_persistence_and_reset(client) -> None:
    """Graph history should persist in session and reset correctly."""
    add_vertex = client.post(
        "/graph/graph/operate",
        json={"operation": "insert_vertex", "payload": {"vertex": "99"}},
    )
    assert add_vertex.status_code == 200

    list_vertices = client.post("/graph/graph/operate", json={"operation": "list_vertices", "payload": {}})
    assert 99 in list_vertices.get_json()["result"]

    reset = client.post("/graph/graph/reset")
    assert reset.status_code == 200
    assert reset.get_json()["visual_state"]["metadata"]["vertices_count"] == 0


def test_graph_help_pages_available(client) -> None:
    """Graph module help and structure help should be reachable."""
    module_help = client.get("/help/graph")
    structure_help = client.get("/help/graph/graph")

    assert module_help.status_code == 200
    assert b"Ayuda del modulo de grafos" in module_help.data
    assert structure_help.status_code == 200
    assert b"Operaciones soportadas" in structure_help.data


def test_graph_route_rejects_non_integer_vertex(client) -> None:
    """Graph route should reject non-integer vertices didactically."""
    response = client.post(
        "/graph/graph/operate",
        json={"operation": "insert_vertex", "payload": {"vertex": "A"}},
    )
    assert response.status_code == 400
    assert "entero" in response.get_json()["message"].lower()
