"""Finite hidden priority Front baseline, independent C oracles, no xfail."""
from __future__ import annotations
from pathlib import Path
from functools import cache
import json
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-priority-queue-front-instructions-medium'
CASES=['front','interior','rear','equal-front','equal-interior','several-updates','single','empty']
NORMAL=CASES[:-1]
from scripts.published_test_inputs import audit_input_path
def read(name):return json.loads((audit_input_path(E/name)).read_text(encoding='utf-8-sig'))
@cache
def data(name):
    from app import create_app
    from app.config import Config
    class RegressionConfig(Config):
        TESTING=True
        SESSION_CACHE_DIR=str(E/'private-regression-sessions')
    client=create_app(RegressionConfig).test_client();row=next(x for x in read('API-report.json') if x['case']==name)
    for i,priority in enumerate(row['priorities']):assert client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':10*(i+1),'priority':priority}}).get_json()['success']
    return client.post('/sequential/priority_queue/operate',json={'operation':'frente','payload':{}}).get_json()
def step(name,token):return next(x for x in data(name)['execution_trace']['steps'] if token in x['line_text'])
@pytest.mark.parametrize('name',CASES)
def test_current_API_scalar_and_both_adapter_outputs_match_native(name):
    raw=[x for x in read('reused-front-native-events.json') if x['case']==CASES.index(name)];last=raw[-1];d=data(name);assert d['success']==(name!='empty') and d.get('result')==(last['output_value'] if name!='empty' else None);assert d['visual_state']['items']==[{'value':v,'priority':p} for v,p in last['items']]
    if name!='empty':
        from app.adapters.priority_queue_adapter import PriorityQueueAdapter
        a=PriorityQueueAdapter();priorities=next(x['priorities'] for x in read('API-report.json') if x['case']==name)
        for i,p in enumerate(priorities):a.execute('encolar',{'value':10*(i+1),'priority':p})
        result=a.execute('frente',{});assert result['result']==last['output_value'] and result['result_priority']==last['output_priority']
def test_all_93_defined_native_instruction_boundaries_and_39_conditions_match_current_API():
    report=read('native-priority-front-current-review.json');assert len(report['observations'])==93 and not report['missing_sequence_events'] and report['divergent_observations']==0;assert len(report['condition_comparisons']['observations'])==39
    for row in report['observations']:
        s=data(row['case'])['execution_trace']['steps'][row['index']];state=s['state_snapshot'] if row['line'].startswith('return ') else s['state_after'];assert s['line_text'].strip()==row['line'].strip();assert all(state.get(k)==v for k,v in row['expected'].items())
        if row['native']['condition']!=-1:assert s['pedagogy']['condition']['result']==bool(row['native']['condition'])
@pytest.mark.parametrize('name',CASES)
def test_two_front_queries_preserve_adapter_root_nodes_links_priorities_and_count(name):
    from app.adapters.priority_queue_adapter import PriorityQueueAdapter
    a=PriorityQueueAdapter();priorities=next(x['priorities'] for x in read('API-report.json') if x['case']==name)
    for i,p in enumerate(priorities):a.execute('encolar',{'value':10*(i+1),'priority':p})
    before=a.to_visual_state()
    for _ in range(2):
        try:a.execute('frente',{})
        except Exception as error:
            assert name=='empty';from app.domain.sequential import EstructuraVaciaError;assert isinstance(error,EstructuraVaciaError)
        assert a.to_visual_state()==before
    # Journal may change, while rebuilding GET must never redispatch readonly queries.
    from app import create_app
    from app.config import Config
    from unittest.mock import patch
    class ReplayConfig(Config):
        TESTING=True
        SESSION_CACHE_DIR=str(E/'private-replay-regression-sessions')
    client=create_app(ReplayConfig).test_client()
    for i,p in enumerate(priorities):assert client.post('/sequential/priority_queue/operate',json={'operation':'encolar','payload':{'value':10*(i+1),'priority':p}}).get_json()['success']
    original=PriorityQueueAdapter.execute;queries=[]
    def observed(self,operation,payload):
        if operation=='frente':queries.append(operation)
        return original(self,operation,payload)
    with patch.object(PriorityQueueAdapter,'execute',observed):
        for _ in range(2):
            result=client.post('/sequential/priority_queue/operate',json={'operation':'frente','payload':{}}).get_json();assert result['success']==bool(priorities);assert result['visual_state']==before
        assert sum(x['operation']=='frente' for x in result['history'])==(2 if priorities else 0)
        assert client.get('/sequential/priority_queue').status_code==200
        assert client.get('/sequential/priority_queue').status_code==200
        assert len(queries)==2
