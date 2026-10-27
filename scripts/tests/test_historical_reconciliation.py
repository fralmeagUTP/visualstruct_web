"""Read-only documentary C1 proofs; never import application modules."""
from __future__ import annotations
import ast
import hashlib
import json
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CHANGE = "reconcile-verified-historical-trace-contract"

def change_root():
    active = ROOT / "openspec/changes" / CHANGE
    archived = list((ROOT / "openspec/changes/archive").glob("*-" + CHANGE))
    roots = ([active] if active.exists() else []) + archived
    if len(roots) != 1:
        raise AssertionError("Exactly one C1 change context required")
    return roots[0]

def symbol(source, name):
    node = ast.parse(source)
    for part in name.split("."):
        node = next(x for x in node.body if getattr(x, "name", None) == part)
    return ast.dump(node, include_attributes=False)

class HistoricalReconciliationTests(unittest.TestCase):
    def test_one_complete_requirement_preserved_literally(self):
        base = change_root()
        records = json.loads((base/"evidence/requirement-decisions.json").read_text(encoding="utf-8"))
        admitted = [x for x in records["items"] if x["decision"] == "ADMITTED_VERIFIED_CONTRACT"]
        self.assertEqual(len(admitted), 1)
        delta = (base/"specs/didactic-conformance-remediation/spec.md").read_text(encoding="utf-8")
        self.assertEqual(delta.split("## ADDED Requirements", 1)[1].strip(), admitted[0]["text"].strip())
        self.assertEqual(admitted[0]["text"].count("#### Scenario:"), 2)

    def test_canonical_spec_contains_only_the_admitted_complete_contract(self):
        records = json.loads((change_root()/"evidence/requirement-decisions.json").read_text(encoding="utf-8"))
        admitted = next(x for x in records["items"] if x["decision"] == "ADMITTED_VERIFIED_CONTRACT")
        canonical = (ROOT/"openspec/specs/didactic-conformance-remediation/spec.md").read_text(encoding="utf-8")
        self.assertNotIn("TBD", canonical)
        self.assertEqual(canonical.count("### Requirement:"), 1)
        self.assertEqual(canonical[canonical.index("### Requirement:"):].strip(), admitted["text"].strip())

    def test_all_pending_requirements_keep_source_and_scenarios(self):
        records = json.loads((change_root()/"evidence/requirement-decisions.json").read_text(encoding="utf-8"))
        self.assertEqual((records["total_requirements"], records["admitted"], records["pending"]), (12, 1, 11))
        for item in records["items"]:
            self.assertIn("#### Scenario:", item["text"])
            self.assertTrue(item["reason"])
            raw = (ROOT/item["source"]).read_bytes()
            self.assertEqual(hashlib.sha256(raw).hexdigest(), item["source_sha256"])
            self.assertIn(item["text"], raw.decode("utf-8-sig"))

    def test_current_relevant_implementation_matches_proof(self):
        proof = json.loads((change_root()/"evidence/transfer-proof.json").read_text(encoding="utf-8"))
        for item in proof["whole_source_identity"]:
            self.assertTrue(item["same_normalized"])
            self.assertEqual(hashlib.sha256((ROOT/item["path"]).read_bytes()).hexdigest(), item["sha256"])
        for item in proof["symbol_identity"]:
            self.assertTrue(item["same_AST"])
            current = symbol((ROOT/item["path"]).read_text(encoding="utf-8-sig"), item["symbol"])
            self.assertEqual(hashlib.sha256(current.encode()).hexdigest(), item["ast_sha256"])

    def test_exact_historical_scenarios_have_executed_junit_evidence(self):
        proof = json.loads((change_root()/"evidence/transfer-proof.json").read_text(encoding="utf-8"))
        self.assertEqual(len(proof["execution"]), 2)
        cases = list(ET.parse(ROOT/"docs/qa/comprehensive-app-unit-results-v1.xml").iter("testcase"))
        for item in proof["execution"]:
            self.assertTrue(item["passed"])
            matches = [x for x in cases if x.attrib == item["case"]]
            self.assertEqual(len(matches), 1)
            self.assertFalse(any(matches[0].find(x) is not None for x in ["failure", "error", "skipped"]))

if __name__ == "__main__":
    unittest.main()
