"""Unit tests for component and global coverage gates."""

from __future__ import annotations

from scripts.check_coverage_gates import COMPONENT_MINIMUMS, evaluate


def _summary(covered: int, total: int = 100) -> dict[str, int]:
    return {"covered_lines": covered, "num_statements": total}


def _passing_report() -> dict:
    return {
        "totals": _summary(83),
        "files": {
            path.replace("/", "\\"): {"summary": _summary(85)}
            for path in COMPONENT_MINIMUMS
        },
    }


def test_coverage_gates_accept_exact_thresholds_and_windows_paths() -> None:
    assert evaluate(_passing_report()) == []


def test_coverage_gates_reject_global_regression() -> None:
    report = _passing_report()
    report["totals"] = _summary(82)
    assert evaluate(report) == ["Cobertura global 82.00% < 83.00%."]


def test_coverage_gates_reject_critical_component_regression() -> None:
    report = _passing_report()
    component = next(iter(COMPONENT_MINIMUMS))
    report["files"][component.replace("/", "\\")]["summary"] = _summary(84)
    failures = evaluate(report)
    assert failures == [f"{component}: 84.00% < 85.00%."]


def test_coverage_gates_reject_missing_component_and_malformed_report() -> None:
    report = _passing_report()
    component = next(iter(COMPONENT_MINIMUMS))
    report["files"].pop(component.replace("/", "\\"))
    assert evaluate(report) == [f"Componente ausente del reporte: {component}."]
    assert evaluate({}) == [
        "El reporte de cobertura no contiene 'totals' y 'files' validos."
    ]
