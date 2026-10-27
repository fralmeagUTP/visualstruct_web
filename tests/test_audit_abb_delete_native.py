"""Compare native events, occurrence/phase/physical line, aliases and live heap."""
from _instruction_context_contract import context_stack
import json,os,re,sys
from pathlib import Path
import pytest
from app import create_app
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.abb_delete_instruction import build_abb_delete_trace
W=Path(os.environ.get('AUDIT_DELETE_BASELINE_ROOT',str(Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-abb-delete-baseline-low')))

from scripts.published_test_inputs import audit_input_path
@pytest.fixture(scope='session')
def delete_baselines():
 return [json.loads((audit_input_path(W/folder/'review.json')).read_text(encoding='utf-8')) for folder in ['abb-delete-native-low','abb-delete-root-one-native-low']]

def delete_case(review,case):
 meta=review['cases'][case];client=create_app().test_client()
 for v in meta['seed']:assert client.post('/hierarchical/abb/operate',json={'operation':'insertar','payload':{'value':v}}).json['success']
 data=client.post('/hierarchical/abb/operate',json={'operation':'eliminar','payload':meta['payload']}).json
 assert data['success']==meta['api_success']
 if not data['success']:
  state=data['execution_trace']['final_state'];trace={**data['execution_trace'],'success':True,'source_code':CCodeService.get_structure_data('abb')['operations']['eliminar']}
  return build_abb_delete_trace(trace,state,state)
 return data['execution_trace']

def events_for(review,case):return [{**r['native'],'source_line':r['source_line']} for r in review['rows'] if r['native']['case']==case]+[review['cases'][case]['native_endpoint']]

def id_mapping(events):
 nodes={n['id']:n for n in events[0]['nodes']};mapping={0:'NULL'}
 def walk(i):
  if not i:return
  mapping[i]='N'+str(len(mapping));n=nodes[i];walk(n['left']);walk(n['right'])
 walk(events[0]['root']);return mapping

def matches(trace,events):
 used=set();out=[]
 for e in events:
  phases={'enter':['enter'],'condition':['condition'],'call':['call'],'after':['assignment','free','link'],'return':['return'],'caller':['caller']}[e['phase']]
  fn=e['frames'][-1]['function'] if e['frames'] else 'main'
  candidates=[s for s in trace['steps'] if s['step_index'] not in used and s['pedagogy']['instruction_event']['phase'] in phases and s['pedagogy']['instruction_event']['function']==fn and (e['phase']=='caller' or s['line_text'].strip()==e['source_line'])]
  assert candidates,(e,[(s['line_text'],s['pedagogy']['instruction_event']) for s in trace['steps']])
  step=candidates[0];used.add(step['step_index']);out.append((e,step))
 return out

@pytest.mark.parametrize('family,case',[(0,i) for i in range(11)]+[(1,i) for i in range(2)])
def test_delete_native_instructions_heap_frames_and_caller(delete_baselines,family,case):
 review=delete_baselines[family];meta=review['cases'][case];trace=delete_case(review,case);events=events_for(review,case);mapping=id_mapping(events);pairing=matches(trace,events)
 raw=(audit_input_path(W/('abb-delete-native-low' if family==0 else 'abb-delete-root-one-native-low')/'tad_abb.c')).read_text(encoding='utf-8-sig').splitlines()
 for e,s in pairing:
  phase=e['phase'];state=s['state_snapshot'] if phase in ['condition','call','return'] else s['pedagogy']['memory_state'];ped=s['pedagogy'];live={n['id'] for n in e['nodes']}
  def ref(i):
   if i==-2:return 'sin inicializar'
   if i<=-100:i=-100-i
   name=mapping[i]
   return name if i==0 or i in live else name+' [valor indeterminado; identidad historica]'
  assert state['head']==ref(e['root'])
  native_nodes={n['id']:n for n in e['nodes']}
  def projection(identity):
   if identity not in live:return None
   n=native_nodes[identity];return {'value':n['value'],'left':projection(n['left']),'right':projection(n['right'])}
  root=projection(e['root']);assert state['root']==root and state['empty']==(root is None)
  def values(n):return [] if n is None else [n['value'],*values(n['left']),*values(n['right'])]
  def height(n):return 0 if n is None else 1+max(height(n['left']),height(n['right']))
  assert state['size']==len(values(root)) and state['reserved_count']==len(live) and state['height']==height(root)
  expected=[{'id':mapping[n['id']],'value':n['value'],'left':ref(n['left']),'right':ref(n['right'])} for n in e['nodes']]
  assert [{k:n[k] for k in ['id','value','left','right']} for n in state['heap_nodes']]==sorted(expected,key=lambda n:int(n['id'][1:])),(e,state)
  assert len(state['tree_frames'])==len(e['frames'])
  for a,b in zip(state['tree_frames'],e['frames']):
   assert a['function']==b['function'] and a['parameters']['nodo']==ref(b['nodo'])
   if b['function']=='abb_eliminar':assert a['parameters']['valor']==b['arg']
   if b['temp']!=-2:assert a['locals']['temp']==ref(b['temp'])
   else:assert a['locals'].get('temp','sin inicializar')=='sin inicializar'
  if phase=='condition':assert s['condition_result']==bool(e['result']) and ped['condition']['result']==bool(e['result'])
  if phase=='return':assert ped['instruction_event']['return']==ref(e['result']) and context_stack(ped)[-1]['scope_status']=='terminado (contexto del retorno)'
  if phase in ['enter','return']:assert ped['instruction_event']['frame_id']==(state['tree_frames'][-1]['id'])
  if e['line']:
   fn=e['frames'][-1]['function'];original_start=next(i for i,l in enumerate(raw) if l.strip().startswith('ABBNodo* '+fn+'('));display_start=next(i for i,l in enumerate(trace['source_code'].splitlines()) if l.strip().startswith('ABBNodo* '+fn+'('));assert s['line_index']==display_start+e['line']-1-original_start
  assert state['console_stdout']=='' and not ped['memory']['allocated_objects']
  assert not ped['memory']['dangling_references'] and all(x['historical_identity'] and not x['usable'] for x in ped['memory']['unusable_reference_records'])
  expected_records=[]
  if e['root']<=-101:expected_records.append(('caller','arbol',mapping[-100-e['root']]))
  remaining=e['frames'][:-1] if phase=='return' else e['frames']
  for f in remaining:
   for name in ['nodo','temp']:
    if f[name]<=-101:expected_records.append(('parameter' if name=='nodo' else 'local',name,mapping[-100-f[name]]))
  for n in e['nodes']:
   for side in ['left','right']:
    if n[side]>0 and n[side] not in live:expected_records.append(('field',side,mapping[n[side]]))
  assert sorted((x['kind'],x['name'],x['identity']) for x in ped['memory']['unusable_reference_records'])==sorted(expected_records)
  assert {n['id'] for n in state['freed_nodes']}==set(mapping.values())-{'NULL'}-{mapping[i] for i in live}
  if ped['instruction_event']['phase']=='free':assert len(ped['memory']['freed_objects'])==1
 for a,b in zip(trace['steps'],trace['steps'][1:]):assert a['pedagogy']['memory_state']==b['state_snapshot']
 assert trace['steps'][-1]['state_after']['root']==meta['trace']['final_state']['root']
 assert len(trace['steps'][-1]['pedagogy']['memory_state']['freed_nodes'])==int(meta['api_success'])

def test_delete_baseline_downloads_still_match_current_http(delete_baselines):
 client=create_app().test_client()
 for kind,suffix in [('source','c'),('header','h')]:
  response=client.get('/help/source/abb/'+kind);assert response.status_code==200
  assert response.data==(audit_input_path(W/'abb-delete-native-low'/('tad_abb.'+suffix))).read_bytes()

def test_delete_future_successor_stays_alive_until_its_free(delete_baselines):
 trace=delete_case(delete_baselines[0],8);steps=trace['steps'];call=next(s for s in steps if s['line_text'].strip()=='nodo->derecho = abb_eliminar(nodo->derecho, temp->valor);' and s['pedagogy']['instruction_event']['phase']=='call');child=steps[call['step_index']+1]
 assert child['state_snapshot']['root']['right']['left']['left']['value']==12
 copy=next(s for s in steps if s['line_text'].strip()=='nodo->valor = temp->valor;');assert copy['state_after']['heap_nodes'][0]['id']=='N1' and copy['state_after']['heap_nodes'][0]['value']==12
 assert len(copy['state_after']['heap_nodes'])==8 and copy['state_after']['validation'] is None
