"""Clear: native live allocations, historical identities, scopes and real caller."""
from pathlib import Path
import os,sys,json,shutil,subprocess
import pytest
from test_audit_abb_insert_native import identities
SUFFIX=' [valor indeterminado; identidad historica]'

@pytest.fixture(scope='module')
def abb_clear_native_review(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: clear unverified')
 output=tmp_path_factory.mktemp('abb-clear-native');root=Path(__file__).resolve().parents[1]
 env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_ROOT':str(output),'AUDIT_ABB_OPERATION':'limpiar','AUDIT_ABB_CLEAR_SKEW_CASES':'1','PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_abb_native_observer.py'))],env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0,run.stdout+run.stderr
 review=json.loads((output/'review.json').read_text(encoding='utf-8'));assert len(review['cases'])==5 and review['native_events']==201 and len(review['rows'])==191;return review

def clear_events(review,case):
 return [{**x['native'],'source_line':x['source_line']} for x in review['rows'] if x['native']['case']==case]+review['cases'][case]['caller_observations']

def clear_matches(trace,events):
 used=set();matches=[]
 for e in events:
  if e['phase']=='caller':step=next(s for s in trace['steps'] if s['pedagogy']['instruction_event']['phase']=='caller_assign')
  elif e['phase']=='clear_caller_resume':step=next(s for s in trace['steps'] if s['pedagogy']['instruction_event']['phase']=='caller_resume')
  else:
   phase='free' if e['phase']=='after' and e['source_line']=='free(nodo);' else 'resume' if e['phase']=='after' else e['phase']
   candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==phase];assert candidates,e;step=candidates[0];used.add(step['step_index'])
  matches.append((e,step))
 return matches

def native_reference(value,mapping,live):
 if value==0:return 'NULL'
 if value<=-101:return mapping[-100-value]+SUFFIX
 return mapping[value]+('' if value in live else SUFFIX)

