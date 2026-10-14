"""Independent remove native statement, scopes and object-lifetime conformance."""
from pathlib import Path
import json
import pytest
BASE=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-remove-instructions-medium'
PAIRS={'empty':[],'head':[(1,10),(4,40),(7,70),(10,100)],'middle':[(1,10),(4,40),(7,70),(10,100)],'tail':[(1,10),(4,40),(7,70),(10,100)],'negative':[(-1,-10),(-4,-40),(-6,-60)],'extremes':[(-2147483648,2147483647),(2147483647,-2147483648)]}
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(PAIRS))
def test_remove_each_native_event_heap_scope_and_count(client,case):
 client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
 for k,v in PAIRS[case]:client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 for fixture in [r for r in json.loads((audit_input_path(BASE/'report.json')).read_text(encoding='utf-8')) if r['case']==case]:
  data=client.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':fixture['key']}}).get_json();frames=data['execution_trace']['steps'];native=fixture['native']
  assert [f['event_type'] for f in frames]==[n['token'] for n in native]
  for i,(frame,n) in enumerate(zip(frames,native)):
   d=frame['debug'];state=frame['state_after'];assert state['metadata']['size']==n['size']
   assert [[[e['key'],e['value']] for e in b['entries']] for b in state['buckets']]==n['buckets']
   assert d['comparisons']==n['comparisons'] and d['frees']==n['frees'] and d['allocations']==0
   assert d['condition_result']==(None if n['condition']==-1 else bool(n['condition']))
   assert frame['pedagogy']['cost']['comparisons']==n['comparisons']
   assert frame['pedagogy']['cost']['hash_evaluations']==int(any(f['event_type']=='index_assigned' for f in frames[:i+1]))
   assert not frame['console'] and not frame['pedagogy']['memory']['allocation_failed']
   assert d['actual']==(None if n['actual_key'] is None else f"0xHASH-{n['actual_key']}")
   assert d['anterior']==(None if n['previous_key'] is None else f"0xHASH-{n['previous_key']}")
   for scope in d['scopes']:
    assert scope['variables']['tabla']['value']==d['root_identity']=='&tabla'
    assert scope['variables']['tabla']['type']==('TablaHash *' if scope['function']=='th_eliminar' else 'const TablaHash *')
   assert frame['pedagogy']['variables']=={**{k:v['value'] for k,v in d['variables'].items()},'tabla->capacidad':3,'tabla->cantidad':n['size'],'retorno':d['return_status']}
   array=d['bucket_array'];assert array['element_type']=='THNodo *' and array['alive']
   assert [cell['value'] for cell in array['cells']]==[None if not bucket else f'0xHASH-{bucket[0][0]}' for bucket in n['buckets']]
   if 'th_eliminar.actual' not in d['variables']:assert frame['pedagogy']['pointers']['actual']=='fuera de alcance'
   if 'th_eliminar.anterior' not in d['variables']:assert frame['pedagogy']['pointers']['anterior']=='fuera de alcance'
   if n['token']=='index_return':
    assert not any(s['function']=='th_indice' for s in d['scopes'])
    assert not d['variables']['th_eliminar.indice']['initialized']
   if n['token'] in ['bucket_link','previous_link']:
    target=next(h for h in d['heap'] if h['key']==fixture['key']);assert target['alive'] and not target['published'] and target['fields_valid']
    assert d['count_write_pending'] and d['frees']==0
   if n['token']=='node_free':
    target=next(h for h in d['heap'] if h['id']==d['retired_actual']);assert not target['alive'] and not target['fields_valid']
    assert target['key'] is target['value'] is target['next'] is None
    assert target['historical_fields']['key']==fixture['key']
    assert d['variables']['th_eliminar.actual']['valid'] is False
    assert not d['variables']['th_eliminar.actual']['initialized'] and d['variables']['th_eliminar.actual']['value'] is None
    assert target['initialized_mask']==0 and target['historical_initialized_mask']==7
    assert frame['pedagogy']['memory']['freed'][0]['address']==d['retired_actual']
    assert frame['pedagogy']['memory']['freed'][0]['historical'] and not frame['pedagogy']['memory']['freed'][0]['fields_valid']
    assert d['count_write_pending'] and frame['pedagogy']['pointers']['actual']==d['retired_actual']
    assert 'no utilizable' in frame['pedagogy']['pointers']['actual_status']
    assert frame['pedagogy']['invariant']['holds'] and frame['pedagogy']['invariant']['status']=='transient'
   if n['token']=='count_decrement':assert not d['count_write_pending']
  assert data['result']==bool(native[-1]['status'])
  assert not frames[-1]['debug']['scopes'] and not frames[-1]['debug']['variables']

def test_remove_rejected_inputs_never_call_C_or_change_history(client):
 for key in [True,'abc',1.5,2147483648,-2147483649]:
  r=client.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':key}});assert r.status_code==400;d=r.get_json()
  assert not d['history'];assert [f['event_type'] for f in d['execution_trace']['steps']]==['input_rejected']
  assert d['execution_trace']['steps'][0]['debug']['frees']==0


def test_remove_destroyed_table_guard_has_no_hash_call_or_free(client):
 client.post('/hash/hash_table/operate',json={'operation':'destroy_table','payload':{}})
 response=client.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':-2147483648}})
 assert response.status_code==200 and response.get_json()['result'] is False
 frames=response.get_json()['execution_trace']['steps']
 assert [f['event_type'] for f in frames]==['remove_entry','remove_guard','remove_return']
 assert frames[1]['debug']['condition_result'] is True
 assert all(f['debug']['frees']==f['debug']['hash_calls']==0 for f in frames)
 assert all(f['debug']['bucket_array']['alive'] is False for f in frames)
 assert not frames[-1]['debug']['scopes'] and not frames[-1]['debug']['variables']
