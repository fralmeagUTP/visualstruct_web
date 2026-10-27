"""Finite stats parity and unsuppressed instruction/caller regressions."""
from pathlib import Path
import json,pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-stats-baseline-low'
from scripts.published_test_inputs import audit_input_path
def fixture(client,case):
 row=next(x for x in json.loads((audit_input_path(E/'report.json')).read_text(encoding='utf-8')) if x['case']==case)
 client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':row['created_capacity']}})
 for k,v in row['pairs']:client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 if case=='destroyed':client.post('/hash/hash_table/operate',json={'operation':'destroy_table','payload':{}})
 return row
@pytest.mark.parametrize('case',['empty','collision','sparse','destroyed'])
def test_stats_integer_fields_match_native_C_and_API_projection(client,case):
 row=fixture(client,case);d=client.post('/hash/hash_table/operate',json={'operation':'stats','payload':{}}).get_json();n=row['native'];assert d['result']['capacity']==n['capacity'] and d['result']['size']==n['size'];state=d['execution_trace']['final_state'];assert state['metadata']['collisions']==n['collisions'] and state['metadata']['occupied_buckets']==n['occupied']
def test_stats_retained_C_buffer_prefixes_and_guard_observations():
 rows=json.loads((audit_input_path(E/'buffer-report.json')).read_text(encoding='utf-8'));assert len(rows)==27
 for case in range(4):
  full=bytes.fromhex(next(x['hex'] for x in rows if x['case']==case and x['buffer_capacity']==512)).split(b'\0',1)[0]
  for x in [r for r in rows if r['case']==case]:
   if x['buffer_capacity']:assert bytes.fromhex(x['hex']).split(b'\0',1)[0]==full[:x['buffer_capacity']-1]
   else:assert x['first_byte']==165
 assert next(x for x in rows if x['null_dest'])['first_byte']==165

def test_stats_actual_function_and_formatter_definitions_present(client):
 fixture(client,'collision');s=client.post('/hash/hash_table/operate',json={'operation':'stats','payload':{}}).get_json()['execution_trace']['source_code'];assert 'THEstadisticas th_estadisticas(' in s;assert 'void th_formatear_estadisticas(' in s

def test_stats_zero_initialized_struct_float_fields_and_scopes_present(client):
 fixture(client,'collision');f=client.post('/hash/hash_table/operate',json={'operation':'stats','payload':{}}).get_json()['execution_trace']['steps'];assert any(x.get('debug',{}).get('scopes') for x in f);assert any(v['type']=='THEstadisticas' for x in f for v in x['pedagogy']['memory'].get('variables',{}).values())

def test_stats_repeated_queries_survive_in_actual_C_caller(client):
 fixture(client,'collision')
 for _ in range(2):client.post('/hash/hash_table/operate',json={'operation':'stats','payload':{}})
 main=client.get('/help/source/hash_table/main').data;assert main.count(b'th_estadisticas(')==2 and main.count(b'th_formatear_estadisticas(')==2
 client.get('/hash/hash_table');assert client.get('/help/source/hash_table/main').data==main
