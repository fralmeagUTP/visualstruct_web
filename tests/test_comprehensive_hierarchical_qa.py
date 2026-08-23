"""Complete route-level QA matrix for hierarchical structures."""

from __future__ import annotations

from typing import Any

import pytest

from app.services.hierarchical_structure_service import HierarchicalStructureService


TREE_SETUP = [("insertar", {"value": "8"}), ("insertar", {"value": "4"}), ("insertar", {"value": "12"})]
HEAP_SETUP = [("insertar", {"value": "8"}), ("insertar", {"value": "4"}), ("insertar", {"value": "12"})]

CASES: dict[str, dict[str, tuple[list[tuple[str, dict[str, str]]], dict[str, str]]]] = {
    "abb": {name: (TREE_SETUP, {"value": "8"} if name in {"eliminar", "buscar"} else {}) for name in ("eliminar", "buscar", "minimo", "maximo", "altura", "contar_hojas", "inorden", "preorden", "postorden", "validar", "limpiar")},
    "avl": {name: (TREE_SETUP, {"value": "8"} if name in {"eliminar", "buscar"} else {}) for name in ("eliminar", "buscar", "minimo", "maximo", "altura", "inorden", "validar", "limpiar")},
    "red_black": {name: (TREE_SETUP, {"value": "8"} if name in {"eliminar", "buscar"} else {}) for name in ("eliminar", "buscar", "inorden", "altura", "validar", "limpiar")},
    "binary_heap": {name: (HEAP_SETUP, {}) for name in ("extraer_raiz", "raiz", "a_lista", "limpiar")},
}
for tree in ("abb", "avl", "red_black"):
    CASES[tree]["insertar"] = ([], {"value": "8"})
CASES["binary_heap"]["insertar"] = ([], {"value": "8"})


def _post(client: Any, structure: str, operation: str, payload: dict[str, str]) -> Any:
    return client.post(f"/hierarchical/{structure}/operate", json={"operation": operation, "payload": payload})


def _registered() -> set[tuple[str, str]]:
    return {(s["id"], op["name"]) for s in HierarchicalStructureService.list_structures() for op in HierarchicalStructureService._new_adapter(s["id"]).get_supported_operations()}


def test_hierarchical_case_matrix_covers_every_registered_operation() -> None:
    assert {(structure, operation) for structure, cases in CASES.items() for operation in cases} == _registered()


@pytest.mark.parametrize(("structure", "operation"), sorted(_registered()))
def test_every_hierarchical_operation_has_valid_state_and_trace(client: Any, structure: str, operation: str) -> None:
    setup, payload = CASES[structure][operation]
    for setup_op, setup_payload in setup:
        assert _post(client, structure, setup_op, setup_payload).status_code == 200
    response = _post(client, structure, operation, payload)
    assert response.status_code == 200, response.get_json()
    body = response.get_json()
    assert body["success"] is True
    assert body["execution_trace"]["steps"]
    assert body["execution_trace"]["steps"][-1]["state_after"] == body["visual_state"]
    assert all(step["pedagogy"]["invariant"]["holds"] for step in body["execution_trace"]["steps"])


@pytest.mark.parametrize("structure", ["abb", "avl", "red_black", "binary_heap"])
def test_hierarchical_invalid_integer_is_rejected_without_history(client: Any, structure: str) -> None:
    response = _post(client, structure, "insertar", {"value": "invalid"})
    assert response.status_code == 400
    assert response.get_json()["history"] == []


@pytest.mark.parametrize("structure", ["abb", "avl", "red_black"])
def test_balanced_tree_rotations_and_deletion_keep_invariants(client: Any, structure: str) -> None:
    for value in ("30", "20", "10", "25", "40", "50"):
        assert _post(client, structure, "insertar", {"value": value}).status_code == 200
    assert _post(client, structure, "eliminar", {"value": "30"}).status_code == 200
    validated = _post(client, structure, "validar", {}).get_json()
    ordered = _post(client, structure, "inorden", {}).get_json()
    assert validated["result"] is True
    assert ordered["result"] == [10, 20, 25, 40, 50]


def test_heap_extracts_in_ascending_order_and_preserves_heap_property(client: Any) -> None:
    for value in ("9", "1", "7", "1", "3"):
        assert _post(client, "binary_heap", "insertar", {"value": value}).status_code == 200
    extracted = [_post(client, "binary_heap", "extraer_raiz", {}).get_json()["result"] for _ in range(5)]
    assert extracted == [1, 1, 3, 7, 9]
