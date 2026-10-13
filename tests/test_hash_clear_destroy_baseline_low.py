"""Clear/destroy final parity and unsuppressed instruction/memory regressions."""
from pathlib import Path
import json,pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-clear-destroy-baseline-low'
def fixture(client,case):
 row=next(x for x in json.loads((E/'report.json').read_text(encoding='utf-8')) if x['case']==case)
 client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':row['created_capacity']}})
 for k,v in row['pairs']:client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':k,'value':v}})
 if case=='destroyed':client.post('/hash/hash_table/operate',json={'operation':'destroy_table','payload':{}})
 return row
@pytest.mark.parametrize('case',['empty','collision','sparse','destroyed'])
@pytest.mark.parametrize('operation',['clear','destroy_table'])
def test_terminal_roots_and_repeated_operations_match_actual_C(client,case,operation):
 fixture(client,case)
 for repeat in [1,2]:
  n=next(x['native'] for x in json.loads((E/'report.json').read_text(encoding='utf-8')) if x['case']==case and x['operation']==operation and x['repeat']==repeat);d=client.post('/hash/hash_table/operate',json={'operation':operation,'payload':{}}).get_json();state=d['execution_trace']['final_state'];assert d['success'] and state['metadata']['capacity']==n['capacity'] and state['metadata']['size']==n['size'];assert not any(b['entries'] for b in state['buckets'])
def test_actual_C_free_order_guard_repetition_and_final_ownership():
 rows=json.loads((E/'report.json').read_text(encoding='utf-8'));native=json.loads((E/'native-report.json').read_text(encoding='utf-8'))
 assert native[-1]['allocations']==native[-1]['frees']==26 and native[-1]['live']==0
 for row in rows:
  events=row['free_order'];assert len(events)==row['native']['frees_this_call']
  if row['repeat']==2 or row['case']=='destroyed':assert not events
  else:
   nodes=[x['key_before_free'] for x in events if x['kind']=='node'];expected={'empty':[],'collision':[7,4,1],'sparse':[14,7,-7,2]}[row['case']];assert nodes==expected
   if row['operation']=='destroy_table':assert events[-1]['kind']=='bucket_array'
   else:assert all(x['kind']=='node' for x in events)

def test_actual_mutable_root_scopes_and_pointer_types_present(client):
 for op in ['clear','destroy_table']:
  fixture(client,'collision');frames=client.post('/hash/hash_table/operate',json={'operation':op,'payload':{}}).get_json()['execution_trace']['steps'];assert any(f.get('debug',{}).get('scopes') for f in frames);assert any(v['type']=='TablaHash *' for f in frames for v in f['pedagogy']['memory'].get('variables',{}).values())

def test_after_free_node_fields_and_current_pointer_are_invalid_until_assignment(client):
 fixture(client,'collision');frames=client.post('/hash/hash_table/operate',json={'operation':'clear','payload':{}}).get_json()['execution_trace']['steps'];after=[f for f in frames if 'free(actual)' in f['line_text']];assert after
 for f in after:
  freed=[node for node in f['pedagogy']['memory'].get('heap',[]) if node.get('alive') is False];assert freed and all(n.get('fields_valid') is False and n.get('initialized_mask')==0 for n in freed)
  assert any(v['type']=='THNodo *' and v.get('valid') is False for v in f['pedagogy']['memory'].get('variables',{}).values())

def test_destroy_bucket_array_has_indeterminate_root_pointer_before_NULL_write(client):
 fixture(client,'collision');frames=client.post('/hash/hash_table/operate',json={'operation':'destroy_table','payload':{}}).get_json()['execution_trace']['steps'];f=next(x for x in frames if 'free(tabla->buckets)' in x['line_text']);memory=f['pedagogy']['memory'];assert memory.get('bucket_array_freed') is True;assert memory.get('root_bucket_pointer_valid') is False

@pytest.mark.parametrize('operation',['clear','destroy_table'])
def test_reinsert_or_recreate_then_clear_destroy_matches_native_C(client,operation):
 fixture(client,'collision');first=client.post('/hash/hash_table/operate',json={'operation':operation,'payload':{}}).get_json();assert first['success']
 if operation=='destroy_table':client.post('/hash/hash_table/operate',json={'operation':'create_table','payload':{'capacity':5}})
 inserted=client.post('/hash/hash_table/operate',json={'operation':'insert','payload':{'key':8,'value':80}}).get_json();assert inserted['success'];assert inserted['visual_state']['metadata']['capacity']==(3 if operation=='clear' else 5) and inserted['visual_state']['metadata']['size']==1
 row=next(x for x in json.loads((E/'recreation-report.json').read_text(encoding='utf-8')) if x['operation']==operation);n=row['native_target_records'][1];d=client.post('/hash/hash_table/operate',json={'operation':operation,'payload':{}}).get_json();assert d['visual_state']['metadata']['capacity']==n['capacity'] and d['visual_state']['metadata']['size']==0
 identity=row['native_allocation_identity'];assert (identity[1]==identity[2]) is (operation=='clear')

@pytest.mark.parametrize('operation',['clear','destroy_table'])
def test_NULL_bucket_guard_returns_before_writes_calls_and_frees(client,operation):
 fixture(client,'destroyed');d=client.post('/hash/hash_table/operate',json={'operation':operation,'payload':{}}).get_json();lines=[f['line_text'].strip() for f in d['execution_trace']['steps']]
 forbidden=['tabla->cantidad = 0;','th_vaciar(tabla);','free(tabla->buckets);','tabla->buckets = NULL;','tabla->capacidad = 0;']
 assert not any(line in forbidden for line in lines)
