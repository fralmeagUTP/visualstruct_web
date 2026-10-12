"""Permanent finite Cima regressions: red assertions document unresolved private fidelity gaps."""
from pathlib import Path
import json
import pytest
E=Path(__file__).resolve().parents[1]/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-cima-baseline-low'
M=E.parent/'visible-stack-cima-instructions-medium'
CASES=['empty','single','top','duplicate','minus1','minimum','maximum','bounds']
def report():return json.loads((E/'report.json').read_text(encoding='utf-8'))
def row(name):return next(x for x in report() if x['case']==name)
def private(name):
    from app.services.structure_service import StructureService
    from app.services.execution_trace_service import ExecutionTraceService
    d=row(name);v=d['visual']
    return ExecutionTraceService.build_trace(structure_id='stack',operation_name='cima',payload={},didactic_data=StructureService._didactic_content('stack'),before_state=v,after_state=v,success=name!='empty',message='private adapter query',mutates=False,console_events=[])
def adapter(name):
    from app.adapters.stack_adapter import StackAdapter
    a=StackAdapter()
    for v in reversed(row(name)['items_top_to_bottom']):a.execute('apilar',{'value':v})
    return a
@pytest.mark.parametrize('name',CASES)
def test_raw_public_C_function_has_exact_NULL_or_value_return(name):
    from app.domain.sequential import tad_pila as t
    f=getattr(t,'pila_cima',None);assert callable(f),'Missing Python transcription of public int pila_cima(ptrPila)'
    node=None
    for v in reversed(row(name)['items_top_to_bottom']):node=t.NodoPila(v,node)
    assert f(node)==row(name)['native_result']
@pytest.mark.parametrize('name',CASES)
def test_adapter_scalar_or_empty_exception_preserves_current_wrapper_contract(name):
    a=adapter(name)
    if name=='empty':
        from app.domain.sequential import EstructuraVaciaError
        with pytest.raises(EstructuraVaciaError):a.execute('cima',{})
    else:assert a.execute('cima',{})['result']==row(name)['native_result']
@pytest.mark.parametrize('name',CASES)
def test_repeated_private_queries_preserve_object_root_values_links_and_counter(name):
    a=adapter(name)
    def snapshot():
        q=a._structure;node=q._tope_ref[0];nodes=[]
        while node:nodes.append((id(node),node.nro,id(node.sgte)));node=node.sgte
        return id(q._tope_ref),id(q._tope_ref[0]),q._tamano,nodes,a.to_visual_state()
    before=snapshot()
    for _ in range(2):
        try:a.execute('cima',{})
        except Exception as error:
            from app.domain.sequential import EstructuraVaciaError
            assert name=='empty' and isinstance(error,EstructuraVaciaError)
        assert snapshot()==before
@pytest.mark.parametrize('name',CASES)
def test_private_trace_short_circuit_condition_matches_native_NULL_guard(name):
    steps=private(name)['steps'];conditions=[x['pedagogy']['condition'] for x in steps if x['pedagogy'].get('condition') is not None]
    assert len(conditions)==1,'Conditional expression p == NULL must have actual outcome, without reading NULL->nro'
    assert conditions[0]['result']==bool(row(name)['native'][1]['condition'])
@pytest.mark.parametrize('name',CASES)
def test_private_parameter_ptrPila_aliases_live_root_with_typed_scope(name):
    m=private(name)['steps'][0]['pedagogy'];p=next(x for x in m['pointers'] if x['name']=='p')
    assert p['type']=='ptrPila';assert p['initialized'] and p['scope']=='pila_cima' and p['scope_state']=='active'
    target=None if name=='empty' else m['heap_objects'][0]['id'];assert p['target']==target
    assert all(x['name']!='t' for x in m['pointers']),'No t local exists in pila_cima'
@pytest.mark.parametrize('name',CASES)
def test_private_heap_exact_nro_sgte_initialized_fields_and_stable_query(name):
    steps=private(name)['steps'];items=row(name)['items_top_to_bottom']
    for step in steps:
        m=step['pedagogy'];heap=m['heap_objects'];assert len(heap)==len(items);assert step['state_after']==row(name)['visual'];assert step['console']==[];assert m['heap_transition']['before']==m['heap_transition']['after']
        if not heap:
            if step['event_type']=='return':
                assert not any(x['name']=='p' for x in m['pointers'])
                assert any(x['name']=='pila' and x['initialized'] and x['scope']=='caller' for x in m['pointers'])
            else:assert any(x['name']=='p' and x.get('initialized') is True for x in m['pointers'])
            continue
        for i,h in enumerate(heap):
            assert h['type']=='struct NodoPila' and h['alive'] and h['initialized_mask']==3
            assert h['fields']=={'nro':items[i],'sgte':heap[i+1]['id'] if i+1<len(heap) else None}
