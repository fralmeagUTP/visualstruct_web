"""Listing parity from retained independent C buffers plus unsuppressed fidelity/caller reds."""
from pathlib import Path
import json
import pytest
BASE=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-listings-baseline-low'
CASES={'empty':(3,[]),'mixed':(3,[(1,10),(4,40),(7,40),(0,0),(-1,-10)]),'extremes':(1,[(-2147483648,2147483647),(2147483647,-2147483648),(0,-2147483648),(1,0)]),'sparse':(7,[(-7,70),(7,70),(14,-14),(2,2)])}
def setup(client,case):
 cap,pairs=CASES[case];client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':cap}})
 for k,v in pairs:client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
from scripts.published_test_inputs import audit_input_path
@pytest.mark.parametrize('case',list(CASES))
def test_listing_C_order_projection_results_and_history(client,case):
 setup(client,case)
 for r in [r for r in json.loads((audit_input_path(BASE/'report.json')).read_text(encoding='utf-8')) if r['case']==case]:
  d=client.post('/hash/hash_table/operate',json={'operation':r['operation'],'payload':{}}).get_json()
  assert d['result']==r['expected_projection'] and d['success']
  assert len(d['history'])==1+len(CASES[case][1])

def test_actual_C_buffer_prefix_null_termination_and_outside_guard():
 rows=json.loads((audit_input_path(BASE/'buffer-report.json')).read_text(encoding='utf-8'))
 for case in range(4):
  full=next(r for r in rows if r['case']==case and r['capacity']==4096);text=bytes.fromhex(full['hex']).split(b'\0',1)[0]
  for r in [r for r in rows if r['case']==case]:
   assert r['outside_changed']==0
   if not r['capacity']:assert r['first_byte']==0xA5
   else:
    raw=bytes.fromhex(r['hex']);assert b'\0' in raw
    assert raw.split(b'\0',1)[0]==text[:r['capacity']-1]
 for r in [r for r in rows if r['null_destination']]:assert r['first_byte']==0xA5

def test_listing_C_function_and_helper_definitions_present(client):
 setup(client,'mixed')
 for op in ['keys','values','items']:
  trace=client.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()['execution_trace']
  assert 'void th_formatear(' in trace['source_code']
  assert 'void th_append_text(' in trace['source_code']

def test_listing_buffer_declaration_has_indeterminate_typed_storage(client):
 setup(client,'mixed')
 for op in ['keys','values','items']:
  frames=client.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()['execution_trace']['steps']
  declaration=next(f for f in frames if 'char buffer[2048]' in f['line_text'])
  variables=declaration['pedagogy']['memory'].get('variables',{})
  assert any(v['type']=='char[2048]' and v['initialized'] is False for v in variables.values())
  assert any(f.get('debug',{}).get('scopes') for f in frames)

def test_listing_actual_caller_preserves_all_repeat_calls_across_reload(client):
 setup(client,'mixed')
 for op in ['keys','values','items','keys','values','items']:client.post('/hash/hash_table/operate',json={'operation':op,'payload':{}})
 main=client.get('/help/source/hash_table/main').data
 assert main.count(b'th_formatear(')==6
 client.get('/hash/hash_table')
 assert client.get('/help/source/hash_table/main').data==main
