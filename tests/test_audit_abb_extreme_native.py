"""ABB minimum/maximum: actual single iterative scope and borrowed return."""
from _instruction_context_contract import context_stack
from pathlib import Path
import os,sys,json,shutil,subprocess
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.abb_extreme_instruction import build_abb_extreme_trace
from test_audit_abb_insert_native import identities

@pytest.fixture(scope='module')
def abb_extreme_native_review(tmp_path_factory):
 if not shutil.which('gcc'):pytest.skip('GCC unavailable: native extrema unverified')
 output=tmp_path_factory.mktemp('abb-extreme-native');root=Path(__file__).resolve().parents[1];env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_ROOT':str(output),'AUDIT_ABB_OPERATION':'minimo,maximo','PYTHONIOENCODING':'utf-8'}
 run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_abb_native_observer.py'))],env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0,run.stdout+run.stderr
 review=json.loads((output/'review.json').read_text(encoding='utf-8'));assert len(review['cases'])==6 and review['native_events']==34;return review

def extreme_trace(meta):
 # The wrapper calls the TAD even for NULL, then converts NULL to an API error.
 return meta['trace']

def extreme_matches(trace,events):
 used=set();matches=[]
 for e in events:
  if e['phase']=='caller':step=trace['steps'][-1]
  else:
   phase={'enter':'enter','condition':'condition','after':'assignment','return':'return'}[e['phase']]
   candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==phase];assert candidates,e;step=candidates[0];used.add(step['step_index'])
  matches.append((e,step))
 return matches

@pytest.mark.parametrize('case',range(6))
def test_extreme_native_one_scope_local_alias_and_borrowed_return(abb_extreme_native_review,case):
 review=abb_extreme_native_review;meta=review['cases'][case];trace=extreme_trace(meta);events=[{**x['native'],'source_line':x['source_line']} for x in review['rows'] if x['native']['case']==case];events.append(meta['native_endpoint']);mapping=identities(events)
 assert len(trace['steps'])==len(events)-1
 for e,step in extreme_matches(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if e['phase'] in {'condition','return'} else ped['memory_state'];assert state['root']==trace['final_state']['root'] and state['head']==mapping[e['root']]
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted([{'id':mapping[n['id']],'value':n['value'],'left':mapping[n['left']],'right':mapping[n['right']]} for n in e['nodes']],key=lambda n:n['id'])
  assert len(state['tree_frames'])==len(e['frames'])<=1;assert state['console_stdout']==bytes.fromhex(e['console_hex']).decode()=='';assert not step['console']
  if e['frames']:assert state['tree_frames'][0]=={'id':'F1','function':e['frames'][0]['function'],'depth':0,'parameters':{'nodo':mapping[e['frames'][0]['nodo']]},'locals':{}}
  assert not ped['memory']['allocated_objects'] and not ped['memory']['freed_objects'] and not ped['memory']['dangling_references']
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='return':assert context_stack(ped)[0]['return']==mapping[e['result']];assert ped['memory_state']['returned']==mapping[e['result']];assert not ped['memory_state']['tree_frames'];assert not ped['return_propagation']['reconnects_subtree']
  if e['phase']=='after':assert len(ped['memory_state']['tree_frames'])==1 and ped['memory_state']['tree_frames'][0]['id']=='F1'
 assert trace['steps'][-1]['state_after']==trace['final_state'];assert not trace['steps'][0]['state_snapshot']['tree_frames']
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

@pytest.mark.parametrize('operation',['minimo','maximo'])
def test_empty_interface_extreme_remains_rejected_without_mutation(operation):
 from unittest.mock import patch
 from app.domain.hierarchical import tad_wrappers
 symbol='abb_encontrarMinimo' if operation=='minimo' else 'abb_encontrarMaximo'
 original=getattr(tad_wrappers,symbol)
 with patch.object(tad_wrappers,symbol,wraps=original) as observed:
  client=create_app().test_client();data=client.post('/hierarchical/abb/operate',json={'operation':operation,'payload':{}})
  assert observed.call_count==1 and observed.call_args.args==(None,)
 assert data.status_code==400 and not data.json['success'];assert data.json['visual_state']['root'] is None
 trace=data.json['execution_trace'];assert len(trace['steps'])==3;assert trace['steps'][-1]['pedagogy']['memory_state']['returned']=='NULL'
 assert all(s['state_snapshot']['root'] is None and s['state_after']['root'] is None and s['pedagogy']['memory_state']['abb_read_model'] for s in trace['steps'])