@pytest.mark.parametrize('name',CASES)
def test_private_int_return_ends_function_scope_without_erasing_caller_nodes(name):
    m=private(name)['steps'][-1]['pedagogy'];result=[x for x in m['variables'] if x['name']=='return']
    assert len(result)==1 and result[0]['type']=='int' and result[0]['value']==row(name)['native_result']
    assert result[0]['initialized'] is True
    assert any(x.get('state')=='ended' for x in m['scopes']);assert m['call_stack']==[]
    assert not any(x['scope']=='pila_cima' for x in m['variables'])
    caller=next(x for x in m['variables'] if x['name']=='caller_result');assert caller['initialized'] is False and caller['written'] is False and caller['value'] is None
@pytest.mark.parametrize('name',CASES)
def test_rejected_unregistered_query_has_no_fabricated_executed_C_call(name):
    d=row(name)
    assert d['public_query_not_registered'] and d['public_query_dispatches_POST_and_GET']==0 and d['journal_queries']==0
    from app import create_app
    from app.config import Config
    from app.adapters.stack_adapter import StackAdapter
    from unittest.mock import patch
    class Q(Config):
        TESTING=True
        SESSION_CACHE_DIR=str(E.parent/'visible-stack-cima-instructions-medium/private-regression-sessions')
    client=create_app(Q).test_client()
    for v in reversed(d['items_top_to_bottom']):assert client.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':v}}).get_json()['success']
    original=StackAdapter.execute;queries=[]
    def observe(self,op,payload):
        if op=='cima':queries.append(op)
        return original(self,op,payload)
    results=[]
    with patch.object(StackAdapter,'execute',observe):
        for _ in range(2):
            response=client.post('/sequential/stack/operate',json={'operation':'cima','payload':{}});data=response.get_json();assert response.status_code==400 and data['success'] is False and data['visual_state']==d['visual'];results.append(data)
        assert client.get('/sequential/stack').status_code==200;assert client.get('/sequential/stack').status_code==200;assert queries==[]
    assert all(not any(x['operation']=='cima' for x in data['history']) for data in results)
    for data in results:
        assert not any(step['pedagogy'].get('concept') in ('call','return') for step in data['execution_trace']['steps']),'Rejected operation did not execute pila_cima; a validation-only frame must not claim C call/return'
@pytest.mark.parametrize('name',['empty','top','bounds','minus1'])
def test_existing_UI_rejects_query_without_new_feature_or_history_or_state_mutation(name):
    rows=json.loads((M/'browser/report.json').read_text(encoding='utf-8'));d=next(x for x in rows if x['case']==name)
    assert d['public_cima_not_registered'] and d['no_cima_selector'] and d['history_unchanged'] and d['both_views_exactly_unchanged'] and d['five_sections'] and d['extra_UI_POSTs']==0 and not d['JS_errors'] and d['standalone_queries_in_history']==0
    assert all(x['HTTP']==400 and x['data']['execution_trace']['steps']==[] and x['data']['execution_trace']['execution_started'] is False for x in d['rejected'])
    assert d['DOM_main_present']==(name!='empty')
@pytest.mark.parametrize('name',['empty','top','bounds','minus1'])
def test_real_DOM_HTTP_C17_caller_integrated_setup_queries_ownership_and_Doxygen(name):
    import hashlib
    d=json.loads((M/'caller-report.json').read_text(encoding='utf-8'));c=next(x for x in d['cases'] if x['case']==name)
    assert hashlib.sha256((M/'actual-callers'/name/'main.c').read_bytes()).hexdigest()==c['SHA'];assert c['runs']['C17']['exit']==c['runs']['ownership']['exit']==0
    assert c['alloc']==c['free'] and c['live']==0;assert all(x['exit']==1 for x in c['faults']);assert len(c['faults'])==c['alloc']
    assert d['Doxygen_warnings']==0 and d['documented_mains']==4
    body=(M/'actual-callers'/name/'main.c').read_text(encoding='utf-8');assert body.count('pila_cima(')==c['alloc'],'Integrated push echoes only, no standalone query history'
def test_native_defined_readonly_repeat_samples_and_resources_are_finite_scoped():
    native=[json.loads(x) for x in (E/'native/events.jsonl').read_text().splitlines()];assert len(native)==48
    for sample in range(16):
        rows=[x for x in native if x['sample']==sample];assert [x['phase'] for x in rows]==['entry','conditional','return'];assert rows[0]['items']==rows[1]['items']==rows[2]['items'];assert rows[1]['condition']==rows[0]['root_NULL'];assert rows[-1]['result_written']==1
    r=json.loads((M/'resources.json').read_text());assert len(r['samples'])==24 and all(x['max_python_peak_bytes']>0 and x['max_JSON_bytes']>0 for x in r['by_scope'].values())
    compare=json.loads((M/'private-native-comparison.json').read_text(encoding='utf-8'));assert compare['events_aligned']==48 and compare['conditions_aligned']==16 and compare['divergences']==0 and compare['C_H_current_exact'] and compare['native_execution_rerun'] is False
    reuse=json.loads((M/'caller-input-reuse.json').read_text());assert reuse['input_count']==6 and reuse['all_exact_bytes_equal'] and not reuse['C17_ownership_NULL_Doxygen_rerun']
