"""Seeded generation and shrinking tests for differential scenarios."""

import shutil

import pytest

from app.services.conformance import (
    ConformanceRunner,
    ScenarioOperation,
    generate_scenario,
    reduce_failing_sequence,
)
from app.services.conformance.runner import SPECS


@pytest.mark.parametrize("structure_id", sorted(SPECS))
def test_generation_is_reproducible(structure_id: str) -> None:
    first = generate_scenario(structure_id, seed=20260818, length=5)
    second = generate_scenario(structure_id, seed=20260818, length=5)
    different = generate_scenario(structure_id, seed=20260819, length=5)
    assert first == second
    assert first != different


@pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc no está instalado")
@pytest.mark.parametrize("structure_id", sorted(SPECS))
def test_generated_scenario_is_equivalent(structure_id: str) -> None:
    operations = generate_scenario(structure_id, seed=73, length=5)
    result = ConformanceRunner().compare(structure_id, operations)
    assert result.equivalent, (result.c_state, result.python_state)


def test_reducer_returns_one_minimal_reproduction() -> None:
    operations = [
        ScenarioOperation("insert", {"value": value}) for value in (1, 2, 99, 3, 4)
    ]

    reduced = reduce_failing_sequence(
        operations,
        lambda candidate: any(item.payload.get("value") == 99 for item in candidate),
    )

    assert reduced == [ScenarioOperation("insert", {"value": 99})]
