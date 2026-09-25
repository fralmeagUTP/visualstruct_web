import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
QA = ROOT / "docs" / "qa"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def test_final_report_covers_every_inventory_operation_and_finding():
    inventory = load(QA / "didactic-c-trace-inventory.json")
    results = load(QA / "didactic-c-trace-results.json")
    finding_ids = {p.stem for p in (QA / "findings").glob("*.json")}

    assert results["schema"] == "didactic-c-trace-audit/v1"
    assert len(results["operation_results"]) == inventory["operations_count"] == 120
    assert all(row["result"] in {"passed", "failed"} and row["evidence"] for row in results["operation_results"])
    assert {f["case_id"] for f in results["findings"]} == finding_ids


def test_every_finding_is_reproducible_prioritized_and_characterized():
    results = load(QA / "didactic-c-trace-results.json")
    tests = (ROOT / "tests" / "test_didactic_qa_findings.py").read_text(encoding="utf-8").lower()
    backlog = (QA / "correction-backlog.md").read_text(encoding="utf-8")
    required = {"input", "expected", "observed", "severity", "probable_cause", "location", "recommended_test", "suggested_fix", "priority"}

    for finding in results["findings"]:
        assert required <= finding.keys()
        assert finding["expected"] and finding["observed"]
        assert finding["severity"] in {"critical", "high", "medium", "low"}
        assert finding["priority"] in {"P0", "P1", "P2"}
        assert finding["case_id"].lower().replace("-", "_") in tests
        assert finding["case_id"] in backlog


def test_published_minimal_fixture_matches_findings_and_no_product_fix_is_claimed():
    results = load(QA / "didactic-c-trace-results.json")
    fixtures = load(ROOT / "tests" / "qa" / "fixtures" / "didactic-qa-minimal-cases-v1.json")
    assert {c["case_id"] for c in fixtures["cases"]} == {f["case_id"] for f in results["findings"]}
    assert results["product_logic_modified"] is False
    assert (QA / "didactic-c-trace-audit.md").is_file()
