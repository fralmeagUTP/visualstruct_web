"""Rojo-Negro clear: fresh native C lifetimes, historical aliases and caller NULL boundary."""
from _instruction_context_contract import context_stack
import os,sys,json,subprocess
from pathlib import Path
import pytest
SUFFIX=' [valor indeterminado; identidad historica]'

@pytest.fixture(scope='module')
def rbt_clear_native(tmp_path_factory):
 from app import create_app
 import hashlib
 root=Path(__file__).resolve().parents[1]
 cache=os.environ.get('AUDIT_RBT_CLEAR_CACHE')
 if cache:
  out=Path(cache);report=json.loads((out/'review.json').read_text(encoding='utf-8'))
  for suffix,key in [('c','downloaded_sha256'),('h','header_sha256')]:assert hashlib.sha256((root/'docs/tads_C'/('tad_rojo_negro.'+suffix)).read_bytes()).hexdigest()==report[key]
 else:
  out=tmp_path_factory.mktemp('rbt-clear-native');env={**os.environ,'AUDIT_REPO':str(root),'AUDIT_OUTPUT_DIR':str(out),'PYTHONPATH':str(root),'PYTHONIOENCODING':'utf-8'}
  run=subprocess.run([sys.executable,str(Path(__file__).with_name('_audit_rbt_clear_native_observer.py'))],cwd=root,env=env,capture_output=True,text=True,encoding='utf-8',timeout=90);assert run.returncode==0,run.stdout+run.stderr
  report=json.loads((out/'review.json').read_text(encoding='utf-8'))
 assert report['native_events']==215 and report['native_frees']==15 and report['native_fixture_invariants_verified']
 # Native observations are immutable; all product traces are obtained from current code.
 for meta in report['cases']:
  client=create_app().test_client()
  for value in meta['seed']:assert client.post('/hierarchical/red_black/operate',json={'operation':'insertar','payload':{'value':value}}).json['success']
  data=client.post('/hierarchical/red_black/operate',json={'operation':'limpiar','payload':{}}).json;assert data['success'];meta['trace']=data['execution_trace']
  data=client.post('/hierarchical/red_black/operate',json={'operation':'limpiar','payload':{}}).json;assert data['success'];meta['repeat_trace']=data['execution_trace']
 return report

def clear_matches(trace,events):
 used=set();pairs=[]
 for e in events:
  if e['phase'] in {'caller_resume','caller_assign'}:candidates=[s for s in trace['steps'] if s['pedagogy']['instruction_event']['phase']==e['phase']]
  else:candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['line_text'].strip()==e['source_line'] and s['pedagogy']['instruction_event']['phase']==e['phase']]
  assert len(candidates)>=1,e;step=candidates[0];used.add(step['step_index']);pairs.append((e,step))
 return pairs

def ref(identity,live):return 'NULL' if identity==0 else 'N'+str(identity)+('' if identity in live else SUFFIX)
def case_events(review,case):
 lines=(Path(__file__).resolve().parents[1]/'docs/tads_C/tad_rojo_negro.c').read_text(encoding='utf-8-sig').splitlines()
 return [{**e,'source_line':lines[e['line']-1].strip() if e['line'] else None} for e in review['events'] if e['case']==case]

