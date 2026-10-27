"""Finite priority dequeue regressions from current C/API/UI baseline; no xfail."""
from __future__ import annotations
import json
from pathlib import Path
import pytest
from functools import cache
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-desencolar-instructions-medium'
CASES=['front','interior','rear','equal-front','equal-interior','several-updates','single','empty']
NORMAL=CASES[:-1]
from scripts.published_test_inputs import audit_input_path
def read(name):return json.loads((audit_input_path(E/name)).read_text(encoding='utf-8'))
@cache
def data(name):
    # Fresh isolated API execution: stored reports remain evidence, never the sole product oracle.
    from app import create_app
    from app.config import Config
    class RegressionConfig(Config):
        TESTING=True
        SESSION_CACHE_DIR=str(E/'private-regression-sessions')
    client=create_app(RegressionConfig).test_client()
    row=next(x for x in read('API-report.json') if x['case']==name)
    for i,priority in enumerate(row['priorities']):assert client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':10*(i+1),'priority':priority}}).get_json()['success']
    return client.post('/sequential/priority_queue/operate',json={'operation':'desencolar','payload':{}}).get_json()
def step(name,token):return next(x for x in data(name)['execution_trace']['steps'] if token in x['line_text'])
@pytest.mark.parametrize('name',CASES)
def test_API_scalar_and_adapter_both_outputs_match_native_stable_selection(name):
    row=next(x for x in read('API-report.json') if x['case']==name);d=data(name);raw=[x for x in read('reused-dequeue-native-events.json') if x['case']==CASES.index(name)];last=raw[-1];assert d['success']==(name!='empty');assert d.get('result')==(last['output_value'] if name!='empty' else None);assert d['visual_state']['items']==[{'value':v,'priority':p} for v,p in last['items']]
    if name!='empty':
        from app.adapters.priority_queue_adapter import PriorityQueueAdapter
        adapter=PriorityQueueAdapter()
        for i,priority in enumerate(row['priorities']):
            adapter.execute('encolar',{'value':10*(i+1),'priority':priority});assert adapter.to_visual_state()['items']==[{'value':10*(j+1),'priority':p} for j,p in enumerate(row['priorities'][:i+1])]
        direct=adapter.execute('desencolar',{});assert direct['result']==last['output_value'] and direct['result_priority']==last['output_priority']
def test_all_74_native_conditions_have_correct_current_result():
    report=read('native-priority-dequeue-current-review.json');assert len(report['condition_comparisons']['observations'])==74 and report['condition_comparisons']['mismatches']==[]
def test_current_trace_contains_all_198_compatible_native_occurrences():
    report=read('native-priority-dequeue-current-review.json');assert len(report['observations'])==198 and report['missing_sequence_events']==[]
    for row in report['observations']:
        observed=data(row['case'])['execution_trace']['steps'][row['index']];assert observed['line_text'].strip()==row['line'].strip()
        state=observed['state_snapshot'] if row['line'].startswith('return ') else observed['state_after']
        assert all(state.get(k)==v for k,v in row['expected'].items())
        if row['native']['condition']!=-1:assert observed['pedagogy']['condition']['result']==bool(row['native']['condition'])
@pytest.mark.parametrize('name',NORMAL)
def test_unlink_keeps_other_initialized_aliases_and_objective_identity(name):
    rows=[x for x in read('native-priority-dequeue-current-review.json')['observations'] if x['case']==name and x['line'] in ['cola->delante = objetivo->sgte;','objetivoPrev->sgte = objetivo->sgte;']];assert len(rows)==1
    for row in rows:assert all(data(name)['execution_trace']['steps'][row['index']]['state_after'].get(k)==row['expected'][k] for k in ['actual','prev','objetivo','objetivoPrev'])
@pytest.mark.parametrize('name',['front','rear','single','empty'])
def test_declarations_show_indeterminate_typed_scoped_locals_without_fake_NULL(name):
    for local in ['actual','prev','objetivo','objetivoPrev']:
        s=step(name,'CPNodo *'+local+';');v=next((x for x in s['pedagogy']['variables'] if x['name']==local),None);assert v is not None and v['type']=='CPNodo *' and v['initialized'] is False and v['scope']=='cp_desencolar'
