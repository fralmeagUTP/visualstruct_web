"""Height instruction scopes observed independently in copies of HTTP C/H."""
from pathlib import Path
import os,sys,json,shutil,subprocess
import pytest
from test_audit_abb_insert_native import identities

@pytest.fixture(scope='module')
def abb_leaves_native_review(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: leaves remains unverified')
 output=tmp_path_factory.mktemp('abb-leaves-native');root=Path(__file__).resolve().parents[1]
 env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_ROOT':str(output),'AUDIT_ABB_OPERATION':'contar_hojas','AUDIT_ABB_LEAF_SKEW_CASES':'1','PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_abb_native_observer.py'))],env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0,run.stdout+run.stderr
 review=json.loads((output/'review.json').read_text(encoding='utf-8'));assert len(review['cases'])==5 and review['native_events']==126 and len(review['rows'])==121;return review

def leaves_matches(trace,events):
 used=set();matches=[]
 for e in events:
  if e['phase']=='caller':step=trace['steps'][-1]
  else:
   phase=e['phase']
   candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==phase];assert candidates,e
   step=candidates[0];used.add(step['step_index'])
  matches.append((e,step))
 return matches

@pytest.mark.parametrize('case',range(5))
def test_leaves_every_native_instruction_heap_scope_local_and_return(abb_leaves_native_review,case):
 review=abb_leaves_native_review;meta=review['cases'][case];trace=meta['trace'];assert meta['api_success'] and meta['result_same'] and meta['final_tree_same']
 events=[{**x['native'],'source_line':x['source_line']} for x in review['rows'] if x['native']['case']==case];events.append(meta['native_endpoint']);mapping=identities(events)
 assert len(trace['steps'])==len(events)+2
 for e,step in leaves_matches(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if e['phase']=='return' else ped['memory_state']
  assert state['root']==trace['final_state']['root'] and state['head']==mapping[e['root']]
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted([{'id':mapping[n['id']],'value':n['value'],'left':mapping[n['left']],'right':mapping[n['right']]} for n in e['nodes']],key=lambda n:n['id'])
  assert len(state['tree_frames'])==len(e['frames']) and len({f['id'] for f in state['tree_frames']})==len(e['frames'])
  for depth,(f,n) in enumerate(zip(state['tree_frames'],e['frames'])):
   assert f['function']==n['function']=='abb_contarHojas' and f['depth']==depth and f['parameters']=={'nodo':mapping[n['nodo']]}
   assert f['locals']=={}
   expected={name:('en evaluacion' if flag==1 else value if flag==2 else 'no evaluado') for name,(flag,value) in zip(['left','right'],n['leaf_operands'])}
   assert f['expression']==(expected if any(x[0] for x in n['leaf_operands']) else None)
  assert state['console_stdout']==bytes.fromhex(e['console_hex']).decode()=='' and not step['console']
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['memory']['dangling_references'] and not ped['return_propagation']['reconnects_subtree']
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='return':
   assert ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and ped['call_stack'][-1]['return']==e['result']
   assert len(ped['memory_state']['tree_frames'])==len(e['frames'])-1 and ped['memory_state']['returned']==e['result']
  if e['phase'].startswith('call_'):assert state['tree_frames'][-1]['expression'][e['phase'][5:]]=='en evaluacion'
  if e['phase'].startswith('operand_'):assert state['tree_frames'][-1]['expression'][e['phase'][8:]]==e['result']
  assert all(v['name'] in {'raiz','nodo'} for v in ped['variables'])
  assert all(f['locals']=={} for f in ped['call_stack'])
  if e['phase']=='caller':assert state['wrapper_result']==e['result'] and not state['caller_frame']
 assert trace['steps'][-1]['state_after']==trace['final_state']
 assert not trace['steps'][0]['state_snapshot']['tree_frames'] and trace['steps'][0]['state_snapshot']['wrapper_result'] is None
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_leaves_permitted_right_first_model_matches_independent_native_subtree_results(abb_leaves_native_review):
 from copy import deepcopy
 from app.domain.hierarchical.abb_leaves_instruction import build_abb_leaves_trace
 from app.services.c_code_service import CCodeService
 for case,meta in enumerate(abb_leaves_native_review['cases']):
  events=[{**x['native'],'source_line':x['source_line']} for x in abb_leaves_native_review['rows'] if x['native']['case']==case];mapping=identities(events)
  returns={mapping[e['frames'][-1]['nodo']]:e['result'] for e in events if e['phase']=='return'}
  base={**deepcopy(meta['trace']),'source_code':CCodeService.get_structure_data('abb')['operations']['contar_hojas']}
  model=build_abb_leaves_trace(base,meta['trace']['steps'][0]['state_snapshot'],meta['trace']['final_state'],evaluation_order='right-first')
  assert model['steps'][-1]['pedagogy']['memory_state']['wrapper_result']==meta['native_endpoint']['result']
  for step in model['steps']:
   ped=step['pedagogy'];assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'];assert all(f['locals']=={} for f in ped['call_stack'])
   assert ped['memory_state']['root']==meta['trace']['final_state']['root'] and ped['memory_state']['console_stdout']==''
   if ped['instruction_event']['phase']=='return':assert ped['return_propagation']['value']==returns[step['state_snapshot']['tree_frames'][-1]['parameters']['nodo']]
  calls=[x for x in model['steps'] if x['pedagogy']['instruction_event']['phase'].startswith('call_')]
  if calls:assert calls[0]['pedagogy']['instruction_event']['phase']=='call_right'
  assert 'right-first (opcion permitida)' in model['source_code']

def test_leaves_conditions_short_circuit_and_operand_results_are_not_c_locals(abb_leaves_native_review):
 rows=abb_leaves_native_review['rows']
 assert any('segundo operando no evaluado' in r['step']['pedagogy']['condition']['substituted'] for r in rows if r['native']['phase']=='condition')
 assert any(r['native']['phase']=='operand_left' for r in rows) and any(r['native']['phase']=='operand_right' for r in rows)
 for r in rows:
  if r['native']['phase'].startswith('operand_'):
   expression=r['step']['pedagogy']['memory_state']['tree_frames'][-1]['expression'];assert expression[r['native']['phase'][8:]]==r['native']['result']
   assert 'no variables C' in r['step']['pedagogy']['narration']['basic'] or 'no se declaran locales C' in r['step']['pedagogy']['narration']['basic']
