"""Isolated continuity tests; no application fixtures, imports or services."""
from __future__ import annotations
import importlib.util
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SPEC = importlib.util.spec_from_file_location(
    "continuity_guard", Path(__file__).resolve().parents[1] / "check_session_continuity.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

class ContinuityTests(unittest.TestCase):
    """Verify failure gates independently of the live audit."""
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name).resolve()
        self.config = {
            "canonical_project": str(self.root), "changes": {
                "fixture": {
                    "sources": ["tasks.md"], "tasks": "tasks.md", "operations": {
                        "pending": {"source": "tasks.md", "scope": "recorded cases"},
                        "closed": {"source": "closure.md", "closed_marker": "# Verified closure",
                                   "scope": "one recorded case", "evidence": ["evidence.log"]},
                    }
                }
            }
        }
        for path, text in {
            "openspec/changes/fixture/proposal.md": "fixture active change",
            "openspec/AGENTS.md": "rules", "openspec/project.md": "context",
            "tasks.md": "- [x] done\n- [ ] pending\n  - [x] nested\n## Current\n",
            "closure.md": "# Verified closure\n", "evidence.log": "retained evidence",
        }.items():
            self.write(path, text)

    def write(self, path, text):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")

    def run_guard(self, **kwargs):
        args = dict(root=self.root, config=self.config, change="fixture",
                    operation="pending", cwd=self.root)
        args.update(kwargs)
        return guard.checkpoint(**args)

    def test_derived_count_and_no_writes(self):
        before = {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        result = self.run_guard()
        self.assertEqual(result["global_tasks"]["completed"], 1)
        self.assertEqual(result["global_tasks"]["total"], 2)
        self.assertEqual(result["operations"]["closed"]["status"], "recorded-closed")
        self.assertEqual(result["latest_task_heading"], "## Current")
        self.assertTrue(result["generated_at_utc"])
        self.assertEqual(before, {str(p): p.read_bytes() for p in self.root.rglob("*") if p.is_file()})

    def test_wrong_cwd_and_project(self):
        with self.assertRaisesRegex(guard.GuardError, "Wrong project"):
            self.run_guard(cwd=self.root / "other")
        self.config["canonical_project"] = str(self.root / "other")
        with self.assertRaisesRegex(guard.GuardError, "Wrong project"):
            self.run_guard()

    def test_unknown_change_and_operation(self):
        with self.assertRaisesRegex(guard.GuardError, "Unregistered change"):
            self.run_guard(change="unknown")
        with self.assertRaisesRegex(guard.GuardError, "Unregistered operation"):
            self.run_guard(operation="unknown")

    def test_missing_evidence_and_escape(self):
        (self.root / "evidence.log").unlink()
        with self.assertRaisesRegex(guard.GuardError, "Missing or escaping"):
            self.run_guard()
        with self.assertRaisesRegex(guard.GuardError, "Missing or escaping"):
            guard.read_source(self.root, "../outside.txt")

    def test_reopening_requires_persisted_identity_and_reason(self):
        with self.assertRaisesRegex(guard.GuardError, "Recorded closed"):
            self.run_guard(operation="closed")
        self.write("openspec/changes/fixture/decision.md", "closed: new regression")
        result = self.run_guard(operation="closed", reason="new regression",
                               decision_ref="openspec/changes/fixture/decision.md")
        self.assertEqual(result["reopen"]["reason"], "new regression")
        with self.assertRaisesRegex(guard.GuardError, "exact operation"):
            self.run_guard(operation="closed", reason="another reason",
                           decision_ref="openspec/changes/fixture/decision.md")

    def test_similar_operation_name_does_not_authorize_reopening(self):
        self.write("openspec/changes/fixture/decision.md", "closed-other: new regression")
        with self.assertRaisesRegex(guard.GuardError, "exact operation"):
            self.run_guard(operation="closed", reason="new regression",
                           decision_ref="openspec/changes/fixture/decision.md")

    def test_decision_from_other_change_is_rejected(self):
        self.write("openspec/changes/other/decision.md", "closed: new regression")
        with self.assertRaisesRegex(guard.GuardError, "change artifact"):
            self.run_guard(operation="closed", reason="new regression",
                           decision_ref="openspec/changes/other/decision.md")

    def test_unclosed_reopen_is_not_a_bypass(self):
        with self.assertRaisesRegex(guard.GuardError, "only to"):
            self.run_guard(reason="reason", decision_ref="file.md")

    def test_stale_checkpoint_and_identity(self):
        previous = self.run_guard()
        self.assertEqual(self.run_guard(previous=previous)["operation"], "pending")
        self.write("tasks.md", "- [x] changed\n")
        with self.assertRaisesRegex(guard.GuardError, "stale"):
            self.run_guard(previous=previous)
        previous["operation"] = "other"
        with self.assertRaisesRegex(guard.GuardError, "identity mismatch"):
            self.run_guard(previous=previous)

    def test_changed_source_set(self):
        previous = self.run_guard()
        self.write("extra.md", "extra")
        self.config["changes"]["fixture"]["sources"].append("extra.md")
        with self.assertRaisesRegex(guard.GuardError, "stale"):
            self.run_guard(previous=previous)

    def test_changes_during_second_read_fail(self):
        original = guard.read_source
        calls = {}
        def read(root, relative):
            calls[relative] = calls.get(relative, 0) + 1
            if relative == "tasks.md" and calls[relative] == 2:
                self.write("tasks.md", "changed")
            return original(root, relative)
        with patch.object(guard, "read_source", side_effect=read):
            with self.assertRaisesRegex(guard.GuardError, "during checkpoint"):
                self.run_guard()

    def register_assignment(self):
        self.write("openspec/changes/fixture/assignment.json",
            '{"assignment_id":"current-delete","change":"fixture","operation":"pending",'
            '"task":"current deletion instruction","scope_ref":"tasks.md"}')
        self.config["changes"]["fixture"]["assignment_source"] = "openspec/changes/fixture/assignment.json"

    def test_current_assignment_rejects_historical_closed_search_first(self):
        self.register_assignment()
        with self.assertRaisesRegex(guard.GuardError, "Assignment operation pending conflicts"):
            self.run_guard(operation="closed", assignment_id="current-delete")
        self.assertEqual(self.run_guard(assignment_id="current-delete")["operation"], "pending")
        # Even a persisted reopen reason cannot replace the assigned operation.
        self.write("openspec/changes/fixture/decision.md", "closed: historical search")
        with self.assertRaisesRegex(guard.GuardError, "Assignment operation pending conflicts"):
            self.run_guard(operation="closed", assignment_id="current-delete",
                           reason="historical search", decision_ref="openspec/changes/fixture/decision.md")

    def test_old_assignment_or_checkpoint_cannot_replace_new_instruction(self):
        self.register_assignment()
        before = self.run_guard(assignment_id="current-delete")
        with self.assertRaisesRegex(guard.GuardError, "Current assignment ID required"):
            self.run_guard(assignment_id="old-search")
        self.write("openspec/changes/fixture/assignment.json",
            '{"assignment_id":"new-delete-scope","change":"fixture","operation":"pending",'
            '"task":"new bounded scope","scope_ref":"tasks.md"}')
        with self.assertRaisesRegex(guard.GuardError, "Current assignment ID required"):
            self.run_guard(assignment_id="current-delete", previous=before)
        with self.assertRaisesRegex(guard.GuardError, "stale"):
            self.run_guard(assignment_id="new-delete-scope", previous=before)
        self.assertEqual(self.run_guard(assignment_id="new-delete-scope")["assignment"]["task"], "new bounded scope")

    def test_missing_assignment_id_does_not_infer_from_checkpoint(self):
        self.register_assignment()
        previous = self.run_guard(assignment_id="current-delete")
        with self.assertRaisesRegex(guard.GuardError, "Current assignment ID required"):
            self.run_guard(previous=previous)

    def test_active_change_becomes_archived(self):
        active = self.root / "openspec/changes/fixture"
        archived = self.root / "openspec/changes/archive/2026-10-02-fixture"
        archived.parent.mkdir(parents=True, exist_ok=True)
        active.rename(archived)
        with self.assertRaisesRegex(guard.GuardError, "not active"):
            self.run_guard()

    def test_new_unregistered_log_does_not_block_valid_checkpoint(self):
        previous = self.run_guard()
        self.write("new-run.log", "legitimate new result")
        result = self.run_guard(previous=previous, phase="after")
        self.assertEqual(result["phase"], "after")

    def test_appended_registered_log_requires_refresh_not_permanent_block(self):
        previous = self.run_guard()
        self.write("evidence.log", "retained evidence\nnew legitimate result")
        with self.assertRaisesRegex(guard.GuardError, "stale"):
            self.run_guard(previous=previous)
        fresh = self.run_guard(phase="after")
        self.assertEqual(fresh["operations"]["closed"]["status"], "recorded-closed")
        self.assertEqual(self.run_guard(previous=fresh)["operation"], "pending")

    def test_new_required_evidence_can_be_registered_and_refreshed(self):
        previous = self.run_guard()
        self.write("new-result.log", "new result")
        self.config["changes"]["fixture"]["operations"]["pending"]["evidence"] = ["new-result.log"]
        with self.assertRaisesRegex(guard.GuardError, "stale"):
            self.run_guard(previous=previous)
        fresh = self.run_guard(phase="after")
        self.assertIn("new-result.log", [m["path"] for m in fresh["sources"]])

    def test_task_status_is_derived_not_manual(self):
        self.config["changes"]["fixture"]["operations"]["pending"]["task_prefix"] = "pending"
        self.assertEqual(self.run_guard()["operations"]["pending"]["task_status"], "pending")
        self.write("tasks.md", "- [x] done\n- [x] pending\n")
        self.assertEqual(self.run_guard()["operations"]["pending"]["task_status"], "completed")
        self.assertEqual(self.run_guard()["operations"]["pending"]["status"], "not-signed-off")
        self.write("tasks.md", "- [x] different task\n")
        with self.assertRaisesRegex(guard.GuardError, "binding missing"):
            self.run_guard()

    def test_new_requirement_full_fixture_cycle_and_justified_reopen(self):
        change = "new-requirement"
        prefix = "openspec/changes/" + change + "/"
        artifacts = {
            "proposal.md": "Authorized fixture: new requirement",
            "design.md": "Test-only design",
            "tasks.md": "- [ ] Implement new requirement\n",
            "specs/fixture/spec.md": "## ADDED Requirements\n### Requirement: New behavior\nSHALL persist.\n#### Scenario: New request\n- **WHEN** requested\n- **THEN** persisted\n",
            "evidence/result.log": "not executed",
            "evidence/verification.md": "# Verification pending",
        }
        for rel, text in artifacts.items():
            self.write(prefix + rel, text)
        self.config["changes"][change] = {
            "sources": [prefix + p for p in ["proposal.md", "design.md", "tasks.md", "specs/fixture/spec.md"]],
            "tasks": prefix + "tasks.md",
            "operations": {"new.behavior": {
                "source": prefix + "evidence/verification.md",
                "closed_marker": "# Verified new behavior",
                "scope": "single fixture", "evidence": [prefix + "evidence/result.log"],
                "task_prefix": "Implement new requirement",
            }},
        }
        before = self.run_guard(change=change, operation="new.behavior")
        self.assertEqual(before["operations"]["new.behavior"]["status"], "not-signed-off")
        self.write(prefix + "tasks.md", "- [x] Implement new requirement\n")
        self.write(prefix + "evidence/result.log", "fixture checks passed")
        self.write(prefix + "evidence/verification.md", "# Verified new behavior")
        with self.assertRaisesRegex(guard.GuardError, "Recorded closed"):
            self.run_guard(change=change, operation="new.behavior", previous=before)
        with self.assertRaisesRegex(guard.GuardError, "stale"):
            self.run_guard(change=change, operation="new.behavior", previous=before, phase="after")
        # A fresh completion report never authorizes another implementation.
        completed = self.run_guard(change=change, operation="new.behavior", phase="after")
        self.assertEqual(completed["operations"]["new.behavior"]["status"], "recorded-closed")
        self.assertEqual(completed["purpose"], "completion-report-only")
        self.assertEqual(completed["global_tasks"]["completed"], 1)
        self.write(prefix + "decision.md", "new.behavior: regression after generator change; scope: fixture only")
        reopened = self.run_guard(change=change, operation="new.behavior",
            reason="regression after generator change", decision_ref=prefix+"decision.md")
        self.assertEqual(reopened["reopen"]["reason"], "regression after generator change")
        self.assertIn(prefix+"specs/fixture/spec.md", [m["path"] for m in reopened["sources"]])
        # Simulate reviewed consolidation only inside the temporary fixture.
        canonical = artifacts["specs/fixture/spec.md"].replace("## ADDED Requirements", "## Requirements")
        self.write("openspec/specs/fixture/spec.md", canonical)
        archived = self.root / "openspec/changes/archive/2026-10-02-new-requirement"
        archived.parent.mkdir(parents=True, exist_ok=True)
        archived.relative_to(self.root)
        (self.root / prefix).rename(archived)
        self.assertIn("### Requirement: New behavior", (self.root/"openspec/specs/fixture/spec.md").read_text())
        self.assertTrue((archived/"evidence/result.log").is_file())
        with self.assertRaisesRegex(guard.GuardError, "not active"):
            self.run_guard(change=change, operation="new.behavior", phase="after")

    def test_missing_closure_marker_does_not_infer_signoff(self):
        self.write("closure.md", "historical work; no signoff")
        result = self.run_guard(operation="closed")
        self.assertEqual(result["operations"]["closed"]["status"], "not-signed-off")

if __name__ == "__main__":
    unittest.main()