def test_both_int_output_pointers_are_distinct_from_caller_scalars():
    for name in NORMAL:
        s=step(name,'*valor = objetivo->valor;');pointers=s['pedagogy']['pointers'];v=next((x for x in pointers if x['name']=='valor'),None);p=next((x for x in pointers if x['name']=='prioridad'),None);assert v is not None and p is not None and v['type']==p['type']=='int *' and v['target']!=p['target']
def test_free_removes_same_node_and_marks_every_alias_to_it_unusable():
    for name in NORMAL:
        s=step(name,'free(objetivo);');f=s['pedagogy'];freed=f['heap_transition']['freed'];assert len(freed)==1 and freed[0]['freed']
        target=step(name,'*valor = objetivo->valor;')['state_after']['objetivo'];refs=[x for x in f['pointers'] if x['name'] in ['objetivo','prev'] and x.get('target')==target];assert refs and all(x.get('valid') is False for x in refs);assert not any(x['id']==freed[0]['id'] for x in f['heap_objects'])
@pytest.mark.parametrize('name',NORMAL)
def test_quantity_changes_only_at_own_guarded_store_and_output_copies_precede_free(name):
    steps=data(name)['execution_trace']['steps'];store=next(i for i,x in enumerate(steps) if 'cola->cantidad--;' in x['line_text']);free=next(i for i,x in enumerate(steps) if 'free(objetivo);' in x['line_text']);v=next(i for i,x in enumerate(steps) if '*valor = objetivo->valor;' in x['line_text']);p=next(i for i,x in enumerate(steps) if '*prioridad = objetivo->prioridad;' in x['line_text']);initial=len(next(x['priorities'] for x in read('API-report.json') if x['case']==name));assert v<p<free<store;assert all(x['state_after'].get('cantidad',initial)==initial for x in steps[:store]);assert steps[store]['state_after']['cantidad']==initial-1
@pytest.mark.parametrize('name',['root_NULL','empty','value_NULL','priority_NULL','both_NULL','extremes','minus1','counter_zero'])
def test_python_C_transcription_matches_defined_native_private_guard_and_counter_case(name):
    from app.domain.sequential import tad_cola_prioridad as t
    seeds={'root_NULL':None,'empty':[],'value_NULL':[(17,7)],'priority_NULL':[(17,7)],'both_NULL':[(17,7)],'extremes':[(2147483647,2147483647),(-2147483648,-2147483648)],'minus1':[(-1,-1)],'counter_zero':[(17,7)]}[name];q=None if seeds is None else t.ColaPrioridad();v=None if name in ['value_NULL','both_NULL'] else [-999];p=None if name in ['priority_NULL','both_NULL'] else [-888]
    for value,priority in seeds or []:assert t.cp_encolar(q,value,priority)
    if name=='counter_zero':q.cantidad=0
    result=t.cp_desencolar(q,v,p);items=[];node=q.delante if q else None
    while node:items.append([node.valor,node.prioridad]);node=node.sgte
    expected=next(x['native_final'] for x in read('new-native-gap-report.json')['cases'] if x['case']==name);assert {'return':result,'items':items,'count':q.cantidad if q else 0,'value':v[0] if v else None,'priority':p[0] if p else None}==expected

def test_new_native_gap_types_safe_lifetimes_and_initialized_output_guards():
    report=read('new-native-gap-report.json');assert report['calls']==8 and report['ownership']=='OWNERSHIP 7 7 0' and report['signature_types_C17'];events=[json.loads(x) for x in (audit_input_path(E/'new-native-gaps/events.jsonl')).read_text(encoding='utf-8').splitlines()]
    for sample in range(5):
        rows=[x for x in events if x['sample']==sample];assert rows[-1]['return']==0 and not rows[-1]['value_written'] and not rows[-1]['priority_written'];assert all(x['aliases']==[None]*4 for x in rows)
