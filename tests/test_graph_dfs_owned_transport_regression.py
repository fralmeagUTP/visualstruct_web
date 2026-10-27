"""Canonical DFS request-owned publication; archives retained, corrupt pools rejected."""
from pathlib import Path
import copy,gzip,json
import pytest
from _book_traversal_oracle import recorded_call
from app.domain.graph.owned_transport import OwnedTransportPool
from app.domain.graph.snapshot_pool import SnapshotPool,GraphLogicalTrace,expand_graph_trace,REFERENCE
from app.services.trace.engine import TraceEngine
from app.services.c_code_service import CCodeService
from app.routes.graph_routes import _json_safe

FIXTURES=Path(__file__).parent/'fixtures/dfs_owned_transport'
CASES=['chain3','cycle3','disconnected','self-loop','prior-marks','raw-missing-start','single-vertex-return','API-missing-start-rejection','owned-alias-input-mutation']
def wire(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=True).encode()

@pytest.mark.parametrize('case',CASES)
def test_every_c_event_and_field_roundtrips_canonical_trace_with_archive_preserved(case):
    historical=json.loads(gzip.decompress((FIXTURES/(case+'.json.gz')).read_bytes()))
    assert historical['steps'] and historical['source_code']
    fixture={'vertices':[1,2,3],'edges':[[1,2],[2,3]],'start':1}
    if case=='cycle3':fixture['edges'].append([3,1])
    elif case=='disconnected':fixture['edges']=[[1,2]]
    elif case=='self-loop':fixture={'vertices':[1],'edges':[[1,1]],'start':1}
    elif case in ['raw-missing-start','API-missing-start-rejection']:fixture['start']=99
    elif case=='single-vertex-return':fixture={'vertices':[1],'edges':[],'start':1}
    marks={1:1,2:0,3:1} if case=='prior-marks' else None
    result,trace=recorded_call('dfs',fixture,marks)
    expected=copy.deepcopy(trace)
    TraceEngine.validate_legacy_trace(trace,copy_value=lambda x:x)
    assert isinstance(trace,GraphLogicalTrace) and trace['book_instruction_model']
    own=trace.snapshot_pool.pack(trace);legacy=SnapshotPool().pack(expected)
    # Pool record numbering belongs to its construction order, not C semantics.
    # The full expanded transport must remain exactly equal in every field.
    assert wire(expand_graph_trace(own))==wire(expand_graph_trace(legacy))
    assert wire(expand_graph_trace(own))==wire(expected)
    assert wire(_json_safe(expand_graph_trace(own)))==wire(_json_safe(expand_graph_trace(legacy)))
    assert wire(trace.snapshot_pool.pack(trace))==wire(own)
    seal=wire(trace)
    # Mutation of actual external recorded transition inputs must not alter
    # the already assembled request-owned canonical trace.
    result['transitions'][0]['before']['heap_nodes'].clear()
    result['graph_after']['vertices'].clear()
    assert wire(trace)==seal

@pytest.mark.parametrize('value',[b'x',{1},object()])
def test_invalid_primitive_in_unreachable_record_is_not_silently_omitted(value):
    pool=OwnedTransportPool();pool.records.append([1,[value]])
    with pytest.raises(TypeError):pool.pack({'steps':[]})

@pytest.mark.parametrize('record',[[1,[{REFERENCE:0}]],[0,[['x',1],['x',2]]],[0,[[1,2]]],[2,[]],[1,[[]]],[0,[['x']]],[0,'bad'],[True,[]]])
def test_entire_unreachable_source_table_is_validated(record):
    pool=OwnedTransportPool();pool.records.append(record)
    with pytest.raises(ValueError):pool.pack({'steps':[]})

def test_unreachable_nonfinite_primitive_does_not_change_target_safety():
    pool=OwnedTransportPool();pool.records.append([1,[float('inf')]])
    assert pool.pack({'steps':[]})['graph_snapshot_pool'].is_json_safe

def test_normalized_tuple_dictionary_keys_primitives_and_final_memory_match_legacy():
    pool=OwnedTransportPool(preserve_tuples=True)
    step={'state_after':{1:(True,1,1.0,None),'other':[-0.0,float('inf')]},'console':[]}
    trace={'steps':[pool.intern(step)],'numeric_C_memory':{'returned':None}}
    packed=pool.pack(trace)
    assert wire(packed)==wire(SnapshotPool().pack(trace))
    assert not packed['graph_snapshot_pool'].is_json_safe
    assert wire(_json_safe(packed))==wire(_json_safe(SnapshotPool().pack(trace)))

def test_existing_plain_and_no_pool_fallbacks_remain_identical():
    trace={'steps':[{'state_after':{'n':1},'console':[]}]}
    legacy=SnapshotPool().pack(trace)
    wrapped=GraphLogicalTrace(trace,snapshot_pool=None)
    assert wire((getattr(wrapped,'snapshot_pool',None) or SnapshotPool()).pack(wrapped))==wire(legacy)
    assert expand_graph_trace(legacy)==trace
