import json
from pathlib import Path

from scripts.run_didactic_generated_audit import AUDITORS, ddmin, run_audit


ROOT = Path(__file__).resolve().parents[1]


def test_ddmin_reduces_to_minimal_failing_operation() -> None:
    operations = ["setup", "noise-a", "trigger", "noise-b", "finish"]
    reduced = ddmin(operations, lambda candidate: "trigger" in candidate)
    assert reduced == ["trigger"]


def test_generated_audit_smoke_covers_every_family() -> None:
    report = run_audit(3)
    assert set(report["families"]) == set(AUDITORS)
    assert report["total_sequences"] == 15
    assert all(not item["failures"] for item in report["families"].values())
    assert report["product_logic_changes"] == []


def test_published_generated_audit_contains_one_thousand_sequences_per_family() -> None:
    report = json.loads((ROOT / "docs/qa/generated-audit-v1.json").read_text(encoding="utf-8"))
    assert report["total_sequences"] == 5000
    assert set(report["families"]) == set(AUDITORS)
    assert all(item["sequences"] == 1000 and not item["failures"] for item in report["families"].values())
    assert report["product_logic_changes"] == []


def test_every_published_finding_has_a_named_characterization_test() -> None:
    test_source = (ROOT / "tests/test_didactic_qa_findings.py").read_text(encoding="utf-8").lower()
    finding_ids = {
        json.loads(path.read_text(encoding="utf-8"))["case_id"]
        for path in (ROOT / "docs/qa/findings").glob("*.json")
    }
    assert finding_ids
    for case_id in finding_ids:
        assert f"test_{case_id.lower().replace('-', '_')}" in test_source