@pytest.mark.parametrize('name',['front','single','empty'])
@pytest.mark.parametrize('local',['actual','objetivo'])
def test_const_node_declarations_are_indeterminate_in_correct_scope(name,local):
    s=step(name,'const CPNodo *'+local+';');v=next((v for v in s['pedagogy']['variables'] if v['name']==local),None);assert v is not None and v['type']=='const CPNodo *' and v['initialized'] is False and v['scope']=='cp_frente'
@pytest.mark.parametrize('name',['front','single','empty'])
def test_const_borrowed_root_parameter_has_typed_scope_and_initialized_address(name):
    p=next(x for x in data(name)['execution_trace']['steps'][0]['pedagogy']['pointers'] if x['name']=='cola');assert p['type']=='const ColaPrioridad *' and p['scope']=='cp_frente' and p['initialized'] is True
@pytest.mark.parametrize('name',['front','rear','single'])
def test_two_int_output_pointers_are_distinct_from_initialized_caller_copies(name):
    s=step(name,'*prioridad = objetivo->prioridad;');f=s['pedagogy'];v=next((x for x in f['pointers'] if x['name']=='valor'),None);p=next((x for x in f['pointers'] if x['name']=='prioridad'),None);assert v and p and v['type']==p['type']=='int *' and v['target']!=p['target'];caller={x['name']:x for x in f['variables'] if x.get('scope')=='caller'};assert caller['caller_valor']['initialized'] and caller['caller_prioridad']['initialized']
@pytest.mark.parametrize('name',NORMAL)
def test_all_nonnull_local_aliases_resolve_to_same_live_heap_objects(name):
    s=step(name,'actual = cola->delante->sgte;');f=s['pedagogy'];ids={x['id'] for x in f['heap_objects']};aliases=[x for x in f['pointers'] if x['name'] in ['actual','objetivo']];assert len(aliases)==2;assert all(x['target'] in ids for x in aliases if x['target'] not in [None,'NULL'])
@pytest.mark.parametrize('name',CASES)
def test_return_ends_local_scope_but_preserves_readonly_caller_roots_and_count(name):
    s=step(name,'return false;' if name=='empty' else 'return true;');p=s['pedagogy']
    assert any(x.get('state')=='ended' for x in p.get('scopes',[]))
    physical=p['memory_state'];memory=p['front_memory'];root=memory['root']
    assert {'delante','atras','cantidad'} <= physical.keys()
    assert (physical['delante'],physical['atras'],physical['cantidad'])==(root['front'] or 'NULL',root['rear'] or 'NULL',root['quantity'])
    assert root['alive'] and root['valid'] and root['identity']=='&cp'
    assert memory['scope_state']=='ended' and memory['call_stack']==[]
    trace=data(name)['execution_trace'];assert s['state_after']==data(name)['visual_state']==trace['final_state']
    assert not {'delante','atras','cantidad'}.intersection(s['state_after'])
    assert root['quantity']==len(s['state_after']['items'])
    first=trace['steps'][0]['pedagogy'];assert root==first['front_memory']['root']
    assert all(x['pedagogy']['heap_objects']==first['heap_objects'] and not x['pedagogy']['heap_transition']['freed'] for x in trace['steps'])
    heap=p['heap_objects'];assert len(heap)==root['quantity'] and all(n['alive'] and not n['freed'] for n in heap)
    ids={n['id'] for n in heap};assert all(target is None or target in ids for target in [root['front'],root['rear']])
