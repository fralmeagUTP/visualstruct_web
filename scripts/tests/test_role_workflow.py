"""Role protocol tests in temporary fixtures, without application imports."""
import copy
import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from role_workflow import evaluate, ROLES
from check_session_continuity import GuardError

class RoleWorkflowTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(); self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        for ref in ['req.md', 'base.md', 'out/code.py', 'out/guide.md']:
            self.write(ref, 'fixture ' + ref)
        t = dict(objective='bounded fixture', role='code', owner='author', requirements=['req.md'],
                 base=['base.md'], allowed_paths=['out'], dependencies=[], deliverables=['out/code.py'],
                 documentation=['out/guide.md'], evidence=['run.json','qa.json'], checks=['unit'],
                 next_step='review', state='active', approval='approval.json', decisions=[],
                 reasoning={'default':'LOW','current':'LOW'})
        self.config = dict(schema='continuity-role-workflow/v1', project_root=str(self.root),
                           roles={r:{'enabled':True} for r in ROLES}, tasks={'t':t}, protected_paths=['foreign'])
        self.write('approval.json', json.dumps(dict(approved=True, owner='author', allowed_paths=['out'])))
        self.evidence()
    def write(self, ref, text):
        p=self.root/ref; p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text,encoding='utf-8')
    def evidence(self):
        inputs={ref:hashlib.sha256((self.root/ref).read_bytes()).hexdigest()
                for ref in ['req.md','base.md','out/code.py','out/guide.md']}
        self.record=dict(executed=True,result='passed',exit_code=0,observed_at_utc='2026-10-02T00:00:00Z',inputs=inputs)
        self.write('run.json',json.dumps(dict(self.record,check='unit')))
        self.write('qa.json',json.dumps(dict(self.record,kind='independent-qa',author='author',reviewer='reviewer',role='quality')))
    def run_gate(self, gate='before', **kwargs):
        return evaluate(self.root,self.config,'t',gate,**kwargs)
    def test_recovery_without_chat_and_no_writes(self):
        before={str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        recovered=self.run_gate()['recovered_task']
        self.assertEqual(recovered['next_step'],'review'); self.assertEqual(recovered['owner'],'author')
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.root.rglob('*') if p.is_file()})
    def test_stale_checkpoint(self):
        old=self.run_gate(); self.write('base.md','changed')
        with self.assertRaisesRegex(GuardError,'Stale checkpoint'):self.run_gate(previous=old)
    def test_config_change_stales_checkpoint(self):
        old=self.run_gate(); self.config['tasks']['t']['next_step']='different'
        with self.assertRaisesRegex(GuardError,'Stale checkpoint'):self.run_gate(previous=old)
    def test_evidence_invalidated(self):
        self.write('out/code.py','changed')
        with self.assertRaisesRegex(GuardError,'Evidence invalidated'):self.run_gate('verify')
    def test_required_check_failed(self):
        self.write('run.json',json.dumps(dict(self.record,check='unit',result='failed',exit_code=1)))
        with self.assertRaisesRegex(GuardError,'failed or not executed'):self.run_gate('verify')
    def test_not_run_not_approved(self):
        self.write('run.json',json.dumps(dict(self.record,check='unit',executed=False)))
        with self.assertRaisesRegex(GuardError,'not executed'):self.run_gate('verify')
    def test_pending_decision(self):
        self.config['tasks']['t']['decisions']=['decision.json'];self.write('decision.json','{"status":"pending"}')
        with self.assertRaisesRegex(GuardError,'Pending decision'):self.run_gate()
    def test_closed_work_report_only(self):
        self.config['tasks']['t']['state']='closed'
        with self.assertRaisesRegex(GuardError,'Closed work'):self.run_gate()
        self.assertEqual(self.run_gate('after')['purpose'],'report-only')
    def test_overlap_even_parent_child(self):
        other=copy.deepcopy(self.config['tasks']['t']);other['allowed_paths']=['out/code.py'];other['documentation']=[]
        self.config['tasks']['other']=other
        with self.assertRaisesRegex(GuardError,'Overlapping ownership'):self.run_gate()
    def test_sequential_nonoverlapping_writers(self):
        other=copy.deepcopy(self.config['tasks']['t']);other['allowed_paths']=['other'];other['deliverables']=['other/code'];other['documentation']=[]
        self.config['tasks']['other']=other
        with self.assertRaisesRegex(GuardError,'multiple active writers'):self.run_gate()
    def test_qa_separate_from_author(self):
        self.write('qa.json',json.dumps(dict(self.record,kind='independent-qa',author='author',reviewer='author',role='quality')))
        with self.assertRaisesRegex(GuardError,'differ'):self.run_gate('close')
    def test_successful_close_does_not_mutate_state(self):
        self.assertEqual(self.run_gate('close')['gate'],'close')
        self.assertEqual(self.config['tasks']['t']['state'],'active')
    def test_docs_required_for_close(self):
        self.config['tasks']['t']['documentation']=[]; self.config['tasks']['t']['evidence']=[]
        with self.assertRaises(GuardError):self.run_gate('close')
    def test_dependency_not_closed(self):
        dep=copy.deepcopy(self.config['tasks']['t']);dep['state']='pending'
        self.config['tasks']['dep']=dep;self.config['tasks']['t']['dependencies']=['dep']
        with self.assertRaisesRegex(GuardError,'Dependency not closed'):self.run_gate()
    def test_closed_dependency_stale_evidence(self):
        dep=copy.deepcopy(self.config['tasks']['t']);dep['state']='closed'
        self.config['tasks']['dep']=dep;self.config['tasks']['t']['dependencies']=['dep'];self.transition('dep');self.write('base.md','changed')
        with self.assertRaisesRegex(GuardError,'Evidence invalidated'):self.run_gate()
    def test_cycle(self):
        self.config['tasks']['t']['dependencies']=['t']
        with self.assertRaisesRegex(GuardError,'Invalid dependency'):self.run_gate()
    def test_protected_or_escape_path(self):
        self.config['tasks']['t']['allowed_paths']=['foreign']
        with self.assertRaisesRegex(GuardError,'Protected'):self.run_gate()
        self.config['tasks']['t']['allowed_paths']=['../escape']
        with self.assertRaisesRegex(GuardError,'Escaping'):self.run_gate()
    def test_wrong_approval(self):
        self.write('approval.json','{"approved":false}')
        with self.assertRaisesRegex(GuardError,'approval'):self.run_gate()
    def test_unbounded_escalation(self):
        self.config['tasks']['t']['reasoning']['current']='MEDIUM'
        with self.assertRaisesRegex(GuardError,'Unbounded'):self.run_gate()
    def transition(self, predecessor='old', kind='reopening'):
        task=self.config['tasks']['t']
        task['closed_scope_decisions']={predecessor:'transition.json'}
        task['decisions']=['transition.json']
        self.decision=dict(status='resolved',approved=True,predecessor=predecessor,task='t',
                           owner=task['owner'],allowed_paths=task['allowed_paths'],
                           reason='New evidence requires bounded review',kind=kind,new_scope='A new bounded requirement')
        self.write('transition.json',json.dumps(self.decision))
    def old_closed(self):
        self.config['tasks']['old']=dict(copy.deepcopy(self.config['tasks']['t']),state='closed')
    def test_snapshot_does_not_alias_callers_nested_config(self):
        snap=self.run_gate()
        self.config['tasks']['t']['allowed_paths'].append('new-path')
        self.assertEqual(snap['config']['tasks']['t']['allowed_paths'],['out'])
        self.assertEqual(snap['recovered_task']['allowed_paths'],['out'])
    def test_recovered_task_does_not_mutate_snapshot_config(self):
        snap=self.run_gate();snap['recovered_task']['next_step']='caller changed returned task'
        self.assertEqual(snap['config']['tasks']['t']['next_step'],'review')
        self.assertEqual(self.config['tasks']['t']['next_step'],'review')
    def test_new_id_same_closed_scope_requires_decision(self):
        self.old_closed()
        with self.assertRaisesRegex(GuardError,'Closed scope overlaps'):self.run_gate()
    def test_new_id_closed_parent_scope_requires_decision(self):
        self.old_closed();self.config['tasks']['t']['allowed_paths']=['out/code.py'];self.config['tasks']['t']['documentation']=[]
        self.write('approval.json',json.dumps(dict(approved=True,owner='author',allowed_paths=['out/code.py'])))
        with self.assertRaisesRegex(GuardError,'Closed scope overlaps'):self.run_gate()
    def test_bound_reopening_allowed(self):
        self.old_closed();self.transition()
        self.assertEqual(self.run_gate()['gate'],'before')
    def test_reopening_wrong_task_or_owner_or_scope_or_approval(self):
        self.old_closed();self.transition()
        for field,value in [('task','different'),('predecessor','other'),('owner','other'),('allowed_paths',['other']),('approved',False),('reason','  ')]:
            with self.subTest(field=field):
                self.write('transition.json',json.dumps(dict(self.decision,**{field:value})))
                with self.assertRaisesRegex(GuardError,'Invalid reopening'):self.run_gate()
    def test_generic_resolved_decision_cannot_reopen(self):
        self.old_closed();self.transition();self.write('transition.json','{"status":"resolved"}')
        with self.assertRaisesRegex(GuardError,'Invalid reopening'):self.run_gate()
    def test_successor_cannot_relabel_same_scope(self):
        self.old_closed();self.transition(kind='successor')
        with self.assertRaisesRegex(GuardError,'explicit new scope'):self.run_gate()
    def test_successor_with_explicit_new_scope_allowed(self):
        self.old_closed();self.transition(kind='successor');self.config['tasks']['t']['objective']='Distinct approved objective'
        self.assertEqual(self.run_gate()['gate'],'before')
    def test_successor_without_new_scope_rejected(self):
        self.old_closed();self.transition(kind='successor');self.config['tasks']['t']['objective']='Distinct approved objective'
        self.write('transition.json',json.dumps(dict(self.decision,new_scope='')))
        with self.assertRaisesRegex(GuardError,'explicit new scope'):self.run_gate()
    def test_nonoverlapping_closed_task_no_reopening_required(self):
        self.old_closed();old=self.config['tasks']['old'];old['allowed_paths']=['elsewhere'];old['deliverables']=['elsewhere/code'];old['documentation']=[]
        self.assertEqual(self.run_gate()['gate'],'before')
    def test_after_reports_overlap_without_authorizing_reopening(self):
        self.old_closed();self.assertEqual(self.run_gate('after')['purpose'],'report-only')
    def test_invalid_utc_timestamps_rejected(self):
        for stamp in ['not-a-date','2026-10-02','2026-10-02T00:00:00','2026-10-02T00:00:00+01:00','2026-02-30T00:00:00Z','2026-10-02T25:00:00Z',True,123,'2026-10-02T00:00:00-00:00']:
            with self.subTest(stamp=stamp):
                self.write('run.json',json.dumps(dict(self.record,check='unit',observed_at_utc=stamp)))
                with self.assertRaisesRegex(GuardError,'timestamp'):self.run_gate('verify')
    def test_valid_utc_timestamps_accepted(self):
        for stamp in ['2026-10-02T00:00:00Z','2026-10-02T00:00:00+00:00','2026-10-02T00:00:00.123456+00:00']:
            self.write('run.json',json.dumps(dict(self.record,check='unit',observed_at_utc=stamp)))
            self.assertEqual(self.run_gate('verify')['gate'],'verify')
    def test_qa_invalid_timestamp_rejected(self):
        self.write('qa.json',json.dumps(dict(self.record,kind='independent-qa',author='author',reviewer='reviewer',role='quality',observed_at_utc='not-a-date')))
        with self.assertRaisesRegex(GuardError,'timestamp'):self.run_gate('close')
    def test_role_required_checks(self):
        self.config['roles']['code']['required_checks']=['visual-accessibility-responsive']
        with self.assertRaisesRegex(GuardError,'Role checks missing'):self.run_gate()
    def test_disabled_role(self):
        self.config['roles']['code']['enabled']=False
        with self.assertRaisesRegex(GuardError,'Disabled'):self.run_gate()
    def test_unknown_schema_and_role(self):
        self.config['schema']='other'
        with self.assertRaisesRegex(GuardError,'schema'):self.run_gate()
    def test_missing_required_verification(self):
        self.config['tasks']['t']['checks']=['absent']
        with self.assertRaisesRegex(GuardError,'missing/ambiguous'):self.run_gate('verify')

if __name__=='__main__':unittest.main()