@pytest.mark.parametrize('case',range(5))
def test_clear_every_native_instruction_live_heap_scopes_void_return_and_root(abb_clear_native_review,case):
 review=abb_clear_native_review;meta=review['cases'][case];trace=meta['trace'];events=clear_events(review,case);mapping=identities(events);assert meta['api_success'] and meta['final_tree_same']
 assert len(trace['steps'])==len(events)+2
 all_ids=set(mapping.values())-{'NULL'};freed=set();freed_order=[]
 for e,step in clear_matches(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if e['phase']=='return' else ped['memory_state'];live={n['id'] for n in e['nodes']};ref=lambda n:native_reference(n,mapping,live)
  assert state['head']==ref(e['root'])
  live_nodes={n['id']:n for n in e['nodes']}
  def project(identity):
   if identity not in live_nodes:return None
   n=live_nodes[identity];return {'value':n['value'],'left':project(n['left']),'right':project(n['right'])}
  assert state['root']==project(e['root']) and state['live_visual_projection']
  def projected_height(n):return 0 if n is None else 1+max(projected_height(n['left']),projected_height(n['right']))
  def projected_traversal(n,order):
   if n is None:return []
   left,right=projected_traversal(n['left'],order),projected_traversal(n['right'],order)
   return [n['value']]+left+right if order=='preorden' else left+right+[n['value']] if order=='postorden' else left+[n['value']]+right
  assert state['empty']==(project(e['root']) is None) and state['height']==projected_height(project(e['root']))
  assert state['traversals']=={order:projected_traversal(project(e['root']),order) for order in ['inorden','preorden','postorden']}

  initial_values={mapping[n['id']]:n['value'] for n in events[0]['nodes']}
  assert all(n['value']==initial_values[n['id']] and n['contents_are_historical'] for n in state['freed_nodes'])
  if e['frames']:assert ped['instruction_event']['frame_id']==state['tree_frames'][-1]['id']

  assert sorted(state['heap_nodes'],key=lambda n:n['id'])==sorted([{'id':mapping[n['id']],'value':n['value'],'left':ref(n['left']),'right':ref(n['right']),'status':'linked'} for n in e['nodes']],key=lambda n:n['id'])
  assert len(state['tree_frames'])==len(e['frames']) and len({f['id'] for f in state['tree_frames']})==len(e['frames'])
  for depth,(f,n) in enumerate(zip(state['tree_frames'],e['frames'])):assert f['function']==n['function']=='abb_liberarArbol' and f['depth']==depth and f['parameters']=={'nodo':ref(n['nodo'])} and f['locals']=={}
  assert state['console_stdout']==bytes.fromhex(e['console_hex']).decode()=='' and not step['console']
  assert not ped['memory']['allocated_objects'] and not ped['return_propagation']['reconnects_subtree']
  assert ped['invariant']['name']=='Vida de reservas y referencias'
  assert ped['call_stack'][0]['function']=='main' and ped['call_stack'][0]['local_root_address']==ped['memory_state']['head']
  assert ped['call_stack'][0]['locals']=={'arbol':ped['memory_state']['head']}

  assert all(x['usable'] is False and x['historical_identity'] for x in ped['memory']['unusable_reference_records'])
  expected_records=[]
  if e['root']<=-101:expected_records.append(('caller','arbol',mapping[-100-e['root']]))
  reference_frames=e['frames'][:-1] if e['phase']=='return' else e['frames']
  for n in reference_frames:
   if n['nodo']<=-101:expected_records.append(('parameter','nodo',mapping[-100-n['nodo']]))
  for n in e['nodes']:
   for side in ['left','right']:
    if n[side]>0 and n[side] not in live:expected_records.append(('field',side,mapping[n[side]]))
  assert sorted((x['kind'],x['name'],x['identity']) for x in ped['memory']['unusable_reference_records'])==sorted(expected_records)

  assert {n['id'] for n in state['freed_nodes']}==all_ids-{mapping[n] for n in live}
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='after' and e['source_line']=='free(nodo);':
   newly=all_ids-{mapping[n] for n in live}-freed;assert len(newly)==1
   freed.update(newly);freed_order+=list(newly);assert [n['id'] for n in ped['memory']['freed_objects']]==list(newly)
   assert ped['memory']['event']=='free' and SUFFIX in state['tree_frames'][-1]['parameters']['nodo']
  else:assert ped['memory']['freed_objects']==[]
  if e['phase']=='return':assert ped['call_stack'][-1]['return']=='void' and ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and len(ped['memory_state']['tree_frames'])==len(e['frames'])-1
  if e['phase']=='clear_caller_resume':
   assert not state['tree_frames'] and not state['heap_nodes'] and not state['caller_root_cleared']
   assert state['head']==('NULL' if not meta['seed'] else mapping[1]+SUFFIX)
  if e['phase']=='caller':assert state['head']=='NULL' and state['caller_root_cleared'] and state['caller_frame']['locals']=={'arbol':'NULL'}
 assert [n['id'] for n in trace['steps'][-1]['pedagogy']['memory_state']['freed_nodes']]==freed_order
 assert len(freed)==len(meta['seed']);assert trace['steps'][-1]['state_after']==trace['final_state'] and not trace['steps'][-1]['pedagogy']['memory_state']['caller_frame']
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_clear_child_freed_references_are_recorded_not_assigned_null(abb_clear_native_review):
 cases=abb_clear_native_review['cases'];balanced=cases[2]['trace'];records=[s for s in balanced['steps'] if s['pedagogy']['instruction_event']['phase']=='free']
 assert len(records)==7
 assert any(any(SUFFIX in n['left'] or SUFFIX in n['right'] for n in s['pedagogy']['memory_state']['heap_nodes']) for s in records)
 for s in records:assert 'NULL' not in s['line_text'] and s['pedagogy']['memory']['records_are_not_pointer_values']
