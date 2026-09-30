"""Exhaustive API campaign for every public sequential-adapter operation."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

import pytest

from app.services.structure_service import StructureService


OperationCase = tuple[list[tuple[str, dict[str, str]]], dict[str, str]]


def _case(setup: list[tuple[str, dict[str, str]]] | None = None, **payload: str) -> OperationCase:
    return setup or [], payload


CASES: dict[str, dict[str, OperationCase]] = {
    "stack": {
        "apilar": _case(value="7"),
        "desapilar": _case([("apilar", {"value": "7"})]),
        "limpiar": _case([("apilar", {"value": "7"})]),
    },
    "queue": {
        "encolar": _case(value="7"),
        "desencolar": _case([("encolar", {"value": "7"})]),
        "limpiar": _case([("encolar", {"value": "7"})]),
    },
    "priority_queue": {
        "encolar": _case(value="7", priority="1"),
        "desencolar": _case([("encolar", {"value": "7", "priority": "1"})]),
        "frente": _case([("encolar", {"value": "7", "priority": "1"})]),
        "limpiar": _case([("encolar", {"value": "7", "priority": "1"})]),
    },
    "linked_list": {
        "insertar_inicio": _case(value="7"),
        "insertar_final": _case(value="7"),
        "lista_insertar_elemento": _case([("insertar_inicio", {"value": "1"})], value="7", position="1"),
        "eliminar_elemento": _case([("insertar_inicio", {"value": "7"})], value="7"),
        "eliminar_repetidos": _case([("insertar_inicio", {"value": "7"}), ("insertar_final", {"value": "7"})], value="7"),
        "buscar_elemento": _case([("insertar_inicio", {"value": "7"})], value="7"),
        "mostrar": _case([("insertar_inicio", {"value": "7"})]),
        "limpiar": _case([("insertar_inicio", {"value": "7"})]),
        "insertar_posicion": _case([("insertar_inicio", {"value": "1"})], value="7", position="1"),
        "insertar_elemento": _case([("insertar_inicio", {"value": "1"})], value="7", position="1", relative="0"),
        "eliminar_primero": _case([("insertar_inicio", {"value": "7"})], value="7"),
        "buscar_posiciones": _case([("insertar_inicio", {"value": "7"})], value="7"),
        "eliminar_inicio": _case([("insertar_inicio", {"value": "7"})]),
        "eliminar_final": _case([("insertar_final", {"value": "7"})]),
        "eliminar_posicion": _case([("insertar_inicio", {"value": "7"})], position="1"),
        "invertir": _case([("insertar_inicio", {"value": "7"}), ("insertar_final", {"value": "8"})]),
        "primero": _case([("insertar_inicio", {"value": "7"})]),
        "ultimo": _case([("insertar_final", {"value": "7"})]),
    },
    "circular_list": {
        "insertar_inicio": _case(value="7"),
        "insertar_final": _case(value="7"),
        "eliminar_inicio": _case([("insertar_inicio", {"value": "7"})]),
        "eliminar_primero": _case([("insertar_inicio", {"value": "7"})], value="7"),
        "buscar_posiciones": _case([("insertar_inicio", {"value": "7"})], value="7"),
        "invertir": _case([("insertar_inicio", {"value": "7"}), ("insertar_final", {"value": "8"})]),
        "limpiar": _case([("insertar_inicio", {"value": "7"})]),
    },
    "sublist": {
        "insertar_padre": _case(parent="1"),
        "insertar_hijo": _case([("insertar_padre", {"parent": "1"})], parent="1", child="7"),
        "eliminar_padre": _case([("insertar_padre", {"parent": "1"})], parent="1"),
        "eliminar_hijo": _case([("insertar_padre", {"parent": "1"}), ("insertar_hijo", {"parent": "1", "child": "7"})], parent="1", child="7"),
        "hijos_de": _case([("insertar_padre", {"parent": "1"}), ("insertar_hijo", {"parent": "1", "child": "7"})], parent="1"),
        "limpiar": _case([("insertar_padre", {"parent": "1"})]),
    },
}


def _operation_ids() -> set[tuple[str, str]]:
    return {
        (structure["id"], operation["name"])
        for structure in StructureService.list_structures()
        for operation in StructureService._new_adapter(structure["id"]).get_supported_operations()
    }


def _case_ids() -> set[tuple[str, str]]:
    return {(structure_id, operation) for structure_id, operations in CASES.items() for operation in operations}


def _post(client: Any, structure_id: str, operation: str, payload: dict[str, str]) -> Any:
    return client.post(
        f"/sequential/{structure_id}/operate",
        json={"operation": operation, "payload": payload},
    )


def test_every_registered_sequential_operation_has_a_normal_case() -> None:
    """The QA scenario table must stay complete when adapters gain an operation."""
    assert _case_ids() == _operation_ids()


@pytest.mark.parametrize(
    ("structure_id", "operation"),
    sorted(_case_ids()),
)
def test_each_sequential_operation_succeeds_and_emits_synchronized_trace(client: Any, structure_id: str, operation: str) -> None:
    """Every public and hidden compatibility operation is exercised through its real route."""
    setup, payload = CASES[structure_id][operation]
    for setup_operation, setup_payload in setup:
        prepared = _post(client, structure_id, setup_operation, setup_payload)
        assert prepared.status_code == 200, prepared.get_json()

    response = _post(client, structure_id, operation, payload)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["success"] is True
    assert body["message"]
    assert body["visual_state"]["size"] >= 0
    assert body["execution_trace"]["steps"]
    assert body["execution_trace"]["steps"][-1]["state_after"] == body["visual_state"]
    assert all(step["pedagogy"]["invariant"]["holds"] for step in body["execution_trace"]["steps"])


@pytest.mark.parametrize("structure_id", sorted(CASES))
def test_input_validation_rejects_invalid_values_for_every_sequential_structure(client: Any, structure_id: str) -> None:
    """Each sequential family rejects a non-integer value without mutating its state."""
    adapter = StructureService._new_adapter(structure_id)
    operation = next(item for item in adapter.get_supported_operations() if item.get("inputs"))
    payload = {input_item["name"]: "not-an-int" for input_item in operation["inputs"]}

    response = _post(client, structure_id, operation["name"], payload)
    assert response.status_code == 400
    body = response.get_json()
    assert body["success"] is False
    assert body["visual_state"]["size"] == 0
    assert body["history"] == []


@pytest.mark.parametrize("boundary", [str(-(2**31)), str(2**31 - 1)])
@pytest.mark.parametrize(
    ("structure_id", "operation", "field"),
    [
        ("stack", "apilar", "value"),
        ("queue", "encolar", "value"),
        ("priority_queue", "encolar", "value"),
        ("linked_list", "insertar_inicio", "value"),
        ("circular_list", "insertar_inicio", "value"),
        ("sublist", "insertar_padre", "parent"),
    ],
)
def test_sequential_integer_boundaries_are_preserved_in_visual_state(client: Any, structure_id: str, operation: str, field: str, boundary: str) -> None:
    """Boundary integers must cross the route without string or precision drift."""
    payload = {field: boundary}
    if structure_id == "priority_queue":
        payload["priority"] = "0"
    response = _post(client, structure_id, operation, payload)

    assert response.status_code == 200, response.get_json()
    assert str(int(boundary)) in str(response.get_json()["visual_state"])


@pytest.mark.parametrize(
    ("structure_id", "operation", "payload"),
    [
        ("stack", "desapilar", {}),
        ("queue", "desencolar", {}),
        ("priority_queue", "desencolar", {}),
        ("priority_queue", "frente", {}),
        ("linked_list", "eliminar_inicio", {}),
        ("linked_list", "eliminar_final", {}),
        ("circular_list", "eliminar_inicio", {}),
        ("sublist", "hijos_de", {"parent": "1"}),
    ],
)
def test_sequential_empty_or_missing_parent_cases_are_controlled(client: Any, structure_id: str, operation: str, payload: dict[str, str]) -> None:
    """Underflow and missing-parent boundaries must be pedagogical 400 responses."""
    response = _post(client, structure_id, operation, payload)

    assert response.status_code == 400
    assert response.get_json()["success"] is False


def test_lifo_fifo_priority_and_circular_invariants_survive_history_replay(client: Any) -> None:
    """Representative histories prove the structural invariants after replay through the route."""
    for value in ("1", "2", "3"):
        assert _post(client, "stack", "apilar", {"value": value}).status_code == 200
        assert _post(client, "queue", "encolar", {"value": value}).status_code == 200
    assert _post(client, "priority_queue", "encolar", {"value": "late", "priority": "5"}).status_code == 400
    assert _post(client, "priority_queue", "encolar", {"value": "30", "priority": "3"}).status_code == 200
    assert _post(client, "priority_queue", "encolar", {"value": "10", "priority": "1"}).status_code == 200
    assert _post(client, "circular_list", "insertar_final", {"value": "1"}).status_code == 200
    assert _post(client, "circular_list", "insertar_final", {"value": "2"}).status_code == 200

    assert _post(client, "stack", "desapilar", {}).get_json()["result"] == 3
    assert _post(client, "queue", "desencolar", {}).get_json()["result"] == 1
    priority = _post(client, "priority_queue", "desencolar", {}).get_json()
    circular = _post(client, "circular_list", "buscar_posiciones", {"value": "2"}).get_json()

    assert priority["result"] == 10
    assert "prioridad 1" in priority["message"]
    assert circular["result"] == [2]
    assert circular["visual_state"]["kind"] == "circular"
