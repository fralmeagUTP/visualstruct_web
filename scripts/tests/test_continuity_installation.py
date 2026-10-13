"""Post-archive installation checks; read-only and isolated from the app."""
from __future__ import annotations
import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RETIRED = "openspec/changes/add-session-continuity-guard"
ARCHIVE = ROOT/"openspec/changes/archive/2026-10-02-add-session-continuity-guard"
SPEC = importlib.util.spec_from_file_location("installed_continuity_guard", ROOT/"scripts/check_session_continuity.py")
guard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(guard)

class ContinuityInstallationTests(unittest.TestCase):
    def test_bootstrap_script_and_index_use_stable_runtime(self):
        self.assertEqual(guard.CONFIG, ROOT/"openspec/continuity/index.json")
        self.assertFalse((ROOT/RETIRED).exists())
        self.assertTrue(ARCHIVE.is_dir())
        for name in ["AGENTS.md","scripts/check_session_continuity.py","openspec/continuity/index.json","openspec/continuity/README.md","openspec/continuity/reconciliation-status.md"]:
            text=(ROOT/name).read_text(encoding="utf-8-sig")
            self.assertNotIn(RETIRED+"/", text)

    def test_all_runtime_binding_and_assignment_links_resolve(self):
        config=json.loads(guard.CONFIG.read_text(encoding="utf-8-sig"))
        self.assertNotIn("add-session-continuity-guard", config["changes"])
        for change, entry in config["changes"].items():
            self.assertTrue((ROOT/"openspec/changes"/change).is_dir())
            refs=entry["sources"]+[entry["tasks"]]
            for binding in entry["operations"].values():
                refs += [binding["source"]]+binding.get("evidence",[])+binding.get("context_sources",[])
            if entry.get("assignment_source"):
                refs.append(entry["assignment_source"])
                assignment=json.loads((ROOT/entry["assignment_source"]).read_text(encoding="utf-8-sig"))
                refs.append(assignment["scope_ref"])
            for ref in refs:
                path=(ROOT/ref).resolve()
                self.assertTrue(path.is_relative_to(ROOT))
                self.assertTrue(path.is_file(), ref)
        for ref in ["openspec/specs/session-continuity/spec.md",
                    "openspec/changes/archive/2026-10-02-add-session-continuity-guard/reconciliation-options.md",
                    "openspec/changes/archive/2026-10-02-reconcile-verified-historical-trace-contract/reconciliation.md"]:
            self.assertTrue((ROOT/ref).is_file(),ref)

    def test_consolidated_requirements_are_preserved_and_purpose_complete(self):
        delta=(ARCHIVE/"specs/session-continuity/spec.md").read_text(encoding="utf-8-sig")
        canonical=(ROOT/"openspec/specs/session-continuity/spec.md").read_text(encoding="utf-8-sig")
        self.assertNotIn("TBD", canonical)
        def requirements(text):
            return {block.splitlines()[0]: block.strip()
                    for block in re.split(r"(?=### Requirement: )", text)[1:]}
        expected=requirements(delta)
        actual=requirements(canonical)
        self.assertEqual(len(expected),7)
        for name, block in expected.items():
            self.assertEqual(actual.get(name), block)
        # Later verified additions must not invalidate preservation of the original seven.
        role_archive=ROOT/"openspec/changes/archive/2026-10-02-extend-continuity-role-workflow"
        if role_archive.exists():
            role_delta=(role_archive/"specs/session-continuity/spec.md").read_text(encoding="utf-8-sig")
            for name, block in requirements(role_delta).items():
                self.assertEqual(actual.get(name), block)
        tasks=(ARCHIVE/"tasks.md").read_text(encoding="utf-8-sig")
        self.assertNotIn("- [ ]", tasks)

    def test_live_readonly_report_and_assignment_conflict_after_archive(self):
        config=json.loads(guard.CONFIG.read_text(encoding="utf-8-sig"))
        with self.assertRaisesRegex(guard.GuardError,"Unregistered change"):
            guard.checkpoint(ROOT,config,"add-session-continuity-guard",
                             "continuity.implementation",ROOT)
        if not config["changes"]:
            self.skipTest("No registered active work; installation links checked separately")
        change,entry=next(iter(config["changes"].items()))
        assignment=json.loads((ROOT/entry["assignment_source"]).read_text(encoding="utf-8-sig")) if entry.get("assignment_source") else None
        operation=assignment["operation"] if assignment else next(iter(entry["operations"]))
        assignment_id=assignment["assignment_id"] if assignment else ""
        result=guard.checkpoint(ROOT,config,change,operation,ROOT,phase="after",
                               assignment_id=assignment_id)
        self.assertEqual(result["purpose"],"completion-report-only")
        self.assertIn(operation,result["operations"])
        if assignment:
            self.assertEqual(result["assignment"]["operation"],operation)
            others=[name for name in entry["operations"] if name!=operation]
            if others:
                with self.assertRaisesRegex(guard.GuardError,"Assignment operation"):
                    guard.checkpoint(ROOT,config,change,others[0],ROOT,
                                     assignment_id=assignment_id)

if __name__=="__main__":
    unittest.main()
