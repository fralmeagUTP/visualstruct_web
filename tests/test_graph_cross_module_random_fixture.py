"""Keep the cross-module trace fixture finite without weakening dense refusal."""
from copy import deepcopy

from app.services.graph_structure_service import GraphStructureService as GraphService


def _construction_history(seed):
    # Same mutating prefix as the visible-method consumer, including the
    # removal/recreation of vertex 2. The last edge removal leaves it isolated.
    commands = [
        ("create_graph", {"directed": "false"}),
        ("generate_random_graph", {"vertices_count": "6", "seed": seed}),
        ("insert_vertex", {"vertex": "2"}),
        ("remove_vertex", {"vertex": "2"}),
        ("insert_edge", {"origin": "1", "target": "2", "weight": "1"}),
        ("remove_edge", {"origin": "1", "target": "2"}),
    ]
    return [
        {"operation": operation, "payload": payload,
         "source_contract": GraphService.SOURCE_CONTRACT}
        for operation, payload in commands
    ]


def test_seed_zero_has_nontrivial_paths_and_keeps_all_six_algorithms_below_budget(monkeypatch):
    def unexpected_randomness(*args, **kwargs):
        raise AssertionError("A stored seed must not consult the ambient RNG")

    with monkeypatch.context() as scoped:
        scoped.setattr("app.domain.graph.graph_commands.random.randint", unexpected_randomness)
        adapter, _ = GraphService._rebuild_adapter("graph", _construction_history(0))
        assert len(adapter.graph._g._vertices) == 6
        assert len(adapter.graph._g._arcos) == 12
        for operation in ("run_bfs", "run_dfs", "run_dijkstra", "run_bellman_ford", "run_prim", "run_kruskal"):
            result = adapter.execute(operation, {"start": "1", "end": "3"})
            assert 0 < adapter._last_book_execution["event_count"] <= 4000
            if operation in {"run_bfs", "run_dfs"}:
                assert result["success"] is True
                assert set(result["result"]) == {1, 3, 4, 5, 6}
            elif operation in {"run_dijkstra", "run_bellman_ford"}:
                assert result["success"] is True
                assert result["result"]["path"] == [1, 3]
                assert result["result"]["distance_to_destination"] == 3
            else:
                # This inherited operation order deliberately leaves vertex 2
                # isolated. Preserve the real disconnected C result as well.
                assert result["success"] is False
                assert result["c_status"] == 5
                assert result["result"]["connected"] is False


def test_dense_seed_retains_complete_budget_rejection_and_normal_c_result():
    history = _construction_history(26)
    original = deepcopy(history)
    adapter, _ = GraphService._rebuild_adapter("graph", history)
    before = adapter.to_visual_state()
    expected = adapter.execute("run_kruskal", {})
    assert len(adapter.graph._g._arcos) == 18
    assert adapter._last_book_execution["event_count"] == 4570

    rejected = GraphService.execute_operation("graph", "run_kruskal", {}, history)
    assert rejected["success"] is False
    assert rejected["preserve_session"] is True
    assert rejected["history"] == history == original
    assert rejected["visual_state"] == before
    assert rejected["trace_event_limit"] == 4000
    assert rejected["trace_available"] is False
    assert rejected["execution_trace"] is None

    normal = GraphService.execute_operation("graph", "run_kruskal", {}, history, execution_mode="normal")
    assert normal["success"] is expected["success"] is False
    assert normal["c_status"] == expected["c_status"] == 5
    assert normal["result"] == expected["result"]
    assert normal["trace_available"] is False
    assert normal["execution_trace"] is None
    assert normal["trace_event_limit"] == 4000
    assert history == original
    assert normal["history"][:-1] == original
    assert normal["history"][-1] == {
        "operation": "run_kruskal", "payload": {},
        "source_contract": GraphService.SOURCE_CONTRACT,
    }
