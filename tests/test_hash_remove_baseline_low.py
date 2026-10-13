"""Retained native remove endpoint parity and three unsuppressed instruction regressions."""
from pathlib import Path
import json
import pytest
BASE=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-remove-baseline-low'
PAIRS={'empty':[],'head':[(1,10),(4,40),(7,70),(10,100)],'middle':[(1,10),(4,40),(7,70),(10,100)],'tail':[(1,10),(4,40),(7,70),(10,100)],'negative':[(-1,-10),(-4,-40),(-6,-60)],'extremes':[(-2147483648,2147483647),(2147483647,-2147483648)]}
def setup(client,name):
 client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':3}})
 for key,value in PAIRS[name]:client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':key,'value':value}})
@pytest.mark.parametrize('case',list(PAIRS))
def test_remove_retained_native_results_and_bucket_order(client,case):
 setup(client,case)
 for row in [r for r in json.loads((BASE/'report.json').read_text(encoding='utf-8')) if r['case']==case]:
  response=client.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':row['key']}});data=response.get_json();last=row['native'][-1]
  assert response.status_code==200 and data['success']
  assert data['result']==bool(last['status'])
  assert [[[e['key'],e['value']] for e in b['entries']] for b in data['visual_state']['buckets']]==last['buckets']
  assert data['visual_state']['metadata']['size']==last['size'] and data['visual_state']['metadata']['capacity']==3

def test_remove_no_future_mutation_and_count_waits_for_decrement(client):
 setup(client,'middle');d=client.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':7}}).get_json();frames=d['execution_trace']['steps']
 boundary=next(i for i,f in enumerate(frames) if 'anterior->siguiente = actual->siguiente;' in f['line_text'])
 for f in frames[:boundary]:
  assert f['state_after']['metadata']['size']==4
  assert [e['key'] for b in f['state_after']['buckets'] for e in b['entries']]==[10,7,4,1]
 freed=next(f for f in frames if 'free(actual);' in f['line_text'])
 assert freed['state_after']['metadata']['size']==4
 assert [e['key'] for b in freed['state_after']['buckets'] for e in b['entries']]==[10,4,1]

 # Entry must not anticipate the final comparison count, hash call or return.
 assert frames[0]['pedagogy']['cost']['comparisons']==0
 assert frames[0]['pedagogy']['cost']['hash_evaluations']==0
 assert frames[0]['pedagogy']['variables'].get('retorno') is None

def test_remove_typed_scopes_and_aliases_exist(client):
 setup(client,'middle');d=client.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':7}}).get_json();frames=d['execution_trace']['steps']
 assert all('debug' in f and 'scopes' in f['debug'] for f in frames)
 scopes=[s for f in frames for s in f['debug']['scopes']]
 assert any(s['function']=='th_eliminar' and s['variables']['tabla']['type']=='TablaHash *' for s in scopes)
 assert any(s['function']=='th_indice' and s['variables']['tabla']['type']=='const TablaHash *' for s in scopes)

def test_remove_negative_zero_residue_does_not_normalize(client):
 setup(client,'negative');d=client.post('/hash/hash_table/operate',json={'operation':'remove','payload':{'key':-6}}).get_json()
 assert not any('indice += tabla->capacidad;' in f['line_text'] for f in d['execution_trace']['steps'])
