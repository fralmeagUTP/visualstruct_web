"""Independent retained C observations and statement-lifetime checks."""
import json
from pathlib import Path
from tests.test_hash_listings_baseline_low import setup
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-listings-instructions-medium'

def test_C_observer_writes_counters_guards_and_types():
 rows=json.loads((E/'native-observer-report.json').read_text(encoding='utf-8'))
 assert len(rows)==39 and sum(r['matched_native_events'] for r in rows)==352
 assert sum(r['matched_full_instruction_events'] for r in rows)==2953
 assert all(r['final_bytes_match'] and r['allocations']==r['frees']==0 for r in rows)
 assert 'default:0)' in (E/'native-observer/observer.c').read_text(encoding='utf-8')

def test_scoped_formatter_storage_aliases_and_no_kernel_console(client):
 setup(client,'mixed')
 for op in ('keys','values','items'):
  d=client.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json();f=d['execution_trace']['steps']
  assert f[0]['debug']['buffer']['bytes']==[] and f[0]['debug']['buffer']['initialized_prefix']==0
  assert f[0]['debug']['call_stack']==['caller']
  assert all(not x['console'] for x in f)
  for x in f:
   v=x['debug']['variables'];stack=x['debug']['call_stack']
   assert all(n.split('.',1)[0] in stack for n in v)
   if x['event_type']=='formatter_entry':assert v['th_formatear.tabla']['type']=='const TablaHash *'
   if x['event_type']=='append_entry':
    assert v['th_append_text.usado']['type']=='size_t *' and v['th_append_text.usado']['value']=='&th_formatear.usado'
   if x['event_type']=='written_declared':assert v['th_append_text.escritos']['initialized'] is False
   if x['event_type']=='va_start':assert v['th_append_text.args']['initialized']
   if x['event_type']=='va_end':assert v['th_append_text.args']['initialized'] is False
   assert not x['debug']['buffer']['uninitialized_bytes_read']
  assert f[-1]['debug']['call_stack']==['caller'] and f[-1]['debug']['buffer']['alive']
  assert all(x['state_after']['buckets']==f[0]['state_after']['buckets'] and x['state_after']['metadata']==f[0]['state_after']['metadata'] for x in f)
  assert f[-1]['state_after']['last_operation']['name']==op
  assert all(x['pedagogy']['listing']['same_representation'] is False for x in f)

def test_actual_caller_projects_computed_C_values_and_repeated_calls(client):
 setup(client,'mixed')
 for op in ['keys','values','items']*2:client.post('/hash/hash_table/operate',json={'operation':op,'payload':{}})
 main=client.get('/help/source/hash_table/main').data.decode()
 assert main.count('th_formatear(')==6
 assert main.count('for (const THNodo *node =')==6
 assert 'node->clave, node->valor' in main and 'node->valor);' in main
 assert main.count('cleanup:')==1
