"""Coverage and execution tests for deterministic conformance cases."""

import shutil

import pytest

from app.services.conformance import CASES, ConformanceRunner
from app.services.conformance.runner import SPECS


def test_catalog_covers_all_registered_tads_and_categories() -> None:
    assert set(CASES) == set(SPECS)
    assert len(CASES) == 13
    for cases in CASES.values():
        assert cases.success
        assert cases.error


@pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc no está instalado")
@pytest.mark.parametrize("structure_id", sorted(CASES))
def test_deterministic_success_case_is_equivalent(structure_id: str) -> None:
    result = ConformanceRunner().compare(structure_id, list(CASES[structure_id].success))
    assert result.equivalent, (result.c_state, result.python_state)


@pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc no está instalado")
@pytest.mark.parametrize("structure_id", sorted(CASES))
def test_valid_boundary_case_is_equivalent(structure_id: str) -> None:
    result = ConformanceRunner().compare(structure_id, list(CASES[structure_id].boundary))
    assert result.equivalent, (result.c_state, result.python_state)


@pytest.mark.skipif(shutil.which("gcc") is None, reason="gcc no está instalado")
@pytest.mark.parametrize("structure_id", sorted(CASES))
def test_deterministic_error_is_rejected_by_c_and_python(structure_id: str) -> None:
    result = ConformanceRunner().compare_error(
        structure_id, list(CASES[structure_id].error)
    )
    assert result.equivalent, (result.c_error, result.python_error)
