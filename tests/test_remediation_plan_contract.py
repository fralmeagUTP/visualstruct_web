import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def test_regression_registry_freezes_all_29_findings_and_fixtures():
    matrix = json.loads((ROOT / "docs/qa/remediation-regression-matrix-v1.json").read_text(encoding="utf-8"))
    findings = {path.stem for path in (ROOT / "docs/qa/findings").glob("*.json")}
    rows = matrix["cases"]
    assert matrix["cases_count"] == len(rows) == 29
    assert {row["case_id"] for row in rows} == findings
    assert len({row["characterization_test"] for row in rows}) == 29
    assert {row["case_id"] for row in rows if row["current_state"] == "fixed_pending_gate"} == {
        "SORT-003", "GRAPH-001", "GRAPH-002", "GRAPH-003", "GRAPH-004", "GRAPH-006",
        "HASH-001", "HASH-002", "LINKED-001", "PRIORITY-001", "PRIORITY-002", "QUEUE-001", "STACK-001",
        "RBT-002", "SORT-004",
        "ABB-001", "AVL-001", "RBT-001", "HEAP-001", "STACK-002", "CIRCULAR-001", "SUBLIST-001", "SUBLIST-002",
        "GRAPH-005", "SORT-001", "SORT-002", "TRACE-001", "TRACE-002", "TRACE-003",
    }
    assert all(row["current_state"] in {"known_failure", "fixed_pending_gate"} for row in rows)
    assert all("do not delete" in row["closure_rule"] for row in rows)
    assert {priority: sum(row["priority"] == priority for row in rows) for priority in ("P0", "P1", "P2")} == {
        "P0": 1, "P1": 14, "P2": 14,
    }


def test_contract_decisions_cover_every_required_compatibility_choice():
    contract = (ROOT / "docs/conformance/didactic_remediation_contract_v2.md").read_text(encoding="utf-8")
    for decision in ("Grafo", "Hash", "Cola de prioridad", "Pila y cola", "Lista enlazada", "Sublista"):
        assert f"| {decision} |" in contract
    assert "contract_v2_incompatible" in contract
    assert "SESSION_RECORD_VERSION" in contract
    assert "no modifica todavía" in contract


def test_remediation_gates_include_all_required_layers():
    gates = (ROOT / "docs/qa/remediation-gates.md").read_text(encoding="utf-8")
    for gate in ("Registro", "Unidad e integración", "C17", "Sanitizers", "Reproducción", "UI", "Generación", "OpenSpec"):
        assert f"| {gate} |" in gates
