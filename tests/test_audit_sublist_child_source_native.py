"""Native instruction oracle for the visible Eliminar hijo source-plan correction.

Heap identity and alias UI remain separate open audit criteria; this test validates
physical instructions, actual guards and reachable values, including failure paths.
"""
import json,os,shutil,subprocess,sys
from pathlib import Path
import pytest

@pytest.fixture(scope='module')
def sublist_native_review(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: native C17 observation requires compiler')
 output=tmp_path_factory.mktemp('sublist-native');root=Path(__file__).resolve().parents[1]
 env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_ROOT':str(output),'PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_sublist_native_observer.py'))],env=env,capture_output=True,text=True,encoding='utf-8',timeout=90)
 assert run.returncode==0,run.stdout+run.stderr
 return json.loads((output/'audit-evidence/native-sublist-visible/review.json').read_text(encoding='utf-8'))

@pytest.mark.parametrize('case',[8,9,10,11,12,20])
def test_visible_child_removal_native_instruction_guard_and_reachable_state(sublist_native_review,case):
 review=sublist_native_review;meta=review['cases'][case];assert meta['operation']=='eliminar_hijo'
 rows=[r for r in review['rows'] if r['native']['case']==case];assert rows
 for row in rows:
  assert not set(row['issues'])&{'missing_instruction','physical_line_or_call_scope','condition_result','reachable_parent_child_values'},row
  assert row['step'] is not None
 # No fabricated predecessor identifier: it must agree with the actual downloaded C.
 texts=[row['step']['line_text'] for row in rows]
 assert all('previo' not in line for line in texts)
 if case==9:assert any('anterior->sgte = actual->sgte;' in line for line in texts)


def sublist_identity_map(rows):
 first=rows[0]['native'];nodes={n['id']:n for n in first['nodes']};mapping={0:'NULL'};parent=first['root'];i=0
 while parent>0:
  i+=1;mapping[parent]=f'P{i}';child=nodes[parent]['sub'];j=0
  while child>0:j+=1;mapping[child]=f'H{i}.{j}';child=nodes[child]['next']
  parent=nodes[parent]['next']
 return mapping

@pytest.mark.parametrize('case',[8,9,10,11,12,20])
def test_visible_child_removal_native_full_heap_alias_scope_and_free(sublist_native_review,case):
 rows=[r for r in sublist_native_review['rows'] if r['native']['case']==case];mapping=sublist_identity_map(rows)
 slots={'nuevo':0,'actual':1,'anterior':2,'next':3,'padre':4,'hijo':5}
 for row in rows:
  e=row['native'];step=row['step'];assert not row['issues'],row
  before=e['line'].startswith(('if ','while ','return ')) or e['condition']==-3
  state=step['state_snapshot'] if before else step['state_after'];assert state['sublist_delete_model']
  expected=[{'id':mapping[n['id']],'kind':'parent' if n['type']==1 else 'child','value':n['value'],'next':mapping[n['next']],**({'sub':mapping[n['sub']]} if n['type']==1 else {})} for n in e['nodes']]
  actual=[{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']];assert actual==expected
  assert state['head']==mapping[e['root']];assert len(state['sublist_frames'])==e['depth']+1
  assert state['sublist_frames'][-1]['function']==e['function']
  for name,slot in slots.items():
   alias=e['aliases'][slot]
   if alias==-2:continue
   expected_alias='indeterminado (liberado)' if alias<=-100 else mapping[alias]
   assert state[name]==expected_alias,(e,name,state)
  freed=step['pedagogy']['heap_transition']['freed']
  assert [x['id'] for x in freed]==([mapping[e['freed']]] if e['line']=='free(actual);' else [])
  assert all(x['allocated'] and not x['freed'] for x in step['pedagogy']['heap_objects'])
  if e['line']=='free(actual);':
   assert state['actual']=='indeterminado (liberado)';assert all(n['kind']=='parent' or n['id']!=mapping[e['freed']] for n in state['heap_nodes'])
  if e['condition']==-4:assert state['returned']==bool(e['return_value'])
  if e['line'].startswith('return sublista_eliminar_hijo_primero(') and e['condition']!=-4:
   assert step['pedagogy']['concept']=='call'
   assert step['pedagogy']['call_stack'][-1]['return'] is None
  assert step['pedagogy']['phase']['label']==step['pedagogy']['concept'].title()
 trace_steps=[row['step'] for row in rows]
 # Final return leaves every local frame but preserves the live parent/other-child heap.
 final=trace_steps[-1];assert not final['pedagogy']['memory_state']['sublist_frames']
 assert final['pedagogy']['memory_state']['scope_ended']


@pytest.mark.parametrize('case',[13,14,15,21])
def test_visible_list_children_native_source_guards_and_reachable_values(sublist_native_review,case):
 rows=[r for r in sublist_native_review['rows'] if r['native']['case']==case];assert rows
 for row in rows:
  assert not set(row['issues'])&{'missing_instruction','physical_line_or_call_scope','condition_result','reachable_parent_child_values'},row
 if case==14:
  assert any(row['native']['line']=='actual = padre->sub;' for row in rows)
  assert any(row['native']['line']=='while (actual != NULL && usados < capacidad)'+' {' for row in rows)
