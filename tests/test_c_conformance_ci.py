"""Static contract tests for the C conformance CI matrix."""

import importlib.util
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_script():
    path = ROOT / "scripts" / "check_c_conformance.py"
    spec = importlib.util.spec_from_file_location("check_c_conformance", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_ci_matrix_covers_exactly_thirteen_tads() -> None:
    module = _load_script()
    assert len(module.CHECKS) == 13


def test_workflow_has_separate_strict_and_sanitizer_jobs() -> None:
    workflow = (ROOT / ".github" / "workflows" / "c-conformance.yml").read_text(encoding="utf-8")
    assert "c17-conformance:" in workflow
    assert "sanitizers:" in workflow
    assert "bash scripts/check_c_sanitizers_linux.sh" in workflow
