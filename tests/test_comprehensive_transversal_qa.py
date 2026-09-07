"""Cross-module functional QA cases for the comprehensive validation campaign."""

from __future__ import annotations

import pytest

from app.services.session_service import SESSION_KEY


@pytest.mark.parametrize(
    ("path", "expected_fragment"),
    [
        ("/", b"Visualizador Web de Estructuras de Datos"),
        ("/healthz", b'"status":"ok"'),
        ("/sequential/", b"Estructuras Secuenciales"),
        ("/hierarchical/", b"Estructuras Jerarquicas"),
        ("/graph/", b"Grafos"),
        ("/hash/", b"Hash"),
        ("/sorting/", b"Ordenamiento"),
        ("/help/manual", b"Manual de uso"),
    ],
)
def test_public_module_entries_and_health_contract(client, path: str, expected_fragment: bytes) -> None:
    """Every top-level student entry point must load without a server error."""
    response = client.get(path)

    assert response.status_code == 200
    assert expected_fragment in response.data


@pytest.mark.parametrize(
    "path",
    [
        "/sequential/unknown",
        "/hierarchical/unknown",
        "/graph/unknown",
        "/hash/unknown",
    ],
)
def test_unknown_public_structures_return_not_found(client, path: str) -> None:
    """Invalid navigation must be a controlled 404 instead of an internal error."""
    assert client.get(path).status_code == 404


@pytest.mark.xfail(
    strict=True,
    reason="QA-ROUTE-HELP-UNKNOWN: las rutas de ayuda aceptan estructuras inexistentes en vez de responder 404.",
)
@pytest.mark.parametrize(
    "path",
    [
        "/help/sequential/unknown",
        "/help/hierarchical/unknown",
        "/help/graph/unknown",
        "/help/hash/unknown",
    ],
)
def test_unknown_structure_help_routes_must_return_not_found(client, path: str) -> None:
    """Known defect: help routes need the same structure validation as visual routes."""
    assert client.get(path).status_code == 404


@pytest.mark.parametrize(
    "path",
    [
        "/sequential/stack/operate",
        "/hierarchical/abb/operate",
        "/graph/graph/operate",
        "/hash/hash_table/operate",
    ],
)
def test_common_operation_endpoints_reject_malformed_requests(client, path: str) -> None:
    """A malformed common API request remains a didactic client error."""
    response = client.post(path, json={"operation": "", "payload": "invalid"})

    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["message"]


def test_history_is_isolated_by_module_and_reset_only_clears_its_own_state(client) -> None:
    """Session replay keys must not leak mutations from one module into another."""
    stack = client.post("/sequential/stack/operate", json={"operation": "apilar", "payload": {"value": "10"}})
    queue = client.post("/sequential/queue/operate", json={"operation": "encolar", "payload": {"value": "20"}})
    assert stack.status_code == queue.status_code == 200

    reset = client.post("/sequential/stack/reset")
    assert reset.status_code == 200
    assert reset.get_json()["history"] == []

    persisted_queue = client.get("/sequential/queue")
    assert persisted_queue.status_code == 200
    with client.session_transaction() as session:
        histories = session[SESSION_KEY]
        assert "stack" not in histories
        assert histories["queue"]["history"] == [{"operation": "encolar", "payload": {"value": "20"}}]


def test_trace_console_history_and_c_source_are_returned_for_a_successful_operation(client) -> None:
    """The primary API response must carry the synchronized didactic evidence."""
    response = client.post(
        "/sequential/stack/operate",
        json={"operation": "apilar", "payload": {"value": "7"}},
    )

    assert response.status_code == 200
    body = response.get_json()
    trace = body["execution_trace"]
    assert body["history"] == [{"operation": "apilar", "payload": {"value": "7"}}]
    assert body["visual_state"]["items"] == [{"value": 7}]
    assert trace["steps"]
    assert trace["steps"][-1]["state_after"] == body["visual_state"]
    assert trace["steps"][-1]["line_text"]
    assert body["message"]
