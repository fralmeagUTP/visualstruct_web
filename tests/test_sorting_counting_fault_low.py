"""Counting HTTP safe failure/retry contracts; deliberate fault injection, not real OOM."""
import pytest
import hashlib
from _audit_approved_source_supersessions import assert_historical_protected_hash
from app import create_app
from app.domain.sorting import counting_sparse_instructions
from app.services.counting_trace_service import get_counting_store

def prepare(c,values):
    assert c.post('/api/ordenamiento/create-array',json={'values':values}).status_code==200
    assert c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'counting_sort'}).status_code==200
    return c.get('/api/ordenamiento/state').get_json()

def test_reserve_creation_failure_is_C_error_not_unhandled_500_and_retry(monkeypatch):
    app=create_app();c=app.test_client();before=prepare(c,[0,1000]);original=counting_sparse_instructions.SparseCounts
    def fail(_length):raise MemoryError('controlled allocation failure')
    monkeypatch.setattr(counting_sparse_instructions,'SparseCounts',fail)
    response=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'})
    assert response.status_code==400
    data=response.get_json();assert not data['success'] and data['visual_state']['items']==before['visual_state']['items'] and data['history']==before['history'] and data['main_c']==before['main_c']
    monkeypatch.setattr(counting_sparse_instructions,'SparseCounts',original)
    good=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'}).get_json();assert good['success'] and sum(x['operation']=='run' for x in good['history'])==1

def test_trace_registration_failure_keeps_error_state_contract_and_retry():
    app=create_app();c=app.test_client();before=prepare(c,[0,1000])
    with app.app_context():store=get_counting_store();store.max_bytes=1
    response=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'});assert response.status_code==400
    data=response.get_json();assert not data['success'] and data['visual_state']['items']==before['visual_state']['items'] and data['history']==before['history'] and data['main_c']==before['main_c']
    with app.app_context():store.max_bytes=128*1024*1024
    good=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'}).get_json();assert good['success'] and len(good['history'])==len(before['history'])+1

def test_range_rejection_invalid_create_and_retry_preserve_history():
    app=create_app();c=app.test_client();before=prepare(c,[0,1000000])
    bad=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'step_by_step'});assert bad.status_code==400
    data=bad.get_json();assert not data['success'] and data['history']==before['history'] and data['visual_state']['items']==[0,1000000]
    assert c.post('/api/ordenamiento/create-array',json={'values':[]}).status_code==400
    assert c.get('/api/ordenamiento/state').get_json()['history']==before['history']
    prepare(c,[0,1000]);good=c.post('/api/ordenamiento/run',json={'algorithm_id':'counting_sort','mode':'fast'}).get_json();assert good['success'] and sum(x['operation']=='run' for x in good['history'])==1


@pytest.mark.parametrize('case',['n5_k5','n2_k6','n8_k17','n80_k1','n80_k80','near_min','near_max','n2_k1001'])
def test_independent_outside_four_full_native_events_are_permanent_oracle(case):
    from pathlib import Path
    import json
    from app.domain.sorting.counting_sparse_tape import expand_small
    root=Path(__file__).resolve().parents[1];base=root/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-counting-native-fault-low/outside-four-full'
    for ext in ['c','h']:assert_historical_protected_hash(root,'docs/tads_C/tad_ordenamiento.'+ext,hashlib.sha256((base/('tad_ordenamiento.'+ext)).read_bytes()).hexdigest())
    d=json.loads((base/(case+'.json')).read_text(encoding='utf-8'));tape=counting_sparse_instructions.run_counting_sparse_trace(d['case']['input'])['steps'];assert len(tape)==len(d['native'])
    for index,native in enumerate(d['native']):
        event=tape[index]['instruction_event'];event['conteo']=expand_small(event['conteo']);assert event=={k:v for k,v in native.items() if k!='case'}