@pytest.mark.parametrize('name',['root_NULL','empty','value_NULL','priority_NULL','both_NULL','extremes','minus1'])
def test_raw_Python_front_matches_defined_private_C_guard_and_output_contract(name):
    from app.domain.sequential import tad_cola_prioridad as t
    seeds={'root_NULL':None,'empty':[],'value_NULL':[(17,7)],'priority_NULL':[(17,7)],'both_NULL':[(17,7)],'extremes':[(2147483647,2147483647),(-2147483648,-2147483648)],'minus1':[(-1,-1)]}[name];q=None if seeds is None else t.ColaPrioridad();v=None if name in ['value_NULL','both_NULL'] else [-999];p=None if name in ['priority_NULL','both_NULL'] else [-888]
    for value,priority in seeds or []:assert t.cp_encolar(q,value,priority)
    before=[];node=q.delante if q else None
    while node:before.append((id(node),id(node.sgte),node.valor,node.prioridad));node=node.sgte
    result=t.cp_frente(q,v,p);items=[];after=[];node=q.delante if q else None
    while node:items.append([node.valor,node.prioridad]);after.append((id(node),id(node.sgte),node.valor,node.prioridad));node=node.sgte
    assert before==after
    native=next(x['native_final'] for x in read('new-native-gap-report.json')['cases'] if x['case']==name);assert {'return':result,'items':items,'count':q.cantidad if q else 0,'value':v[0] if v else None,'priority':p[0] if p else None}==native
    from app.domain.sequential.priority_queue_front_instruction import build_priority_queue_front_trace
    trace=build_priority_queue_front_trace(payload={},source_code=data('front')['execution_trace']['source_code'],code_title='cp_frente',before_state={'items':[{'value':v,'priority':p} for v,p in seeds or []],'size':len(seeds or [])},after_state={},success=native['return'],message='',null_root=name=='root_NULL',null_value=name in ['value_NULL','both_NULL'],null_priority=name in ['priority_NULL','both_NULL'],caller_value=-999,caller_priority=-888)
    memory=trace['steps'][-1]['pedagogy']['front_memory'];assert memory['result']==native['return']
    assert memory['outputs']['value']==(native['value'] if name not in ['value_NULL','both_NULL'] else -999)
    assert memory['outputs']['priority']==(native['priority'] if name not in ['priority_NULL','both_NULL'] else -888)
    assert memory['outputs']['value_written']==memory['outputs']['priority_written']==native['return']
    assert all(x['heap_transition']['before']==x['heap_transition']['after'] and not x['heap_transition']['freed'] for x in [y['pedagogy'] for y in trace['steps']])
    assert all(y['console']==[] for y in trace['steps'])

def test_new_native_private_observer_proves_const_types_readonly_and_no_target_allocation():
    r=read('new-native-gap-report.json');assert r['calls']==7 and r['events']==49 and r['conditions']==11 and r['signature_types_C17'] and r['ownership']=='OWNERSHIP 6 6 0';events=[json.loads(x) for x in (audit_input_path(E/'new-native-gaps/events.jsonl')).read_text().splitlines()]
    for sample in range(7):
        rows=[x for x in events if x['sample']==sample];first=rows[0];assert all((x['items'],x['count'],x['front'],x['rear'],x['heap'])==(first['items'],first['count'],first['front'],first['rear'],first['heap']) for x in rows)
        if sample<5:assert rows[-1]['return']==0 and not rows[-1]['value_written'] and not rows[-1]['priority_written']
@pytest.mark.parametrize('name',['front','equal-interior','extremes','minus1'])
def test_real_existing_UI_keeps_query_hidden_and_readonly_without_fabricated_trace(name):
    d=next(x for x in read('browser/report.json') if x['case']==name);assert d['operation_registered_hidden'] and d['no_front_selector'] and d['five_sections'] and d['visual_unchanged'] and d['DOM_pairs_match_source_frames'] and d['extra_UI_POSTs_reload_or_view_switch']==0 and not d['JS_errors'];assert len(d['responses'])==2 and all(x['data']['success'] for x in d['responses'])
@pytest.mark.parametrize('name',['front','equal-interior','extremes','minus1'])
def test_real_DOM_setup_only_main_C17_Doxygen_and_controlled_NULL_ownership(name):
    r=read('caller-report.json');x=next(x for x in r['cases'] if x['case']==name);n=x['seed_allocations'];assert x['C17_compile_exit']==x['C17_exit']==x['ownership_compile_exit']==x['ownership_exit']==0 and x['allocs']==x['frees']==n and x['live']==0;raw=read('reused-front-native-events.json');gap=read('new-native-gap-report.json')
    if name in ['front','equal-interior']:
        last=[z for z in raw if z['case']==(0 if name=='front' else 4)][-1];value,priority=last['output_value'],last['output_priority']
    else:
        last=next(z['native_final'] for z in gap['cases'] if z['case']==name);value,priority=last['value'],last['priority']
    assert x['C17_stdout'].splitlines()==['Operacion aplicada.']*n+[f'Frente: {value} prioridad: {priority}']*2 and x['ownership_stdout']==x['C17_stdout'];assert r['Doxygen_warnings']==0 and r['documented_main_symbols']==4
    assert len(x['NULL_setup_faults'])==n
    for f in x['NULL_setup_faults']:assert f['exit']==1 and f"OWNERSHIP {f['point']-1} {f['point']-1} 0" in f['stderr']
@pytest.mark.parametrize('name',['front','equal-interior','extremes','minus1'])
def test_successful_hidden_queries_are_reproduced_twice_in_actual_caller_after_reload(name):
    # Fidelity requirement for completed real API actions; not a request for a new selector.
    d=next(x for x in read('browser/report.json') if x['case']==name);assert d['front_calls_in_history']==d['main_front_calls']==2
