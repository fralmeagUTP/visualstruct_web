"""Regressions for the approved integer domain and executed cycle API error."""
from copy import deepcopy
import pytest
from app.adapters.graph_adapter import GraphAdapter

@pytest.mark.parametrize("weight,accepted,expected", [
    (-2147483648, True, -2147483648), (2147483647, True, 2147483647),
    (2.0, True, 2), ("2.0", True, 2), (2.5, False, None),
    (2147483648, False, None), (-2147483649, False, None),
    (float("inf"), False, None), (float("-inf"), False, None),
    (float("nan"), False, None), (True, False, None),
])
def test_finite_c_int_weight(client, weight, accepted, expected):
    client.post("/graph/graph/operate", json={"operation": "create_graph", "payload": {"directed": True}})
    response = client.post("/graph/graph/operate", json={"operation": "insert_edge", "payload": {"origin": 1, "target": 2, "weight": weight}})
    assert response.status_code == (200 if accepted else 400)
    data = response.get_json()
    assert data["success"] is accepted
    if accepted:
        assert data["visual_state"]["edges"][0]["weight"] == expected
    else:
        assert data["visual_state"]["edges"] == []


def test_extreme_cycle_is_executed_error_preserving_prior_query(client, monkeypatch):
    def post(op, payload):
        return client.post("/graph/graph/operate", json={"operation": op, "payload": payload})
    assert post("create_graph", {"directed": True}).status_code == 200
    assert post("insert_edge", {"origin": 1, "target": 2, "weight": -2147483648}).status_code == 200
    success = post("run_bellman_ford", {"start": 1, "end": 2}).get_json()
    assert success["success"] and success["result"]["distance_to_destination"] == -2147483648
    assert post("insert_edge", {"origin": 2, "target": 1, "weight": -2147483648}).status_code == 200
    calls = []
    original = GraphAdapter.execute
    def spy(self, operation, payload):
        if operation == "run_bellman_ford":
            calls.append(deepcopy(payload))
        return original(self, operation, payload)
    monkeypatch.setattr(GraphAdapter, "execute", spy)
    failed = post("run_bellman_ford", {"start": 1, "end": 2})
    assert failed.status_code == 400
    data = failed.get_json()
    assert not data["success"] and data["result"]["has_negative_cycle"]
    assert data["result"]["path"] == [] and data["result"]["distance_to_destination"] is None
    assert data["visual_state"]["last_operation"]["status"] == "error"
    assert sum(x["operation"] == "run_bellman_ford" for x in data["history"]) == 1
    assert any("Se detecto un ciclo negativo." in step.get("console", []) for step in data["execution_trace"]["steps"])
    for _ in range(2):
        assert client.get("/graph/graph").status_code == 200
    assert calls == [{"start": 1, "end": 2}]
