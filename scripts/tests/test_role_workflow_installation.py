"""Verify permanent role runtime and dated acceptance survive archive; no app imports."""
import hashlib
import json
import re
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'scripts'))
from check_session_continuity import GuardError,checkpoint
from role_workflow import evaluate
ARCHIVE=ROOT/'openspec/changes/archive/2026-10-02-extend-continuity-role-workflow'
RETIRED='openspec/changes/extend-continuity-role-workflow/'

class RoleArchiveInstallationTests(unittest.TestCase):
    def mapping(self):
        return json.loads((ROOT/'openspec/continuity/role-workflow-archive.json').read_text(encoding='utf-8'))
    def resolve(self,ref):
        mapping=self.mapping()
        ref=mapping['input_overrides'].get(ref,ref)
        if ref.startswith(mapping['retired_prefix']):
            ref=mapping['archive_prefix']+ref[len(mapping['retired_prefix']):]
        target=(ROOT/ref).resolve()
        self.assertTrue(target.is_relative_to(ROOT))
        self.assertTrue(target.is_file(),ref)
        return target
    def test_permanent_runtime_links_and_no_retired_assignment(self):
        self.assertFalse((ROOT/RETIRED).exists())
        self.assertTrue(ARCHIVE.is_dir())
        for ref in ['openspec/continuity/ROLE-WORKFLOW.md','openspec/continuity/ROLE-WORKFLOW-QUICKSTART.md','openspec/continuity/README.md']:
            text=(ROOT/ref).read_text(encoding='utf-8')
            self.assertNotIn(RETIRED,text)
            for link in re.findall(r'\[[^\]]+\]\(([^)]+)\)',text):
                if '://' not in link:self.assertTrue((ROOT/ref).parent.joinpath(link).is_file(),link)
        profile=json.loads((ROOT/'openspec/continuity/role-workflow.json').read_text(encoding='utf-8'))
        self.assertEqual(profile['tasks'],{})
        self.assertEqual(profile['change'],'SET_APPROVED_ACTIVE_CHANGE')
        with self.assertRaisesRegex(GuardError,'Unknown workflow task'):
            evaluate(ROOT,profile,'documentation-quickstart','before')
        index=json.loads((ROOT/'openspec/continuity/index.json').read_text(encoding='utf-8-sig'))
        self.assertNotIn('extend-continuity-role-workflow',index['changes'])
        with self.assertRaisesRegex(GuardError,'Unregistered change'):
            checkpoint(ROOT,index,'extend-continuity-role-workflow','workflow.documentation-pilot',ROOT)
    def test_all_genuine_qa_artifacts_preserved(self):
        baseline=json.loads((ARCHIVE/'evidence/closure-final/qa-before.json').read_text(encoding='utf-8'))
        self.assertTrue(baseline)
        for ref,sha in baseline.items():
            self.assertEqual(hashlib.sha256(self.resolve(ref).read_bytes()).hexdigest(),sha,ref)
    def test_accepted_inputs_resolve_to_identical_archived_bytes(self):
        for ref in ['evidence/adoption-pilot/documentation-verification.json',
                    'evidence/independent-review/adoption-review-20261002/independent-qa.json',
                    'evidence/closure-final/technical-qa-transfer.json']:
            record=json.loads((ARCHIVE/ref).read_text(encoding='utf-8'))
            self.assertTrue(record['executed']);self.assertEqual(record['result'],'passed')
            for source,sha in record['inputs'].items():
                self.assertEqual(hashlib.sha256(self.resolve(source).read_bytes()).hexdigest(),sha,source)
    def test_closed_tasks_and_new_requirements_preserved(self):
        tasks=(ARCHIVE/'tasks.md').read_text(encoding='utf-8')
        self.assertNotIn('- [ ]',tasks)
        doc=json.loads((ARCHIVE/'evidence/adoption-pilot/workflow.json').read_text(encoding='utf-8'))
        self.assertEqual(doc['tasks']['documentation-quickstart']['state'],'closed')
        implementation=json.loads((ARCHIVE/'evidence/closure-final/implementation-profile-closed.json').read_text(encoding='utf-8'))
        self.assertEqual(implementation['tasks']['workflow-minimum']['state'],'closed')
        canonical=(ROOT/'openspec/specs/session-continuity/spec.md').read_text(encoding='utf-8')
        delta=(ARCHIVE/'specs/session-continuity/spec.md').read_text(encoding='utf-8')
        for block in re.split(r'(?=### Requirement: )',delta)[1:]:
            self.assertIn(block.strip(),canonical)
        self.assertEqual(canonical.count('### Requirement:'),9)

if __name__=='__main__':unittest.main()
