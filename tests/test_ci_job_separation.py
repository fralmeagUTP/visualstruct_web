"""Static regression checks for independent CI quality jobs."""

from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
WORKFLOWS = ROOT / ".github" / "workflows"


def _workflow(name: str) -> str:
    return (WORKFLOWS / name).read_text(encoding="utf-8")


def test_unit_integration_job_excludes_e2e_and_runs_coverage_gates() -> None:
    workflow = _workflow("tests-unit-integration.yml")
    assert "  unit-integration:" in workflow
    assert '-m "not e2e"' in workflow
    assert '-m "not e2e and not performance"' in workflow
    assert "scripts/check_coverage_gates.py" in workflow
    assert "playwright install" not in workflow


def test_e2e_job_installs_chromium_and_runs_only_browser_tests() -> None:
    workflow = _workflow("e2e-playwright.yml")
    assert "  e2e:" in workflow
    assert "playwright install --with-deps chromium" in workflow
    assert "tests/test_ui_playwright_e2e.py" in workflow
    assert "check_c_conformance.py" not in workflow


def test_c17_conformance_and_sanitizers_are_independent_jobs() -> None:
    workflow = _workflow("c-conformance.yml")
    assert "  c17-conformance:" in workflow
    assert "  sanitizers:" in workflow
    assert "python scripts/check_c_conformance.py\n" in workflow
    assert "bash scripts/check_c_sanitizers_linux.sh" in workflow
    assert workflow.index("  c17-conformance:") < workflow.index("  sanitizers:")


def test_quality_workflows_share_the_same_triggers() -> None:
    for name in (
        "tests-unit-integration.yml",
        "e2e-playwright.yml",
        "c-conformance.yml",
    ):
        workflow = _workflow(name)
        assert "pull_request:" in workflow
        assert "push:" in workflow
        assert "workflow_dispatch:" in workflow
