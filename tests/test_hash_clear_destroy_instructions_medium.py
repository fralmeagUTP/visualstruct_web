"""Independent finite C oracle and pointer/scope lifetimes; excludes retired reads."""
from pathlib import Path
import json
from app.domain.hash.clear_destroy_instruction import build_hash_clear_destroy_trace
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-hash-clear-destroy-instructions-medium'
CASES=[('empty',3,[]),('collision',3,[(1,10),(4,40),(7,70)]),('sparse',7,[(-7,70),(7,70),(14,-14),(2,2)]),('destroyed',3,[(1,1),(4,4)])]
def execute(client,op,**payload):
 d=client.post('/hash/hash_table/operate',json={'operation':op,'payload':payload}).get_json();assert d['success'];return d['execution_trace']
def setup(client,name,cap,pairs):
 execute(client,'create_table',capacity=cap)
 for k,v in pairs:execute(client,'insert',key=k,value=v)
 if name=='destroyed':execute(client,'destroy_table')
from scripts.published_test_inputs import audit_input_path
def compare(t,sid):
 native=[json.loads(line) for line in (audit_input_path(E/'native-instructions/events.jsonl')).read_text(encoding='utf-8').splitlines()];ns=[n for n in native if n['sample']==sid]
 assert [n['event'] for n in ns]==[f['debug']['token'] for f in t['steps']]
 for n,f in zip(ns,t['steps']):
  d=f['debug'];root=d['root'];arr=d['bucket_array'];live={h['id']:h for h in d['heap'] if h['alive']}
  assert (n['capacity'],n['size'],n['frees'])==(root['capacidad'],root['cantidad'],d['frees'])
  assert bool(n['root_alive'])==root['alive'] and bool(n['array_alive'])==arr['alive'] and bool(n['pointer_valid'])==root['buckets']['valid']
  assert n['condition']==(-1 if d['condition_result'] is None else int(d['condition_result']))
  assert bool(n['count_pending'])==d['count_write_pending']
  assert sorted(n['live_keys'])==sorted(h['key'] for h in live.values())
  assert len(n['slots'])==len(arr['cells'])
  for nc,mc in zip(n['slots'],arr['cells']):
   assert bool(nc['valid'])==mc['valid'];assert nc['key']==(live[mc['value']]['key'] if mc['valid'] and mc['value'] is not None else None)
  actual=d['variables'].get('th_vaciar.actual');saved=[v for k,v in d['variables'].items() if k.endswith('.siguiente')]
  if n['event'] not in ['clear_return','destroy_return']:
   assert bool(n['has_actual'])==bool(actual)
   if actual:
    assert bool(n['actual_valid'])==actual['valid']
    if actual['valid']:assert bool(n['actual_present'])==(actual['value'] is not None) and (not n['actual_present'] or n['actual_key']==live[actual['value']]['key'])
   assert bool(n['has_saved'])==bool(saved)
   if saved:assert bool(n['saved_present'])==(saved[0]['value'] is not None) and (not n['saved_present'] or n['saved_key']==live[saved[0]['value']]['key'])
  assert f['console']==[]
  for h in d['heap']:
   if not h['alive']:assert h['initialized_mask']==0 and h['fields_valid'] is False and all(h[k] is None for k in ['key','value','next']) and h['historical_fields']
 return t['steps']
def test_core_instruction_events_safe_root_heap_and_cells_match_original_C(client):
 sid=0
 for case in CASES:
  for op in ['clear','destroy_table']:
   setup(client,*case)
   for _ in range(2):compare(execute(client,op),sid);sid+=1
 assert sid==16

def test_recreation_lifetimes_match_separate_original_C_paths(client):
 sid=16
 for op in ['clear','destroy_table']:
  setup(client,*CASES[1]);compare(execute(client,op),sid);sid+=1
  if op=='destroy_table':execute(client,'create_table',capacity=5)
  execute(client,'insert',key=8,value=80);compare(execute(client,op),sid);sid+=1

def test_saved_next_lexical_scope_root_alias_and_NULL_guards(client):
 setup(client,*CASES[1]);frames=execute(client,'destroy_table')['steps']
 for f in frames:
  d=f['debug'];assert all(v['type']=='TablaHash *' and v['value']=='&tabla' for k,v in d['variables'].items() if k.endswith('.tabla'))
  saved=[(k,v) for k,v in d['variables'].items() if k.endswith('.siguiente')]
  assert all(k.split('.')[0] in [s['id'] for s in d['scopes'] if s['kind']=='block'] and v['type']=='THNodo *' and v['valid'] for k,v in saved)
  if d['token'] in ['next_saved','node_free','actual_assigned']:assert len(saved)==1
  if d['token']=='iteration_exit':assert not saved
  if d['token']=='bucket_array_free':assert d['root']['alive'] and d['root']['buckets']['valid'] is False and d['root']['capacidad']==3
  if d['token']=='root_buckets_NULL':assert d['root']['buckets']['valid'] and d['root']['buckets']['value'] is None and d['root']['capacidad']==3
  if d['token']=='clear_return':assert 'th_vaciar' not in d['call_stack'] and all(not k.startswith('th_vaciar.') for k in d['variables'])
 for null_table in [True,False]:
  for op in ['clear','destroy_table']:
   t=execute(client,op);raw=build_hash_clear_destroy_trace(operation_name=op,payload={},source_code=t['source_code'],code_title=t['code_title'],before_state=t['final_state'],after_state=t['final_state'],success=True,message='',null_table=null_table)
   compare(raw,20+(0 if null_table else 2)+(0 if op=='clear' else 1));assert len(raw['steps'])==3 and raw['steps'][-1]['debug']['variables']=={}
