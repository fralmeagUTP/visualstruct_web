"""ABB traversals: independent native scopes and exact printf prefixes."""
from _instruction_context_contract import context_stack
from pathlib import Path
import os,sys,json,shutil,subprocess
import pytest
from test_audit_abb_insert_native import identities

@pytest.fixture(scope='module')
def abb_traversal_native_review(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: native traversal scope not verified')
 output=tmp_path_factory.mktemp('abb-traversal-native');root=Path(__file__).resolve().parents[1]
 env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_ROOT':str(output),'AUDIT_ABB_OPERATION':'inorden,preorden,postorden','PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_abb_native_observer.py'))],env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0,run.stdout+run.stderr
 review=json.loads((output/'review.json').read_text(encoding='utf-8'));assert len(review['cases'])==9 and review['native_events']==300
 return review

def traversal_matches(trace,events):
 used=set();matches=[]
 for event in events:
  phase=event['phase']
  if phase=='caller':step=trace['steps'][-1]
  else:
   phases={'enter':{'enter'},'condition':{'condition'},'call':{'call'},'after':{'printf','resume'},'return':{'return'}}[phase]
   found=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==event['source_line'] and s['pedagogy']['instruction_event']['phase'] in phases];assert found,event;step=found[0];used.add(step['step_index'])
  matches.append((event,step))
 return matches

@pytest.mark.parametrize('case',range(9))
def test_traversal_native_scopes_heap_and_each_printf(abb_traversal_native_review,case):
 review=abb_traversal_native_review;meta=review['cases'][case];assert meta['api_success'];trace=meta['trace']
 events=[{**row['native'],'source_line':row['source_line']} for row in review['rows'] if row['native']['case']==case];events.append(meta['native_endpoint']);mapping=identities(events)
 assert len(trace['steps'])==len(events)-1 # native caller endpoint is not an invented C instruction
 for event,step in traversal_matches(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if event['phase'] in {'return','call','condition'} else ped['memory_state']
  assert state['root']==trace['final_state']['root'] and state['head']==mapping[event['root']]
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted([{'id':mapping[n['id']],'value':n['value'],'left':mapping[n['left']],'right':mapping[n['right']]} for n in event['nodes']],key=lambda n:n['id'])
  assert state['console_stdout']==bytes.fromhex(event['console_hex']).decode('ascii')
  assert len(state['tree_frames'])==len(event['frames'])
  for depth,(frame,native) in enumerate(zip(state['tree_frames'],event['frames'])):
   assert frame['function']==native['function']=='abb_'+meta['operation'];assert frame['depth']==depth;assert frame['parameters']=={'nodo':mapping[native['nodo']]};assert frame['locals']=={}
  assert len({f['id'] for f in state['tree_frames']})==len(state['tree_frames'])
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['memory']['dangling_references']
  if event['phase']=='condition':assert ped['condition']['result']==bool(event['result'])
  if event['phase']=='return':
   assert context_stack(ped)[-1]['return']=='void';assert len(ped['memory_state']['tree_frames'])==len(event['frames'])-1;assert not ped['return_propagation']['reconnects_subtree']
  if ped['instruction_event']['phase']=='printf':assert step['console']==[str(event['nodes'][next(i for i,n in enumerate(event['nodes']) if n['id']==event['frames'][-1]['nodo'])]['value'])+' ']
  else:assert step['console']==[]
 assert trace['steps'][-1]['state_after']==trace['final_state'];assert not trace['steps'][0]['state_snapshot']['tree_frames'];assert trace['steps'][0]['state_snapshot']['console_stdout']==''
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']
 assert ''.join(fragment for s in trace['steps'] for fragment in s['console'])==bytes.fromhex(meta['native_endpoint']['console_hex']).decode('ascii')
