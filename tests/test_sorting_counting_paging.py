"""HTTP Counting paging, ownership, concurrent immutable reads and no redispatch."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from dataclasses import replace
from time import monotonic
import json
from app.services.c_code_service import CCodeService
import pytest
from app import create_app
from app.domain.sorting.tad_ordenamiento import SortingInterpreter

ROOT=Path(__file__).resolve().parents[1]
E=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-expanded-fidelity'

def run(client, values):
    assert client.post('/api/ordenamiento/create-array',json={'values':values}).status_code==200
    r=client.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'})
    assert r.status_code==200,r.data
    return r.get_json()

@pytest.fixture
def paged():
    app=create_app();client=app.test_client();data=run(client,[999999,0])
    return app,client,data

def no_run(*_args,**_kwargs): raise AssertionError('navigation dispatched sorting')

def test_cap_HTTP_first_middle_last_match_real_C_scalar_samples(paged,monkeypatch):
    app,c,d=paged;t=d['execution_trace'];assert t['schema']=='counting-paged-trace/v1' and t['step_count']==3000051
    assert len(json.dumps(d))<2*1024*1024 and len(t['initial_page']['steps'])<=16
    monkeypatch.setattr(SortingInterpreter,'run',no_run)
    for line in (E/'native-cap-scalar/stdout.jsonl').read_text().splitlines():
        native=json.loads(line);page=c.get(t['page_url'],query_string={'start':native['index'],'limit':1}).get_json();assert page['trace_id']==t['trace_id']
        f=page['steps'][0];event=f['debug']['instruction_event'];assert f['step_index']==native['index'] and f['state_after']['metrics']['steps']==native['index']+1
        for key,value in native.items():
            if key not in ('index','selected_counts'):assert event[key]==value
        counts=dict(event['conteo']['nonzero']) if event['conteo'] else None
        assert ([counts.get(k,0) for k in [0,1,499999,999999]] if counts is not None else None)==native['selected_counts']
        assert f['pedagogy']['source']['line_index']==f['line_index']
        assert f['line_text']==('' if f['line_index'] is None else t['source_code'].splitlines()[f['line_index']])
    assert d['result']['metrics']==dict(comparisons=2,moves=6,swaps=0,steps=3000051)

def test_pages_backwards_legacy_step_reload_export_do_not_dispatch_or_append(paged,monkeypatch):
    app,c,d=paged;t=d['execution_trace'];history=d['history'];main=d['main_c'];monkeypatch.setattr(SortingInterpreter,'run',no_run)
    middle=t['step_count']//2
    first=c.get(t['page_url'],query_string={'start':middle,'limit':3}).get_json()
    c.get(t['page_url'],query_string={'start':t['step_count']-3,'limit':3})
    assert c.get(t['page_url'],query_string={'start':middle,'limit':3}).get_json()==first
    step=c.post('/api/ordenamiento/step',json={'algorithm_id':'counting_sort','cursor':middle+1,'direction':'prev'}).get_json()
    assert step['cursor']==middle and step['step']==first['steps'][0] and step['total_steps']==t['step_count']
    state=c.get('/api/ordenamiento/state').get_json();assert state['history']==history and state['main_c']==main and state['visual_state']['items']==[0,999999]
    html=c.get('/sorting/visualizador');assert html.status_code==200 and t['trace_id'].encode() in html.data
    export=c.get(t['export_url']).get_json()['compact_trace'];assert export['step_count']==t['step_count'] and len(export['records'])==58 and len(json.dumps(export))<256*1024
    assert c.get('/api/ordenamiento/state').get_json()['history']==history

def test_ownership_invalid_pages_expiry_and_reset(paged):
    app,c,d=paged;t=d['execution_trace'];other=app.test_client();assert other.get(t['page_url']).status_code==404
    for args in [{'start':-1},{'start':t['step_count']},{'limit':0},{'limit':129},{'start':'x'},{'limit':'2.5'}]:assert c.get(t['page_url'],query_string=args).status_code==400
    store=app.extensions['counting_trace_store'];key=t['trace_id'];store.entries[key]=replace(store.entries[key],expires=monotonic()-1)
    assert c.get(t['page_url']).status_code==410 and c.get(t['export_url']).status_code==410
    assert c.post('/api/ordenamiento/step',json={'algorithm_id':'counting_sort','cursor':10}).status_code==410
    assert other.get(t['page_url']).status_code==404
    assert c.post('/api/ordenamiento/reset',json={}).status_code==200 and key not in store.entries

def test_old_trace_immutable_after_new_input_and_concurrent_session_reads(paged,monkeypatch):
    app,c,d=paged;t=d['execution_trace'];url=t['page_url'];baseline=c.get(url,query_string={'start':1500025,'limit':3}).get_json()
    new=run(c,[0,1000]);assert new['execution_trace']['trace_id']!=t['trace_id']
    state=c.get('/api/ordenamiento/state').get_json();monkeypatch.setattr(SortingInterpreter,'run',no_run)
    cookie=c.get_cookie(app.config['SESSION_COOKIE_NAME'])
    def read(_):
        peer=app.test_client();peer.set_cookie(app.config['SESSION_COOKIE_NAME'],cookie.value)
        return peer.get(url,query_string={'start':1500025,'limit':3}).get_json()
    with ThreadPoolExecutor(max_workers=4) as pool:assert all(r==baseline for r in pool.map(read,range(12)))
    after=c.get('/api/ordenamiento/state').get_json();assert after['history']==state['history'] and after['visual_state']==state['visual_state'] and after['main_c']==state['main_c']

def test_storage_budget_and_concept_seek_without_logical_enumeration(paged):
    from app.services.counting_trace_service import CountingTraceStore
    app,c,d=paged;t=d['execution_trace'];store=app.extensions['counting_trace_store'];source=store.entries[t['trace_id']].source
    limited=CountingTraceStore(max_bytes=source.retained_bytes+1,max_traces=1)
    first=limited.register('owner',source);second=limited.register('owner',source);assert list(limited.entries)==[second]
    with pytest.raises(KeyError):limited.get('owner',first)
    with pytest.raises(ValueError):CountingTraceStore(max_bytes=1).register('owner',source)
    index=1500025;f=c.get(t['page_url'],query_string={'start':index,'limit':1}).get_json()['steps'][0]
    found=c.get(t['page_url'],query_string={'concept':f['pedagogy']['concept'],'occurrence':f['concept_occurrence']}).get_json()['steps'][0];assert found['step_index']==index

def test_eighty_large_range_paged_final_metrics_and_budget():
    app=create_app();c=app.test_client();values=[int(i*999999/79) for i in range(80)];d=run(c,values);t=d['execution_trace'];assert t['schema']=='counting-paged-trace/v1'
    assert t['step_count']==3000909 and d['visual_state']['items']==sorted(values)
    assert d['result']['metrics']==dict(comparisons=158,moves=240,swaps=0,steps=3000909)
    assert t['manifest']['retained_bytes']<24*1024*1024 and len(json.dumps(d))<2*1024*1024
    last=c.get(t['page_url'],query_string={'start':t['step_count']-2,'limit':2}).get_json()['steps']
    assert last[0]['debug']['instruction_event']['token']=='count_free' and last[-1]['state_after']['items']==sorted(values)


@pytest.mark.parametrize('case',['single','ordered','reverse','duplicates','negative','extremes'])
def test_dense_transport_preserves_frozen_C_event_and_before_contract(case):
    old=json.loads((E.parent/'visible-sorting-counting-baseline-low/native-final'/(case+'.json')).read_text(encoding='utf-8'))
    c=create_app().test_client();d=run(c,old['input']);t=d['execution_trace'];assert t.get('schema')!='counting-paged-trace/v1' and len(t['steps'])==len(old['native'])
    for i,(f,native) in enumerate(zip(t['steps'],old['native'])):
        assert f['debug']['instruction_event']=={k:v for k,v in native.items() if k!='case'}
        previous=old['native'][max(0,i-1)];assert f['state_snapshot']['items']==previous['array'] and f['state_snapshot']['auxiliary_array']==previous['conteo']
        assert f['state_after']['auxiliary_array']==native['conteo']
        assert f['pedagogy']['invariant']['holds']
    # Navigation also reuses a dense source and retains its public array representation.
    current=c.post('/api/ordenamiento/step',json={'cursor':0,'direction':'next','algorithm_id':'counting_sort'}).get_json();assert current['step']==t['steps'][1]

def test_comparison_two_owned_paged_traces_leaves_session_unchanged():
    app=create_app();c=app.test_client();before=c.get('/api/ordenamiento/state').get_json()
    d=c.post('/api/ordenamiento/compare',json={'values':[0,1000],'left_algorithm':'counting_sort','right_algorithm':'counting_sort'}).get_json();assert d['success']
    a,b=[d[side]['trace'] for side in ['left','right']];assert a['trace_id']!=b['trace_id']
    for t in [a,b]:assert c.get(t['page_url'],query_string={'start':t['step_count']//2,'limit':1}).status_code==200
    after=c.get('/api/ordenamiento/state').get_json();assert after['history']==before['history'] and after['visual_state']==before['visual_state']

def test_adapter_transport_dictionary_is_JSON_without_private_source_object():
    from app.adapters.sorting_adapter import SortingAdapter
    a=SortingAdapter();a.create_array([0,1000]);a.select_algorithm('counting_sort');d=a.run('step_by_step',source_code=CCodeService.get_structure_data('sorting_array')['operations']['counting_sort']);encoded=json.dumps(d)
    assert 'counting-paged-trace/v1' in encoded and '_page_source' not in encoded
