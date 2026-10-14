"""Static regression checks for independent CI quality jobs."""

from __future__ import annotations

from pathlib import Path
import json
import re


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
    """The complete browser scope is partitioned without dropping cases."""
    workflow = _workflow("e2e-playwright.yml")
    assert "  e2e:" in workflow
    assert "playwright install --with-deps ${{ matrix.suite }}" in workflow
    assert "timeout-minutes: ${{ matrix.minutes }}" in workflow
    assert "max-parallel: 2" in workflow
    assert "fail-fast: false" in workflow
    assert "PYTEST_ADDOPTS: ${{ matrix.addopts }}" in workflow
    assert "scripts/run_e2e_diagnostics.py --suite ${{ matrix.suite }} ${{ matrix.target }} ${{ matrix.cases }}" in workflow

    # Decode the flat include rows; compare values and their group association.
    include = workflow.split("        include:\n", 1)[1].split("\n    env:", 1)[0]
    rows = []
    for block in re.split(r"(?m)^          - ", include):
        if not block.strip():
            continue
        row = {}
        for line in block.splitlines():
            key, separator, value = line.strip().partition(": ")
            assert separator and key not in row
            row[key] = json.loads(value) if value.startswith('"') else int(value) if value.isdigit() else value
        rows.append(row)
    graph_case = "test_playwright_graph_execute_completes_algorithms_across_phases"
    chromium_target = "tests/test_ui_playwright_e2e.py"
    graph = [row for row in rows if row["group"] == "graph-algorithms"]
    firefox = [row for row in rows if row["group"] == "firefox-general"]
    chromium = [row for row in rows if row["group"].startswith("chromium-general-")]
    assert graph == [{"group":"graph-algorithms","suite":"chromium","target":chromium_target,
                      "cases":f"--case {graph_case}","addopts":"","minutes":40}]
    assert firefox == [{"group":"firefox-general","suite":"firefox","target":"tests/test_playwright_firefox_smoke.py",
                        "cases":"","addopts":"","minutes":20}]
    assert len(rows) == 6 and len(chromium) == 4
    for index, row in enumerate(chromium):
        assert row["group"] == f"chromium-general-{index}"
        assert row["suite"] == "chromium" and row["target"] == "tests"
        assert row["cases"] == f"--shard-index {index} --shard-count 4"
        assert row["addopts"] == f"-m e2e --ignore=tests/test_playwright_firefox_smoke.py --deselect={chromium_target}::{graph_case}"
        assert row["minutes"] == 40
    # The only ignored file and deselected case have complete dedicated jobs above.
    # Every remaining E2E case is included through the tests directory and one shard.
    assert re.findall(r"(?m)^  ([\w-]+):\s*$", workflow.split("\njobs:\n", 1)[1]) == ["e2e"]
    for trigger in ("push", "pull_request"):
        assert re.search(rf"(?m)^  {trigger}:\n    branches:\n      - main\n", workflow)
    assert re.search(r"(?m)^  workflow_dispatch:\s*$", workflow)
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
