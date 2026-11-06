"""Keep the allocation bytecode regression covered on the container runtime."""

from __future__ import annotations

from pathlib import Path
import re
import shlex

ROOT = Path(__file__).resolve().parents[1]


def test_container_runtime_allocation_job_is_independent_and_complete() -> None:
    workflow = (ROOT / ".github/workflows/tests-unit-integration.yml").read_text()
    job = workflow.split("  container-runtime-allocation:\n", 1)[1].split(
        "\n  unit-integration:", 1
    )[0]
    dockerfile = (ROOT / "Dockerfile").read_text()
    runtime = re.search(r"(?m)^FROM python:(\d+\.\d+)-slim\b", dockerfile)
    assert runtime is not None
    assert f'python-version: "{runtime.group(1)}"' in job
    assert "uses: actions/checkout@v4" in job
    assert "uses: actions/setup-python@v5" in job
    assert "runs-on: ubuntu-latest" in job
    assert "timeout-minutes: 10" in job
    assert "run: python -m pip install -r requirements-test.txt" in job

    command = job.split("        run: |\n", 1)[1].replace("\\\n", " ")
    assert shlex.split(command) == [
        "python", "-m", "pytest", "-q",
        "tests/test_allocation_constructor_offsets.py",
        "tests/test_sequential_acceptance_criteria_focal.py::test_required_allocation_failure_C_API",
        "tests/test_allocation_transport_fix.py::test_metadata_memory_error_is_not_relabelled_as_constructor_failure",
        "tests/test_ci_container_runtime_allocation.py",
    ]
    for target in shlex.split(command)[4:]:
        assert (ROOT / target.split("::", 1)[0]).is_file()
    for forbidden in (
        "strategy:", "matrix:", "needs:", "if:", "continue-on-error:",
        "permissions:", "VISUALSTRUCT_E2E_SHARD", "--deselect", "--ignore",
        "playwright install",
    ):
        assert forbidden not in job
