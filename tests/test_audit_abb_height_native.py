"""Height instruction scopes observed independently in copies of HTTP C/H."""
from pathlib import Path
import os,sys,json,shutil,subprocess
import pytest
from test_audit_abb_insert_native import identities

@pytest.fixture(scope='module')
def abb_height_native_review(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: height remains unverified')
 output=tmp_path_factory.mktemp('abb-height-native');root=Path(__file__).resolve().parents[1]
 env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_ROOT':str(output),'AUDIT_ABB_OPERATION':'altura','AUDIT_ABB_HEIGHT_LEFT_CASE':'1','PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_abb_native_observer.py'))],env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0,run.stdout+run.stderr
 review=json.loads((output/'review.json').read_text(encoding='utf-8'));assert len(review['cases'])==5 and review['native_events']==196 and len(review['rows'])==191;return review

def height_matches(trace,events):
 used=set();matches=[]
 for e in events:
  if e['phase']=='caller':step=trace['steps'][-1]
  else:
   phase={'after':'assignment','enter':'enter','condition':'condition','call':'call','return':'return'}[e['phase']]
   candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==phase];assert candidates,e
   step=candidates[0];used.add(step['step_index'])
  matches.append((e,step))
 return matches

@pytest.mark.parametrize('case',range(5))
def test_height_every_native_instruction_heap_scope_local_and_return(abb_height_native_review,case):
 review=abb_height_native_review;meta=review['cases'][case];trace=meta['trace'];assert meta['api_success'] and meta['result_same'] and meta['final_tree_same']
 events=[{**x['native'],'source_line':x['source_line']} for x in review['rows'] if x['native']['case']==case];events.append(meta['native_endpoint']);mapping=identities(events)
 assert len(trace['steps'])==len(events)+2
 for e,step in height_matches(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if e['phase']=='return' else ped['memory_state']
  assert state['root']==trace['final_state']['root'] and state['head']==mapping[e['root']]
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted([{'id':mapping[n['id']],'value':n['value'],'left':mapping[n['left']],'right':mapping[n['right']]} for n in e['nodes']],key=lambda n:n['id'])
  assert len(state['tree_frames'])==len(e['frames']) and len({f['id'] for f in state['tree_frames']})==len(e['frames'])
  for depth,(f,n) in enumerate(zip(state['tree_frames'],e['frames'])):
   assert f['function']==n['function']=='abb_altura' and f['depth']==depth and f['parameters']=={'nodo':mapping[n['nodo']]}
   expected={name:('sin inicializar' if flag==1 else value) for name,(flag,value) in zip(['altIzq','altDer'],n['height_locals']) if flag}
   assert f['locals']==expected
  assert state['console_stdout']==bytes.fromhex(e['console_hex']).decode()=='' and not step['console']
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['memory']['dangling_references'] and not ped['return_propagation']['reconnects_subtree']
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='return':
   assert ped['call_stack'][-1]['scope_status']=='terminado (contexto del retorno)' and ped['call_stack'][-1]['return']==e['result']
   assert len(ped['memory_state']['tree_frames'])==len(e['frames'])-1 and ped['memory_state']['returned']==e['result']
  if e['phase']=='call':assert state['tree_frames'][-1]['locals'][('altIzq' if 'altIzq' in e['source_line'] else 'altDer')]=='sin inicializar'
  if e['phase']=='caller':assert state['wrapper_result']==e['result'] and not state['caller_frame']
 assert trace['steps'][-1]['state_after']==trace['final_state']
 assert not trace['steps'][0]['state_snapshot']['tree_frames'] and trace['steps'][0]['state_snapshot']['wrapper_result'] is None
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_height_native_comparison_true_false_and_tie(abb_height_native_review):
 rows=[r for r in abb_height_native_review['rows'] if r['native']['phase']=='condition' and 'altIzq > altDer' in r['source_line']]
 assert any(r['native']['result']==1 for r in rows) and any(r['native']['result']==0 for r in rows)
 assert any(r['native']['frames'][-1]['height_locals'][0][1]==r['native']['frames'][-1]['height_locals'][1][1] for r in rows)
 for r in rows:
  n=r['native']['frames'][-1]['height_locals'];assert all(x[0]==2 for x in n)
  assert r['step']['pedagogy']['executed_branch']==('altIzq' if r['native']['result'] else 'altDer')