@pytest.mark.parametrize('case',range(10))
def test_rbt_clear_native_each_lifetime_scope_and_real_NULL_assignment(rbt_clear_native,case):
 meta=rbt_clear_native['cases'][case%5];trace=meta['trace'] if case<5 else meta['repeat_trace'];events=case_events(rbt_clear_native,case)
 if case>=5:
  meta={'seed':[]};offset=events[0]['frames'][0]['invocation']-1
  events=[{**e,'records':[],'frames':[{**f,'invocation':f['invocation']-offset} for f in e['frames']]} for e in events]
 assert len(trace['steps'])==len(events)+2
 freed_order=[]
 for e,step in clear_matches(trace,events):
  ped=step['pedagogy'];state=step['state_snapshot'] if e['phase']=='return' else ped['memory_state'];records={n['id']:n for n in e['records']};live={i for i,n in records.items() if n['live']}
  assert state['head']==ref(e['root_identity'],live)
  def projection(identity):
   if identity not in live:return None
   n=records[identity];left,right=projection(n['left_identity']),projection(n['right_identity']);return {'value':n['value_before_free'],'left':left,'right':right,'color':'RED' if n['color_before_free']==ord('r') else 'BLACK'}
  assert state['root']==projection(e['root_identity']) and state['live_visual_projection']
  def height(n):return 0 if n is None else 1+max(height(n['left']),height(n['right']))
  assert state['size']==len(live) and state['empty']==(state['root'] is None) and state['height']==height(state['root'])
  expected=[{'id':'N'+str(i),'value':n['value_before_free'],'left':ref(n['left_identity'],live),'right':ref(n['right_identity'],live),'parent':ref(n['parent_identity'],live),'color':'RED' if n['color_before_free']==ord('r') else 'BLACK','status':'linked'} for i,n in records.items() if n['live']]
  assert state['heap_nodes']==expected
  assert len(state['tree_frames'])==len(e['frames'])
  for depth,(f,n) in enumerate(zip(state['tree_frames'],e['frames'])):
   assert f['id']=='F'+str(n['invocation']) and f['function']=='rbt_liberar' and f['depth']==depth and f['identity']==('NULL' if n['identity']==0 else 'N'+str(n['identity'])) and f['parameters']=={'arbol':ref(n['identity'],live)} and f['locals']=={}
   assert n['usable']==int(n['identity']==0 or n['identity'] in live)
  assert state['console_stdout']=='' and not step['console'] and not ped['memory']['allocated_objects'] and not ped['return_propagation']['reconnects_subtree']
  assert ped['memory']['records_are_not_pointer_values'] and ped['invariant']['name']=='Vida de reservas y referencias'
  expected_refs=[]
  if e['root_identity'] and e['root_identity'] not in live:expected_refs.append(('caller','arbol','N'+str(e['root_identity'])))
  active_frames=e['frames'][:-1] if e['phase']=='return' else e['frames']
  for f in active_frames:
   if f['identity'] and f['identity'] not in live:expected_refs.append(('parameter','arbol','N'+str(f['identity'])))
  for i,n in records.items():
   if i in live:
    for side,key in [('left','left_identity'),('right','right_identity'),('parent','parent_identity')]:
     if n[key] and n[key] not in live:expected_refs.append(('field',side,'N'+str(n[key])))
  actual_refs=ped['memory']['unusable_reference_records'];assert all(not x['usable'] and x['historical_identity'] for x in actual_refs);assert sorted((x['kind'],x['name'],x['identity']) for x in actual_refs)==sorted(expected_refs)
  assert {n['id'] for n in state['freed_nodes']}=={'N'+str(i) for i in records if i not in live}
  assert all(n['contents_are_historical'] and n['color']==('RED' if records[int(n['id'][1:])]['color_before_free']==ord('r') else 'BLACK') for n in state['freed_nodes'])
  if e['phase']=='free':
   freed_order.append('N'+str(e['result']));assert [n['id'] for n in ped['memory']['freed_objects']]==[freed_order[-1]] and ped['memory']['event']=='free' and SUFFIX in state['tree_frames'][-1]['parameters']['arbol']
  else:assert not ped['memory']['freed_objects']
  if e['phase']=='condition':assert ped['condition']['result']==bool(e['result'])
  if e['phase']=='return':assert context_stack(ped)[-1]['return']=='void' and context_stack(ped)[-1]['scope_status']=='terminado (contexto del retorno)' and len(ped['memory_state']['tree_frames'])==len(e['frames'])-1
  if e['phase']=='caller_resume':assert not state['heap_nodes'] and not state['tree_frames'] and not state['caller_root_cleared'] and state['head']==('N1'+SUFFIX if meta['seed'] else 'NULL')
  if e['phase']=='caller_assign':assert state['head']=='NULL' and state['caller_root_cleared'] and state['caller_frame']['locals']=={'arbol':'NULL'}
 assert [n['id'] for n in trace['steps'][-1]['pedagogy']['memory_state']['freed_nodes']]==freed_order and len(freed_order)==len(meta['seed'])
 assert not trace['steps'][-1]['pedagogy']['memory_state']['caller_frame'] and trace['steps'][-1]['state_after']==trace['final_state']
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['state_after']==b['state_snapshot']

def test_rbt_clear_no_fake_NULL_or_color_writes(rbt_clear_native):
 trace=rbt_clear_native['cases'][2]['trace'];free_steps=[s for s in trace['steps'] if s['pedagogy']['instruction_event']['phase']=='free'];assert len(free_steps)==7
 assert any(any(SUFFIX in n['left'] or SUFFIX in n['right'] for n in s['pedagogy']['memory_state']['heap_nodes']) for s in free_steps)
 for s in free_steps:assert s['line_text'].strip()=='free(arbol);' and s['pedagogy']['memory']['records_are_not_pointer_values']
 assert [s['line_text'].strip() for s in trace['steps'] if s['pedagogy']['instruction_event']['phase']=='caller_assign']==['arbol = NULL;']
