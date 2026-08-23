"""Publish the immutable mapping from QA findings to remediation regressions."""

from __future__ import annotations

import ast
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINDINGS = ROOT / "docs" / "qa" / "findings"
FIXTURES = ROOT / "tests" / "qa" / "fixtures" / "didactic-qa-minimal-cases-v1.json"
TEST_FILE = ROOT / "tests" / "test_didactic_qa_findings.py"
OUTPUT = ROOT / "docs" / "qa" / "remediation-regression-matrix-v1.json"
AUDIT_RESULTS = ROOT / "docs" / "qa" / "didactic-c-trace-results.json"
EVIDENCE = ROOT / "docs" / "qa" / "remediation-evidence"


def main() -> None:
    fixtures = json.loads(FIXTURES.read_text(encoding="utf-8"))["cases"]
    fixture_by_id = {case["case_id"]: case for case in fixtures}
    audited = json.loads(AUDIT_RESULTS.read_text(encoding="utf-8"))["findings"]
    priority_by_id = {finding["case_id"]: finding["priority"] for finding in audited}
    tree = ast.parse(TEST_FILE.read_text(encoding="utf-8"))
    test_names = [node.name for node in tree.body if isinstance(node, ast.FunctionDef) and node.name.startswith("test_")]
    rows = []
    for path in sorted(FINDINGS.glob("*.json")):
        finding = json.loads(path.read_text(encoding="utf-8"))
        case_id = finding["case_id"]
        token = case_id.lower().replace("-", "_")
        matching = [name for name in test_names if token in name]
        if len(matching) != 1:
            raise SystemExit(f"{case_id}: expected exactly one characterization test, got {matching}")
        if case_id not in fixture_by_id:
            raise SystemExit(f"{case_id}: missing minimal fixture")
        rows.append({
            "case_id": case_id,
            "priority": priority_by_id[case_id],
            "severity": finding["severity"],
            "structure_id": finding["structure_id"],
            "operation": finding["operation"],
            "fixture": f"tests/qa/fixtures/didactic-qa-minimal-cases-v1.json#{case_id}",
            "characterization_test": f"tests/test_didactic_qa_findings.py::{matching[0]}",
            "current_state": "fixed_pending_gate" if (EVIDENCE / f"{case_id}.json").is_file() else "known_failure",
            "closure_rule": "Replace the reproducer assertion with the corrected contract assertion; do not delete the fixture, test, or oracle evidence.",
            "remediation_evidence": f"docs/qa/remediation-evidence/{case_id}.json" if (EVIDENCE / f"{case_id}.json").is_file() else None,
        })
    if set(fixture_by_id) != {row["case_id"] for row in rows}:
        raise SystemExit("Fixture and finding case IDs differ")
    OUTPUT.write_text(json.dumps({
        "schema": "didactic-remediation-regressions/v1",
        "source_findings": "docs/qa/findings/*.json",
        "cases_count": len(rows),
        "cases": rows,
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
