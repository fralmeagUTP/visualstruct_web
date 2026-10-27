"""ABB insertion: native intermediate identities, masks, invocations and returns."""
from _instruction_context_contract import context_stack
from pathlib import Path
import os,sys,json,shutil,subprocess
import pytest
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.abb_instruction import build_abb_insert_trace

@pytest.fixture(scope='module')
def abb_insert_native_review(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: ABB native instruction observations unverified')
 output=tmp_path_factory.mktemp('abb-insert-native');root=Path(__file__).resolve().parents[1];env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_ROOT':str(output),'AUDIT_ABB_OPERATION':'insertar','PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_abb_native_observer.py'))],env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0,run.stdout+run.stderr
 review=json.loads((output/'review.json').read_text(encoding='utf-8'));assert len(review['cases'])==6 and review['native_events']==109
 return review

def identities(events):
 first=events[0];nodes={n['id']:n for n in first['nodes']};mapping={0:'NULL'}
 def walk(identity):
  if not identity:return
  mapping[identity]='N'+str(len(mapping));node=nodes[identity];walk(node['left']);walk(node['right'])
 walk(first['root'])
 for e in events:
  for node in e['nodes']:
   if node['id'] not in mapping:mapping[node['id']]='N'+str(len(mapping))
 return mapping

def case_trace(review,case):
 meta=review['cases'][case]
 if meta['api_success']:return meta['trace']
 # UI rejected duplicate before calling C. Compare a direct C-contract model,
 # not a fictitious executed interface operation; UI rejection tested separately.
 root=meta['trace']['final_state'];base={**meta['trace'],'success':True,'source_code':CCodeService.get_structure_data('abb')['operations']['insertar']}
 return build_abb_insert_trace(base,root,root)

def match_events(trace,events):
 matched=[];used=set()
 for e in events:
  if e['phase']=='caller':
   step=next(s for s in trace['steps'] if s['pedagogy']['instruction_event']['phase']=='caller')
  else:
   # Match occurrence AND phase, so completion never consumes entry to a call.
   text=e['source_line'];phases={'after':{'allocation','assignment','link'},'condition':{'condition'},'enter':{'enter'},'call':{'call'},'return':{'return'}}[e['phase']]
   found=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==text and s['pedagogy']['instruction_event']['phase'] in phases];assert found,e;step=found[0]
  used.add(step['step_index']);matched.append((e,step))
 return matched

@pytest.mark.parametrize('case',range(6))
def test_abb_insert_native_each_live_node_scope_return_and_publication(abb_insert_native_review,case):
 review=abb_insert_native_review;meta=review['cases'][case];trace=case_trace(review,case)
 events=[{**row['native'],'source_line':row['source_line']} for row in review['rows'] if row['native']['case']==case]
 events.append(meta['native_endpoint']);mapping=identities(events);matches=match_events(trace,events)
 for e,step in matches:
  state=step['state_snapshot'] if e['phase'] in {'condition','call','return'} else step['pedagogy']['memory_state'];ped=step['pedagogy']
  expected=[{'id':mapping[n['id']],'value':n['value'] if n['mask']&1 else 'sin inicializar','left':mapping[n['left']] if n['mask']&2 else 'sin inicializar','right':mapping[n['right']] if n['mask']&4 else 'sin inicializar'} for n in e['nodes']]
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted(expected,key=lambda n:n['id']),(e,state)
  assert state['head']==mapping[e['root']]
  assert len(state['tree_frames'])==len(e['frames'])
  for depth,(frame,native) in enumerate(zip(state['tree_frames'],e['frames'])):
   assert frame['function']==native['function']=='abb_insertar' and frame['depth']==depth
   assert frame['parameters']=={'nodo':mapping[native['nodo']],'valor':native['arg']}
   assert len({f['id'] for f in state['tree_frames']})==len(state['tree_frames'])
   if native['nuevo']!=-2:assert frame['locals']['nuevo']==mapping[native['nuevo']]
   else:assert 'nuevo' not in frame['locals']
  assert not ped['memory']['freed_objects'] and not ped['memory']['dangling_references']
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='return':
   assert context_stack(ped)[-1]['return']==mapping[e['result']]
   assert ped['memory_state']['returned']==mapping[e['result']]
   assert len(ped['memory_state']['tree_frames'])==len(e['frames'])-1
  if 'malloc' in e.get('source_line',''):
   assert ped['concept']=='allocation' and len(ped['memory']['allocated_objects'])==1
   allocated=ped['memory']['allocated_objects'][0];assert allocated['value']==allocated['left']==allocated['right']=='sin inicializar';assert allocated['status']=='detached'
  if e.get('source_line')=='nuevo->valor = valor;':assert ped['concept']=='assignment' and not ped['memory']['allocated_objects']
  if e['phase']=='caller':assert not state['tree_frames'] and state['head']==mapping[e['result']]
 assert trace['steps'][-1]['state_after']==trace['final_state']
 assert not trace['steps'][0]['state_snapshot']['tree_frames'] and not trace['steps'][0]['state_snapshot']['caller_frame']
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_duplicate_interface_remains_rejected_with_unchanged_tree(abb_insert_native_review):
 meta=abb_insert_native_review['cases'][4];assert not meta['api_success'];assert meta['final_tree_same'];assert meta['native_endpoint']['result']==meta['native_endpoint']['root'];assert all(not s['state_after'].get('abb_insert_model') for s in meta['trace']['steps'])
