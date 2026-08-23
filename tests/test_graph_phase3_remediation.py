import pytest

from app.adapters.graph_adapter import GraphAdapter
from app.domain.graph import PesoNegativoError


def add_vertices(adapter, *vertices):
    for vertex in vertices:
        adapter.execute("insert_vertex", {"vertex": vertex})


def test_edge_auto_creates_endpoints_and_duplicate_updates_integer_weight():
    adapter = GraphAdapter()
    adapter.execute("create_graph", {"directed": True})
    adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 5})
    adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 7})
    assert adapter.graph.vertices() == [1, 2]
    assert adapter.graph.aristas() == [(1, 2, 7.0)]
    assert adapter.to_visual_state()["edges"][0]["weight"] == 7.0


@pytest.mark.parametrize("weight", [2.5, "2.75", True, "no-numero"])
def test_non_integer_weight_is_rejected_without_mutating_graph(weight):
    adapter = GraphAdapter()
    with pytest.raises(ValueError, match="entero"):
        adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": weight})
    assert adapter.graph.vertices() == []
    assert adapter.graph.aristas() == []


def test_directed_and_undirected_edges_keep_the_declared_orientation_contract():
    directed = GraphAdapter()
    directed.execute("create_graph", {"directed": True})
    directed.execute("insert_edge", {"origin": 1, "target": 2, "weight": 3})
    assert directed.graph.existe_arista(1, 2)
    assert not directed.graph.existe_arista(2, 1)

    undirected = GraphAdapter()
    undirected.execute("insert_edge", {"origin": 1, "target": 2, "weight": 3})
    assert undirected.graph.existe_arista(1, 2)
    assert undirected.graph.existe_arista(2, 1)
    assert undirected.graph.cantidad_aristas() == 1


def test_bfs_and_dfs_expose_c_return_order():
    adapter = GraphAdapter()
    adapter.execute("create_graph", {"directed": True})
    for edge in ((1, 2), (2, 3)):
        adapter.execute("insert_edge", {"origin": edge[0], "target": edge[1], "weight": 1})
    assert adapter.execute("run_bfs", {"start": 1})["result"] == [1, 2, 3]
    assert adapter.execute("run_dfs", {"start": 1})["result"] == [1, 2, 3]


def test_dijkstra_rejects_any_negative_edge_before_relaxation():
    adapter = GraphAdapter()
    adapter.execute("create_graph", {"directed": True})
    adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 1})
    adapter.execute("insert_edge", {"origin": 9, "target": 10, "weight": -1})
    with pytest.raises(PesoNegativoError):
        adapter.execute("run_dijkstra", {"start": 1, "end": 2})


def test_prim_and_kruskal_report_forest_for_disconnected_graph():
    adapter = GraphAdapter()
    add_vertices(adapter, 1, 2, 3, 4, 5)
    adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 4})
    adapter.execute("insert_edge", {"origin": 3, "target": 4, "weight": 2})
    for operation, payload in (("run_prim", {"start": 1}), ("run_kruskal", {})):
        result = adapter.execute(operation, payload)["result"]
        assert result["connected"] is False
        assert result["components_count"] == 3
        assert result["kind"] == "minimum_spanning_forest"
        assert len(result["mst_edges"]) == 2
        assert result["total_weight"] == 6.0


def test_prim_and_kruskal_report_mst_for_connected_graph():
    adapter = GraphAdapter()
    for origin, target, weight in ((1, 2, 3), (2, 3, 1), (1, 3, 9)):
        adapter.execute("insert_edge", {"origin": origin, "target": target, "weight": weight})
    for operation, payload in (("run_prim", {"start": 1}), ("run_kruskal", {})):
        result = adapter.execute(operation, payload)["result"]
        assert result["connected"] is True
        assert result["components_count"] == 1
        assert result["kind"] == "mst"
        assert result["total_weight"] == 4.0


def test_mst_algorithms_reject_directed_graphs():
    adapter = GraphAdapter()
    adapter.execute("create_graph", {"directed": True})
    adapter.execute("insert_edge", {"origin": 1, "target": 2, "weight": 1})
    with pytest.raises(ValueError, match="no dirigido"):
        adapter.execute("run_prim", {"start": 1})
    with pytest.raises(ValueError, match="no dirigido"):
        adapter.execute("run_kruskal", {})
