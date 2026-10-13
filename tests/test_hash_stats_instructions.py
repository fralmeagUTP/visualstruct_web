"""Independent C-value evidence and separate copies/scopes for stats."""
from pathlib import Path
import json
from tests.test_hash_stats_baseline_low import fixture
from app.domain.hash.stats_instruction import cfloat
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-stats-instructions-medium'

def test_native_C_sequences_conditions_structs_and_rounding_preserved():
 rows=json.loads((E/'native-observer-report.json').read_text(encoding='utf-8'));assert len(rows)==27
 assert all(x['final_bytes_match'] and not x['allocations'] and not x['frees'] for x in rows)
 assert sum(x['matched_C_events'] for x in rows)==1658 and sum(x['matched_C_conditions'] for x in rows)==542
 assert sum(x['matched_C_struct_snapshots'] for x in rows)==1424
 probes=json.loads((E/'native-rounding-probes.json').read_text(encoding='utf-8'));assert len(probes)==4
 for p in probes:assert p['result']==cfloat(cfloat(p['n'])/cfloat(p['d']))
 assert any(p['cast_n']!=p['n'] for p in probes)

def test_C_float_struct_copies_lifetimes_and_API_semantics_remain_distinct(client):
 for case in ['empty','collision','sparse','destroyed']:
  row=fixture(client,case);d=client.post('/hash/hash_table/operate',json={'operation':'stats','payload':{}}).get_json();frames=d['execution_trace']['steps'];assert d['result']==row['data']['result'];n=row['native'];expected={name:n[key] for name,key in [('capacidad','capacity'),('cantidad','size'),('buckets_ocupados','occupied'),('colisiones','collisions'),('factor_carga','C_float_load')]}
  assert frames[0]['debug']['variables']['caller.stats']['initialized'] is False
  entries=[f for f in frames if f['event_type']=='stats_entry'];assert len(entries)==(1 if case=='destroyed' else 2)
  ids=[]
  for f in frames:
   v=f['debug']['variables'];stack=f['debug']['call_stack'];assert all(name.split('.',1)[0] in stack for name in v)
   assert not f['console'] and not f['debug']['allocations'] and not f['debug']['frees']
   if f['event_type']=='stats_zero_initialized':
    st=v['th_estadisticas.stats'];assert st['initialized_mask']==31 and all(x['initialized'] and x['value']==0 for x in st['fields'].values());assert st['fields']['factor_carga']['type']=='float';ids.append(st['storage_id'])
   if f['event_type']=='stats_return':assert 'th_estadisticas' not in stack and f['debug']['returned_stats']==expected
   if f['event_type']=='caller_stats_assigned':assert v['caller.stats']['value']==expected
   if f['event_type']=='formatter_stats_assigned':assert v['th_formatear_estadisticas.stats']['value']==v['caller.stats']['value'] and v['th_formatear_estadisticas.stats']['storage_id']!=v['caller.stats']['storage_id']
   if f['event_type']=='buffer_declared':assert v['caller.texto']['initialized_prefix']==0 and v['caller.texto']['type']=='char[512]'
   if f['debug']['buffer']:assert f['debug']['buffer']['uninitialized_bytes_read'] is False
   assert f['pedagogy']['stats_representation']['API_semantics_changed'] is False
  assert len(set(ids))==len(ids) and frames[-1]['debug']['call_stack']==['caller']
  assert frames[-1]['debug']['nodes_visited']==(0 if case=='destroyed' else 2*n['size'])
  assert all(f['state_after']['buckets']==frames[0]['state_after']['buckets'] for f in frames)
  assert frames[-1]['debug']['representation']['API_double_load']==d['result']['load_factor']

def test_actual_stats_caller_preserves_two_distinct_computed_representations(client):
 fixture(client,'collision')
 for _ in range(2):client.post('/hash/hash_table/operate',json={'operation':'stats','payload':{}})
 main=client.get('/help/source/hash_table/main').data.decode();assert main.count('th_estadisticas(')==2 and main.count('th_formatear_estadisticas(')==2
 assert main.count('stats-C:')==2 and main.count('stats-API-projection:')==2 and main.count('cleanup:')==1
 assert '(double)tabla.cantidad / (double)tabla.capacidad' in main
 client.get('/hash/hash_table');assert client.get('/help/source/hash_table/main').data.decode()==main
