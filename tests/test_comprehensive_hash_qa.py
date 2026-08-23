"""Complete route-level QA matrix for fixed-capacity hash tables."""

from __future__ import annotations

from typing import Any

import pytest

from app.services.hash_structure_service import HashStructureService


TABLE = [("create_table", {"capacity": "3"})]
ENTRIES = TABLE + [("insert", {"key": "1", "value": "10"}), ("insert", {"key": "4", "value": "40"})]
CASES: dict[str, tuple[list[tuple[str, dict[str, str]]], dict[str, str]]] = {
    "create_table": ([], {"capacity": "3"}),
    "insert": (TABLE, {"key": "1", "value": "10"}),
    "get": (ENTRIES, {"key": "4"}),
    "contains": (ENTRIES, {"key": "4"}),
    "remove": (ENTRIES, {"key": "4"}),
    "keys": (ENTRIES, {}),
    "values": (ENTRIES, {}),
    "items": (ENTRIES, {}),
    "stats": (ENTRIES, {}),
    "clear": (ENTRIES, {}),
    "destroy_table": (ENTRIES, {}),
}


def _post(client: Any, operation: str, payload: dict[str, str]) -> Any:
    return client.post("/hash/hash_table/operate", json={"operation": operation, "payload": payload})


def test_hash_case_matrix_covers_every_registered_operation() -> None:
    operations = {entry["name"] for entry in HashStructureService._new_adapter("hash_table").get_supported_operations()}
    assert set(CASES) == operations


@pytest.mark.parametrize("operation", sorted(CASES))
def test_every_hash_operation_returns_consistent_state_and_trace(client: Any, operation: str) -> None:
    setup, payload = CASES[operation]
    for setup_op, setup_payload in setup:
        assert _post(client, setup_op, setup_payload).status_code == 200
    response = _post(client, operation, payload)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["execution_trace"]["steps"]
    assert body["execution_trace"]["steps"][-1]["state_after"] == body["visual_state"]
    assert all(step["pedagogy"]["invariant"]["holds"] for step in body["execution_trace"]["steps"])


def test_hash_collision_update_negative_key_and_removal_preserve_bucket_invariants(client: Any) -> None:
    assert _post(client, "create_table", {"capacity": "3"}).status_code == 200
    for key, value in (("1", "10"), ("4", "40"), ("-2", "20")):
        assert _post(client, "insert", {"key": key, "value": value}).status_code == 200
    update = _post(client, "insert", {"key": "4", "value": "44"}).get_json()
    assert update["visual_state"]["metadata"]["size"] == 3
    assert _post(client, "get", {"key": "4"}).get_json()["result"] == 44
    assert _post(client, "get", {"key": "-2"}).get_json()["result"] == 20
    assert _post(client, "remove", {"key": "1"}).status_code == 200
    assert _post(client, "contains", {"key": "1"}).get_json()["result"] is False


def test_hash_allocation_failure_and_invalid_capacity_leave_state_safe(client: Any) -> None:
    invalid = _post(client, "create_table", {"capacity": "0"})
    assert invalid.status_code == 400
    assert _post(client, "create_table", {"capacity": "3"}).status_code == 200
    failed = _post(client, "insert", {"key": "1", "value": "10", "simulate_allocation_failure": "true"})
    assert failed.status_code == 400
    assert failed.get_json()["visual_state"]["metadata"]["size"] == 0


def test_hash_capacity_comparison_is_isolated_and_validates_payload(client: Any) -> None:
    bad = client.post("/hash/compare-capacities", json={"entries": "invalid"})
    assert bad.status_code == 400
    compared = client.post(
        "/hash/compare-capacities",
        json={"entries": [[1, 10], [4, 40]], "success_key": 4, "absent_key": 99},
    )
    assert compared.status_code == 200
    assert compared.get_json()["success"] is True
