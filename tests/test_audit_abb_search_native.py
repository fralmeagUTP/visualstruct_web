"""Search: independent native invocations, short circuit and borrowed return."""
from pathlib import Path
import os,sys,json,shutil,subprocess
import pytest
from app import create_app
from test_audit_abb_insert_native import identities

@pytest.fixture(scope='module')
def abb_search_native_review(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: search instruction fidelity unverified')
 output=tmp_path_factory.mktemp('abb-search-native');root=Path(__file__).resolve().parents[1];env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_ROOT':str(output),'AUDIT_ABB_OPERATION':'buscar','PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_abb_native_observer.py'))],env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0,run.stdout+run.stderr
 review=json.loads((output/'review.json').read_text(encoding='utf-8'));assert len(review['cases'])==5 and review['native_events']==50 and len(review['rows'])==45;return review

def search_matches(trace,events):
 used=set();matches=[]
 for e in events:
  if e['phase']=='caller':step=trace['steps'][-1]
  else:
   phase={'enter':'enter','condition':'condition','call':'call','return':'return'}[e['phase']]
   candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==phase];assert candidates,e;step=candidates[0];used.add(step['step_index'])
  matches.append((e,step))
 return matches

@pytest.mark.parametrize('case',range(5))
def test_search_native_each_scope_short_circuit_return_and_caller(abb_search_native_review,case):
 review=abb_search_native_review;meta=review['cases'][case];trace=meta['trace'];assert meta['api_success'] and meta['result_same'];events=[{**x['native'],'source_line':x['source_line']} for x in review['rows'] if x['native']['case']==case];events.append(meta['native_endpoint']);mapping=identities(events)
 assert len(trace['steps'])==len(events)+2 # equivalent caller entry, call, conversion; native endpoint maps conversion
 for e,step in search_matches(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if e['phase'] in {'condition','call','return'} else ped['memory_state'];assert state['root']==trace['final_state']['root'] and state['head']==mapping[e['root']]
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted([{'id':mapping[n['id']],'value':n['value'],'left':mapping[n['left']],'right':mapping[n['right']]} for n in e['nodes']],key=lambda n:n['id'])
  assert len(state['tree_frames'])==len(e['frames']);assert len({f['id'] for f in state['tree_frames']})==len(state['tree_frames']);assert state['console_stdout']==bytes.fromhex(e['console_hex']).decode()=='';assert not step['console']
  for depth,(frame,native) in enumerate(zip(state['tree_frames'],e['frames'])):assert frame['function']==native['function']=='abb_buscar' and frame['depth']==depth and frame['parameters']=={'nodo':mapping[native['nodo']],'valor':native['arg']} and frame['locals']=={}
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['memory']['dangling_references'];assert not ped['return_propagation']['reconnects_subtree']
  if e['phase']=='condition':
   assert ped['condition']['result']==bool(e['result'])
   if e['frames'][-1]['nodo']==0:assert 'segundo operando no evaluado' in ped['condition']['substituted']
  if e['phase']=='call':assert ped['memory_state']==step['state_snapshot'] and ped['call_stack'][-1]['return'] is None
  if e['phase']=='return':assert ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)';assert ped['call_stack'][-1]['return']==mapping[e['result']];assert ped['memory_state']['returned']==mapping[e['result']];assert len(ped['memory_state']['tree_frames'])==len(e['frames'])-1
  if e['phase']=='caller':assert state['returned']==mapping[e['result']] and state['wrapper_result']==int(e['result']!=0) and not state['caller_frame']
 assert trace['steps'][-1]['state_after']==trace['final_state'];assert not trace['steps'][0]['state_snapshot']['tree_frames'] and not trace['steps'][0]['state_snapshot']['caller_frame'] and trace['steps'][0]['state_snapshot']['wrapper_result'] is None
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

@pytest.mark.parametrize('seed,target,expected',[([],7,False),([7],7,True),([7],3,False),([10,5,15,3,7],7,True),([10,5,15,3,7],6,False)])
def test_search_wrapper_exposes_boolean_and_keeps_tree(seed,target,expected):
 from unittest.mock import patch
 from app.domain.hierarchical import tad_wrappers
 client=create_app().test_client()
 for value in seed:assert client.post('/hierarchical/abb/operate',json={'operation':'insertar','payload':{'value':value}}).json['success']
 # Request restoration inserts the saved seed and invokes duplicate searches.
 # Observe the one requested wrapper call in isolation, with the same real TAD.
 wrapper=tad_wrappers.ABB(iter(seed));original=tad_wrappers.abb_buscar
 with patch.object(tad_wrappers,'abb_buscar',wraps=original) as observed:
  assert wrapper.buscar(target) is expected
  assert observed.call_count==1 and observed.call_args.args==(wrapper._raiz,target)
 response=client.post('/hierarchical/abb/operate',json={'operation':'buscar','payload':{'value':target}})
 assert response.status_code==200 and response.json['success'] and response.json['result'] is expected
 trace=response.json['execution_trace'];assert trace['steps'][-1]['pedagogy']['memory_state']['wrapper_result']==int(expected)
 assert all(s['state_snapshot']['root']==response.json['visual_state']['root'] and s['state_after']['root']==response.json['visual_state']['root'] for s in trace['steps'])
