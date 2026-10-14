"""Radix MEDIUM focused gates; original 39 LOW IDs are immutable."""
import json
from pathlib import Path
import pytest
from app import create_app
from app.domain.sorting.tad_ordenamiento import SortingInterpreter
from app.domain.sorting.radix_instructions import SimulatedRadixAllocationFailure
from app.services.counting_trace_service import get_counting_store
from app.services.radix_trace_service import RadixPageSource
from app.services.sorting_structure_service import SortingStructureService
ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-instructions'

def prepare(values):
 app=create_app();app.testing=True;c=app.test_client()
 assert c.post('/api/ordenamiento/create-array',json={'values':values}).status_code==200
 assert c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'radixsort'}).status_code==200
 return app,c

def run(c):return c.post('/api/ordenamiento/run',json={'algorithm_id':'radixsort','mode':'step_by_step'})

@pytest.mark.parametrize('attempt',[1,2,3,4])
def test_radix_private_fault_returns_native_equivalent_cleanup_preserves_accepted(attempt,monkeypatch):
 app,c=prepare([-5,2]);assert run(c).status_code==200;before=c.get('/api/ordenamiento/state').get_json()
 def allocator(name,capacity,index):
  if index==attempt:raise SimulatedRadixAllocationFailure('private QA')
 app.config['RADIX_QA_ALLOCATOR']=allocator;r=run(c);assert r.status_code==400;d=r.get_json();t=d['execution_trace']
 assert not t['success'] and not t['mutates'] and t['error']['simulated'] and not t['error']['real_c_execution'] and t['native_status']==0
 assert d['history']==before['history'] and d['main_c']==before['main_c'] and d['visual_state']==before['visual_state']
 last=t['steps'][-1];assert last['debug']['instruction_event']['live']==0 and not last['pedagogy']['variables'] and not last['pedagogy']['call_stack']
 assert all(not f['debug']['console_events'] for f in t['steps'])
 def forbid(*a,**kw):raise AssertionError('navigation redispatched')
 monkeypatch.setattr(SortingInterpreter,'run',forbid)
 assert c.get('/api/ordenamiento/traces/'+t['trace_id']+'/page?start=0&limit=128').status_code==200
 assert c.post('/api/ordenamiento/step',json={'algorithm_id':'radixsort','cursor':0}).status_code==200
 model=c.get('/sorting/visualizador');assert model.status_code==200
 assert c.get('/api/ordenamiento/traces/'+t['trace_id']+'/export').get_json()['compact_trace']['success'] is False
 assert c.get('/api/ordenamiento/state').get_json()['history']==before['history']


def test_radix_fault_hook_not_request_controlled_or_active_outside_testing():
 app,c=prepare([7]);app.testing=False
 def forbidden(*a):raise AssertionError('private QA outside testing')
 app.config['RADIX_QA_ALLOCATOR']=forbidden
 assert c.post('/api/ordenamiento/run',json={'algorithm_id':'radixsort','mode':'fast','fail_at':1}).status_code==200


def test_radix_declared_scopes_previous_values_and_unsigned_aliases():
 values=[-5,2];raw=SortingInterpreter(values,'radixsort').run()['steps'];source=SortingStructureService._didactic_content('sorting_array')['operations']['radixsort'];p=RadixPageSource(raw,source)
 frames=[p.frame(i) for i in range(len(raw))];bytoken={}
 for f in frames:bytoken.setdefault(f['debug']['instruction_event']['token'],[]).append(f)
 assert {v['name'] for v in bytoken['radix_entry'][0]['pedagogy']['variables']}=={'arreglo','n'}
 assert not next(v for v in bytoken['radix_declare'][0]['pedagogy']['variables'] if v['name']=='i')['initialized']
 entry=bytoken['digit_entry'][0]['pedagogy'];assert not any(v['name']in{'conteo','salida','i'} and v['scope']=='counting_por_digito' for v in entry['variables'])
 assert entry['call_stack'][-1]['parameters']=={'arreglo':'negative','n':1,'exp':1}
 assert not any(v['name']=='digito' for v in bytoken['digit_value_read'][0]['pedagogy']['variables'])
 select=bytoken['digit_select'][0]['pedagogy']['variables'];digit=next(v for v in select if v['name']=='digito');assert digit['initialized'] and digit['previous'] is None and digit['type']=='uint32_t'
 # Genuine entered scope exits now bind their actual C closing braces.
 lines=source.replace('\r\n','\n').split('\n')
 for token in ['negative_block_exit','positive_block_exit']:
  assert len(bytoken[token])==1
  frame=bytoken[token][0];index=frame['line_index']
  assert type(index) is int and 0<=index<len(lines)
  assert frame['line_text']==lines[index] and lines[index].strip()=='}'
  assert frame['pedagogy']['source']['function']=='ordenar_radixsort'
  assert frame['pedagogy']['source']['line_index']==index
  prefix=token.removesuffix('_block_exit')
  assert bytoken[prefix+'_group_guard'][0]['pedagogy']['condition']['result'] is True
  scope='ordenar_radixsort/bloque_'+('negativos' if prefix=='negative' else 'positivos')
  previous=frames[frame['step_index']-1]
  assert {v['name'] for v in previous['pedagogy']['variables'] if v['scope']==scope}=={'maximo','exp'}
  assert not any(v['scope']==scope for v in frame['pedagogy']['variables'])
 assert all(not f['pedagogy']['variables'] or not any(v['scope'].startswith('counting_por_digito') for v in f['pedagogy']['variables']) for f in bytoken['digit_return'])
 assert all(next(v for v in f['pedagogy']['variables'] if v['name']=='maximo')['previous'] is None for token in ['negative_max_exp_init','positive_max_exp_init'] for f in bytoken[token])


