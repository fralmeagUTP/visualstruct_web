"""Finite overlay accounting and fail-closed checks; no browser/native campaign."""
from copy import deepcopy
import hashlib
import json
from pathlib import Path
from scripts.published_test_inputs import recorded_input_root, audit_input_path
import pytest
from scripts.app_quality_disposition_overlay import apply_disposition_overlay, inventory_identity
from scripts.build_app_quality_inventory import validate_executable_bindings, validate_inventory

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "openspec/changes/archive/2026-10-14-resolve-didactic-stack-c1-residuals"

def load(path):
    return json.loads(path.read_text(encoding="utf-8-sig"))

@pytest.fixture
def registered():
    inventory = load(BASE / "bindings-disposition-overlay/original-inventory-snapshot.json")
    bindings = load(BASE / "bindings-graph-main-fixed/app-executable-bindings.json")
    overlay = load(BASE / "bindings-disposition-overlay/overlay-current-after-archive.json")
    return inventory, bindings, overlay

def apply(data):
    return apply_disposition_overlay(*data, project_root=recorded_input_root())

def test_registered_overlay_preserves_originals_and_accounts_every_active_id(registered):
    before = deepcopy(registered)
    active, bindings, summary, errors = apply(registered)
    assert errors == []
    assert summary == {"original":375,"retired_authorized_not_PASS":7,"retired_dependency_not_PASS":1,"added":2,"active":369,"bound":369,"pending":[],"new_executions":0}
    assert validate_inventory(active) == []
    assert validate_executable_bindings(active, bindings) == []
    assert registered == before
    removed = {r["id"] for r in registered[2]["dispositions"] if r["status"].startswith("RETIRED")}
    assert len(removed) == 8
    assert removed.isdisjoint(bindings["items"])
    assert all(item["id"] not in removed for item in active["items"])

@pytest.mark.parametrize("corruption", ["identity", "unknown", "duplicate", "decision", "retired_pass", "dependency", "counter", "dynamic_duplicate"])
def test_corrupted_disposition_is_rejected(registered, corruption):
    overlay = registered[2]
    retired = next(r for r in overlay["dispositions"] if r["status"] == "RETIRED_AUTHORIZED")
    dependent = next(r for r in overlay["dispositions"] if r["status"] == "RETIRED_DEPENDENCY")
    if corruption == "identity": overlay["original_identity"] = "wrong"
    elif corruption == "unknown": overlay["dispositions"][0]["id"] = "missing"
    elif corruption == "duplicate": overlay["dispositions"].append(deepcopy(overlay["dispositions"][0]))
    elif corruption == "decision": retired["decision"]["sha256"] = "wrong"
    elif corruption == "retired_pass": retired["result"] = "PASS"
    elif corruption == "dependency": dependent["depends_on"] = "not-retired"
    elif corruption == "counter": overlay["expected_summary"]["bound"] += 1
    else: overlay["additions"].append(deepcopy(overlay["additions"][0]))
    assert apply(registered)[3]

@pytest.mark.parametrize("corruption", ["missing_binding", "missing_test", "no_expected", "wrong_layer", "changed_evidence"])
def test_overlay_cannot_bypass_executable_or_evidence_gate(registered, corruption):
    row = next(r for r in registered[2]["dispositions"] if r["status"] == "ACTIVE_REPLACEMENT")
    if corruption == "missing_binding": row.pop("binding")
    elif corruption == "missing_test": row["binding"]["test_node"] = "tests/test_app_quality_disposition_overlay.py::test_missing"
    elif corruption == "no_expected": row["binding"].pop("expected")
    elif corruption == "wrong_layer": row["binding"]["layer"] = "api"
    else: row["evidence"]["sha256"] = "changed"
    active, bindings, _, errors = apply(registered)
    assert errors or validate_executable_bindings(active, bindings)

def test_historical_sources_remain_byte_identical():
    for row in load(BASE / "bindings-disposition-overlay/raw-preservation-after-archive.json"):
        assert hashlib.sha256(audit_input_path(ROOT / row["path"]).read_bytes()).hexdigest() == row["sha256"]
