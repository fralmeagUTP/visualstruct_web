"""Finite dequeue instruction regressions, failures remain visible without xfail."""
from __future__ import annotations
import json
from pathlib import Path
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-queue-desencolar-instructions-medium'
CASES={'single':[-1],'multi':[7,-1],'duplicate':[7,7],'bounds':[-2147483648,2147483647]}
@pytest.fixture(params=list(CASES))
def execution(client,request):
    name=request.param
    for v in CASES[name]:assert client.post('/sequential/queue/operate',json={'operation':'encolar','payload':{'value':v}}).get_json()['success']
    data=client.post('/sequential/queue/operate',json={'operation':'desencolar','payload':{}}).get_json()
    return name,data

def _step(data,token):return next(s for s in data['execution_trace']['steps'] if token in s['line_text'])
def test_native_current_safe12calls87events19conditions():
    d=json.loads((E/'native-summary.json').read_text(encoding='utf-8'));assert (d['calls'],d['events'],d['conditions'])==(12,87,19);assert d['ownership']=='OWNERSHIP 7 7 0'
def test_historical_dequeue_executable_tokens_compatible_not_pointer_coverage():
    d=json.loads((E/'historical-comparison.json').read_text(encoding='utf-8'));assert d['dequeue_executable_tokens_equal'] and d['all_executable_tokens_equal'];assert d['old_SHA']!=d['current_SHA']
def test_dequeue_final_value_and_FIFO_match_C(execution):
    name,d=execution;assert d['success'] and d['result']==CASES[name][0];assert [x['value'] for x in d['visual_state']['items']]==CASES[name][1:]
def test_empty_guard_condition_true_without_predeclared_locals(client):
    d=client.post('/sequential/queue/operate',json={'operation':'desencolar','payload':{}}).get_json();s=_step(d,'if (q == NULL');assert s['pedagogy']['condition']['result'] is True;assert not any(x['name'] in ['aux','num','ant','t'] for x in s['pedagogy']['pointers'])
def test_aux_alias_keeps_first_node_identity_until_free(execution):
    _,d=execution;before=_step(d,'struct NodoCola *aux =');after=_step(d,'q->delante = aux->sgte;');ptr=lambda s:next(x for x in s['pedagogy']['pointers'] if x['name']=='aux');front=before['state_after']['delante'];assert ptr(before)['target']==front and ptr(after)['target']==front

def test_num_is_int_local_copied_before_free_and_survives_return(execution):
    name,d=execution
    for token in ['int num =','free(aux);','return num;']:
        vs=_step(d,token)['pedagogy']['variables'];num=next((x for x in vs if x['name']=='num'),None);assert num is not None and num['type']=='int' and num['value']==CASES[name][0]
def test_detached_node_remains_live_until_actual_free(execution):
    name,d=execution;s=_step(d,'q->delante = aux->sgte;');live=[x for x in s['pedagogy']['heap_objects'] if not x.get('freed')];assert len(live)==len(CASES[name]);assert not s['pedagogy']['heap_transition'].get('freed')
def test_queue_variables_and_heap_use_real_C_types(execution):
    _,d=execution;s=_step(d,'struct NodoCola *aux =');vs=s['pedagogy']['variables'];assert next(x for x in vs if x['name']=='aux')['type']=='struct NodoCola *';assert all(x['type']=='struct NodoCola *' for x in vs if x['name'] in ['delante','atras']);assert all(x.get('type')=='struct NodoCola' for x in s['pedagogy']['heap_objects'])
def test_return_preserves_caller_roots_and_ends_function_scope(execution):
    name,d=execution;s=_step(d,'return num;');expected='NULL' if len(CASES[name])==1 else 'N2';p=s['pedagogy']
    physical=p['memory_state'];memory=p['dequeue_memory'];root=memory['root']
    assert physical['delante']==physical['atras']==expected
    assert (root['front'] or 'NULL')==(root['rear'] or 'NULL')==expected
    assert root['alive'] and root['valid'] and root['initialized'] and root['identity']=='&cola'
    assert any(x.get('state')=='ended' or x.get('scope_state')=='ended' for x in p.get('scopes',[]))
    assert memory['scope_state']=='ended' and memory['call_stack']==[]
    assert s['state_after']==d['visual_state']==d['execution_trace']['final_state']
    assert not {'delante','atras'}.intersection(s['state_after'])
    assert [x['value'] for x in s['state_after']['items']]==CASES[name][1:]
    heap=p['heap_objects'];assert len(heap)==len(CASES[name])-1 and all(n['alive'] and not n['freed'] for n in heap)
    assert {n['id'] for n in heap}==({'N2'} if expected=='N2' else set())
def test_reload_keeps_prepared_dequeue_trace_without_builder(client,execution,monkeypatch):
    _,d=execution
    from app.services.execution_trace_service import ExecutionTraceService
    def forbidden(*args,**kwargs):raise AssertionError('GET must reuse prepared trace')
    monkeypatch.setattr(ExecutionTraceService,'build_trace',forbidden)
    response=client.get('/sequential/queue');assert response.status_code==200
    text=response.data.decode('utf-8');decoder=json.JSONDecoder();model=decoder.raw_decode(text.split('window.SEQ_VIEW_MODEL =',1)[1].lstrip())[0];assert model.get('prepared_dequeue_trace')==d['execution_trace']
@pytest.mark.parametrize('name',list(CASES))
def test_actual_DOM_caller_C17_ownership_and_Doxygen(name):
    d=json.loads((E/'caller-report.json').read_text(encoding='utf-8'));row=next(x for x in d['cases'] if x['case']==name);assert row['C17_exit']==0 and row['ownership_exit']==0 and row['allocs']==row['frees'] and row['live']==0;assert d['documented_mains']==4 and d['Doxygen_warnings']==0

def test_actual_UI_both_views_and_four_reloads_real_Next():
    rows=json.loads((E/'browser/report.json').read_text(encoding='utf-8'));assert len(rows)==4
    for d in rows:assert d['five_numbered_sections_match'] and not d['JS_errors'] and d['extra_POSTs']==0 and d['history_reload_equal'] and d['reload_trace_equal'] and d['reload_next_clicked']


def test_empty_trace_executes_actual_C_printf_before_return(client):
    d=client.post('/sequential/queue/operate',json={'operation':'desencolar','payload':{}}).get_json();s=_step(d,'printf(');assert s['console']==['Cola vacía. No se puede desencolar.']

def test_heap_fields_are_real_nro_sgte_and_nodes_do_not_merge(execution):
    name,d=execution;s=_step(d,'struct NodoCola *aux =');heap=s['pedagogy']['heap_objects'];assert len({x['id'] for x in heap})==len(CASES[name]);assert all(set(x['fields'])=={'nro','sgte'} for x in heap)
