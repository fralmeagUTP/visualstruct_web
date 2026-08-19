"""Differential C/Python runner tests."""

import shutil

import pytest

from app.services.conformance import (
    ConformanceRunner,
    ConformanceRunnerError,
    ScenarioOperation,
)


pytestmark = pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc no está instalado")


def test_runner_compares_equivalent_stack_scenario() -> None:
    result = ConformanceRunner().compare(
        "stack",
        [
            ScenarioOperation("apilar", {"value": 1}),
            ScenarioOperation("apilar", {"value": 2}),
            ScenarioOperation("desapilar", {}),
            ScenarioOperation("apilar", {"value": 3}),
        ],
    )
    assert result.equivalent
    assert result.c_state["state"] == {"values": [3, 1], "size": 2}


def test_runner_compares_equivalent_queue_scenario() -> None:
    result = ConformanceRunner().compare(
        "queue",
        [
            ScenarioOperation("encolar", {"value": 4}),
            ScenarioOperation("encolar", {"value": 7}),
            ScenarioOperation("desencolar", {}),
        ],
    )
    assert result.equivalent
    assert result.python_state["state"] == {"values": [7], "size": 1}


def test_runner_rejects_unregistered_or_arbitrary_operations() -> None:
    runner = ConformanceRunner()
    with pytest.raises(ConformanceRunnerError, match="no registrado"):
        runner.compare("unknown", [])
    with pytest.raises(ConformanceRunnerError, match="no soportada"):
        runner.compare("stack", [ScenarioOperation("shell", {"value": 1})])


@pytest.mark.parametrize(
    ("structure_id", "operations"),
    [
        ("linked_list", [ScenarioOperation("insertar_final", {"value": 2}), ScenarioOperation("insertar_inicio", {"value": 1}), ScenarioOperation("insertar_final", {"value": 3})]),
        ("circular_list", [ScenarioOperation("insertar_final", {"value": 1}), ScenarioOperation("insertar_final", {"value": 2}), ScenarioOperation("invertir", {})]),
        ("priority_queue", [ScenarioOperation("encolar", {"value": 10, "priority": 3}), ScenarioOperation("encolar", {"value": 20, "priority": 1})]),
        ("sublist", [ScenarioOperation("insertar_padre", {"parent": 1}), ScenarioOperation("insertar_hijo", {"parent": 1, "child": 8})]),
    ],
)
def test_runner_compares_remaining_sequential_scenarios(
    structure_id: str, operations: list[ScenarioOperation]
) -> None:
    result = ConformanceRunner().compare(structure_id, operations)
    assert result.equivalent, (result.c_state, result.python_state)


@pytest.mark.parametrize(
    ("structure_id", "operations"),
    [
        ("binary_heap", [ScenarioOperation("insertar", {"value": 5}), ScenarioOperation("insertar", {"value": 1}), ScenarioOperation("insertar", {"value": 3}), ScenarioOperation("extraer_raiz", {})]),
        ("abb", [ScenarioOperation("insertar", {"value": 2}), ScenarioOperation("insertar", {"value": 1}), ScenarioOperation("insertar", {"value": 3}), ScenarioOperation("eliminar", {"value": 2})]),
        ("avl", [ScenarioOperation("insertar", {"value": 30}), ScenarioOperation("insertar", {"value": 20}), ScenarioOperation("insertar", {"value": 10})]),
        ("red_black", [ScenarioOperation("insertar", {"value": 10}), ScenarioOperation("insertar", {"value": 20}), ScenarioOperation("insertar", {"value": 30})]),
    ],
)
def test_runner_compares_heap_and_tree_scenarios(
    structure_id: str, operations: list[ScenarioOperation]
) -> None:
    result = ConformanceRunner().compare(structure_id, operations)
    assert result.equivalent, (result.c_state, result.python_state)


@pytest.mark.parametrize(
    ("structure_id", "operations"),
    [
        ("graph", [ScenarioOperation("create_graph", {"directed": True}), ScenarioOperation("insert_vertex", {"vertex": 1}), ScenarioOperation("insert_vertex", {"vertex": 2}), ScenarioOperation("insert_edge", {"origin": 1, "target": 2, "weight": 7})]),
        ("hash_table", [ScenarioOperation("insert", {"key": "2", "value": "20"}), ScenarioOperation("insert", {"key": "1", "value": "10"}), ScenarioOperation("insert", {"key": "2", "value": "22"})]),
        ("sorting", [ScenarioOperation("create_array", {"values": [5, -1, 3, 3]}), ScenarioOperation("select_algorithm", {"algorithm_id": "quicksort"}), ScenarioOperation("run", {"mode": "fast"})]),
    ],
)
def test_runner_compares_specialized_scenarios(
    structure_id: str, operations: list[ScenarioOperation]
) -> None:
    result = ConformanceRunner().compare(structure_id, operations)
    assert result.equivalent, (result.c_state, result.python_state)