@pytest.mark.parametrize('name',['front','rear','single'])
def test_return_ends_locals_but_preserves_caller_roots_and_counter(name):
    s=step(name,'return true;');p=s['pedagogy']
    assert any(x.get('state')=='ended' or x.get('scope_state')=='ended' for x in p.get('scopes',[]))
    physical=p['memory_state'];memory=p['dequeue_memory'];root=memory['root']
    assert {'delante','atras','cantidad'} <= physical.keys()
    assert (physical['delante'],physical['atras'],physical['cantidad'])==(root['front'] or 'NULL',root['rear'] or 'NULL',root['quantity'])
    assert root['alive'] and root['valid'] and root['identity']=='&cp'
    assert memory['scope_state']=='ended' and memory['call_stack']==[]
    assert s['state_after']==data(name)['visual_state']==data(name)['execution_trace']['final_state']
    assert not {'delante','atras','cantidad'}.intersection(s['state_after'])
    assert root['quantity']==len(s['state_after']['items'])
    heap=p['heap_objects'];assert len(heap)==root['quantity'] and all(n['alive'] and not n['freed'] for n in heap)
    ids={n['id'] for n in heap};assert all(target is None or target in ids for target in [root['front'],root['rear']])
def test_current_UI_two_views_native_diagram_roots_and_replay_are_verified():
    rows=read('browser/report.json');assert len(rows)==4
    for d in rows:assert d['five_numbered_sections_match'] and d['extra_POSTs']==0 and not d['JS_errors'];assert all(x['equal'] for x in d['DOM_root_observations'])
@pytest.mark.parametrize('name',['front','interior','rear','equal-interior'])
def test_priority_dequeue_reload_restores_exact_trace_and_real_Next(name):
    d=next(x for x in read('browser/report.json') if x['case']==name);assert d['history_reload_equal'] and d['reload_trace_equal'] and d['reload_next_clicked']
@pytest.mark.parametrize('name',['front','interior','rear','equal-interior'])
def test_actual_DOM_main_C17_native_outputs_ownership_and_Doxygen(name):
    d=read('caller-report.json');row=next(x for x in d['cases'] if x['case']==name);assert row['C17_compile_exit']==0;assert row['C17_exit']==row['ownership_exit']==0;assert row['allocs']==row['frees']==3 and row['live']==0;assert d['Doxygen_warnings']==0 and d['documented_main_symbols']==4
    pairs={'front':[(10,1),(20,2)],'interior':[(20,1),(30,2)],'rear':[(30,1),(20,2)],'equal-interior':[(20,1),(30,1)]}[name];expected=['Operacion aplicada.']*3+[f'Extraido: {v} prioridad: {p}' for v,p in pairs];assert row['C17_stdout'].splitlines()==row['ownership_stdout'].splitlines()==expected
    assert len(row['NULL_setup_faults'])==3
    for fault in row['NULL_setup_faults']:assert fault['exit']==1 and f"OWNERSHIP {fault['point']-1} {fault['point']-1} 0" in fault['stderr'];assert fault['stdout'].splitlines()==['Operacion aplicada.']*(fault['point']-1)

@pytest.mark.parametrize('name',['root_NULL','value_NULL','priority_NULL','both_NULL','counter_zero'])
def test_private_instruction_trace_preserves_native_guards_outputs_and_guarded_counter(name):
    from app.domain.sequential.priority_queue_dequeue_instruction import build_priority_queue_dequeue_trace
    source=data('front')['execution_trace']['source_code']
    seeds=[] if name=='root_NULL' else [{'value':17,'priority':7}]
    trace=build_priority_queue_dequeue_trace(payload={},source_code=source,code_title='cp_desencolar',before_state={'items':seeds,'size':len(seeds),'cantidad':0 if name=='counter_zero' else len(seeds)},after_state={},success=name=='counter_zero',message='',null_root=name=='root_NULL',null_value=name in ['value_NULL','both_NULL'],null_priority=name in ['priority_NULL','both_NULL'])
    native=next(x['native_final'] for x in read('new-native-gap-report.json')['cases'] if x['case']==name);last=trace['steps'][-1];memory=last['pedagogy']['dequeue_memory']
    assert memory['result']==native['return'] and memory['root']['quantity']==native['count']
    assert last['state_after']['items']==[{'value':v,'priority':p} for v,p in native['items']]
    assert memory['outputs']['value_written']==memory['outputs']['priority_written']==(name=='counter_zero')
    assert memory['outputs']['value']==(native['value'] if name=='counter_zero' else None)
    assert memory['outputs']['priority']==(native['priority'] if name=='counter_zero' else None)
    assert all(x['console']==[] for x in trace['steps'])
    assert last['pedagogy']['scopes'][0]['state']=='ended'