from scripts.published_test_inputs import audit_input_path
def test_radix_large_paging_boundaries_concepts_export_ownership_and_no_redispatch(monkeypatch):
 app,c=prepare([-2147483648,2147483647]*40);d=run(c).get_json();t=d['execution_trace'];assert t['schema']=='counting-paged-trace/v1' and t['step_count']==11408 and 'steps' not in t
 assert t['manifest']['codec']=='radix-delta-tape/v1' and t['manifest']['retained_bytes']<64*1024*1024 and len(t['initial_page']['steps'])==16
 native=[json.loads(s) for s in (audit_input_path(E/'native-expanded/native.jsonl')).read_text(encoding='utf-8').splitlines()];native=[r for r in native if r.get('case')==40 and 'token'in r]
 def forbid(*a,**kw):raise AssertionError('saved page ran sorting')
 monkeypatch.setattr(SortingInterpreter,'run',forbid)
 with c.session_transaction() as session:owner=session['counting_owner']
 with app.app_context():source=get_counting_store().get(owner,t['trace_id'])
 for index in [0,1,127,128,129,2047,2048,5704,11407]:
  frame=c.get(t['page_url']+'?start='+str(index)+'&limit=1').get_json()['steps'][0]
  assert frame['debug']['instruction_event']=={k:v for k,v in native[index].items() if k not in {'case','typed_observation'}}
  assert frame==source.frame(index)
  assert c.get(t['page_url']+'?concept='+frame['pedagogy']['concept']+'&occurrence='+str(frame['concept_occurrence'])).get_json()['steps'][0]['step_index']==index
 assert c.get(t['page_url']+'?limit=129').status_code==400
 assert app.test_client().get(t['page_url']).status_code==404
 compact=c.get(t['export_url']).get_json()['compact_trace'];assert compact['step_count']==11408 and compact['codec']=='radix-delta-tape/v1' and compact['final_state']['items']==sorted([-2147483648,2147483647]*40)
 assert c.post('/api/ordenamiento/step',json={'algorithm_id':'radixsort','cursor':11406}).get_json()['step']['step_index']==11407
 assert c.get('/sorting/visualizador').status_code==200
 with app.app_context():get_counting_store().ttl=0
 # Explicit store expiry; GET must not extend lifetime.
 with app.app_context():
  store=get_counting_store();from dataclasses import replace;store.entries[t['trace_id']]=replace(store.entries[t['trace_id']],expires=0)
 assert c.get(t['page_url']).status_code==410
 assert c.post('/api/ordenamiento/step',json={'algorithm_id':'radixsort','cursor':0}).status_code==410


def test_radix_transport_rejection_preserves_history(monkeypatch):
 app,c=prepare([3,1,2]);assert run(c).status_code==200;before=c.get('/api/ordenamiento/state').get_json()
 with app.app_context():get_counting_store().max_bytes=1
 r=run(c);assert r.status_code==400;d=r.get_json();assert d['history']==before['history'] and d['main_c']==before['main_c'] and d['visual_state']==before['visual_state']


def test_radix_native_report_success_errors_and_maximum_are_not_universal_proof():
 report=json.loads((audit_input_path(E/'native-expanded/report.json')).read_text(encoding='utf-8'));assert len(report['cases'])==16
 assert all(r['exact_selected_events'] and r['exact_declared_memory_observations'] and r['outcome']['live']==0 for r in report['cases'])
 assert not report['real_memory_exhaustion']
