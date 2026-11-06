"""Lossless replay budgets and atomic rejection across session-backed families."""
from copy import deepcopy

import pytest
from flask import session

from app.services.session_service import SESSION_KEY, SessionHistoryLimitError, SessionService


def test_persistence_safety_net_preserves_history_and_checkpoint_on_rejection(app):
    app.config["SESSION_MAX_HISTORY"] = 3
    history = [{"operation": "apilar", "payload": {"value": str(i)}} for i in range(3)]
    with app.test_request_context("/"):
        SessionService.save_history("stack", history)
        SessionService.save_checkpoint("stack", {"schema": "unchanged-test-marker"})
        before = deepcopy(dict(session))
        with pytest.raises(SessionHistoryLimitError, match="límite de 3"):
            SessionService.save_history("stack", history + [{"operation": "apilar", "payload": {"value": "9"}}])
        assert dict(session) == before


def test_oversized_legacy_record_is_readable_not_truncated_and_can_reset(app):
    app.config["SESSION_MAX_HISTORY"] = 3
    history = [{"operation": "apilar", "payload": {"value": str(i)}} for i in range(5)]
    with app.test_request_context("/"):
        session[SESSION_KEY] = {"stack": history}
        assert SessionService.get_history("stack") == history
        SessionService.save_history("stack", history)
        assert SessionService.get_history("stack") == history
        before = deepcopy(dict(session))
        with pytest.raises(SessionHistoryLimitError):
            SessionService.save_history("stack", history + [{"operation": "apilar", "payload": {"value": "9"}}])
        assert dict(session) == before
        SessionService.clear_history("stack")
        assert SessionService.get_history("stack") == []


CASES = [
    ("sequential", "stack", "apilar"),
    ("sequential", "queue", "encolar"),
    ("sequential", "priority_queue", "encolar"),
    ("sequential", "linked_list", "insertar_final"),
    ("sequential", "circular_list", "insertar_final"),
    ("sequential", "sublist", "insertar_padre"),
    *[("hierarchical", structure, "insertar") for structure in ["abb", "avl", "red_black", "binary_heap"]],
    ("hash", "hash_table", "insert"),
]


@pytest.mark.parametrize("family,structure,operation", CASES)
def test_history_budget_preserves_exact_session_and_state_in_each_structure(client, app, family, structure, operation):
    app.config["SESSION_MAX_HISTORY"] = 3
    endpoint = f"/{family}/{structure}"
    for value in range(1, 4):
        payload = {"value": str(value), "parent": str(value), "priority": "1", "key": str(value)}
        response = client.post(endpoint + "/operate", json={"operation": operation, "payload": payload})
        assert response.status_code == 200, response.get_data(as_text=True)
    expected = response.get_json()
    with client.session_transaction() as current:
        before = deepcopy(dict(current))
    rejected = client.post(endpoint + "/operate", json={"operation": operation, "payload": {"value": "9", "parent": "9", "key": "9", "priority": "1"}})
    assert rejected.status_code == 409, rejected.get_data(as_text=True)
    result = rejected.get_json()
    assert result["success"] is False
    assert result["preserve_session"] is True
    assert result["history"] == expected["history"]
    assert result.get("execution_trace") is None
    with client.session_transaction() as current:
        assert dict(current) == before
    assert client.get(endpoint).status_code == 200
    reset = client.post(endpoint + "/reset")
    assert reset.status_code == 200
    assert reset.get_json()["history"] == []


def test_sorting_history_budget_keeps_array_and_trace_metadata_then_allows_reset(client, app):
    app.config["SESSION_MAX_HISTORY"] = 3
    assert client.post("/api/ordenamiento/create-array", json={"values": [3, 2, 1]}).status_code == 200
    for algorithm in ["burbuja", "insercion"]:
        assert client.post("/api/ordenamiento/algorithm", json={"algorithm_id": algorithm}).status_code == 200
    with client.session_transaction() as current:
        before = deepcopy(dict(current))
    rejected = client.post("/api/ordenamiento/algorithm", json={"algorithm_id": "quicksort"})
    assert rejected.status_code == 409
    assert rejected.get_json()["preserve_session"] is True
    with client.session_transaction() as current:
        assert dict(current) == before
    state = client.get("/api/ordenamiento/state")
    assert state.status_code == 200
    assert state.get_json()["visual_state"]["items"] == [3, 2, 1]


def test_default_history_budget_accepts_300_but_rejects_301(app):
    app.config["SESSION_MAX_HISTORY"] = 300
    prefix = [{"operation": "apilar", "payload": {"value": str(i)}} for i in range(300)]
    with app.test_request_context("/"):
        SessionService.validate_history_capacity(prefix, prefix[:-1])
        with pytest.raises(SessionHistoryLimitError, match="límite de 300"):
            SessionService.validate_history_capacity(prefix + [prefix[-1]], prefix)
        SessionService.validate_history_capacity(prefix, prefix)
