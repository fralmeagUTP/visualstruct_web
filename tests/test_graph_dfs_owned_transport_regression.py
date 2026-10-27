"""Exact archived DFS traces, request-owned publication, and corrupt pool rejection."""
from pathlib import Path
import copy,gzip,json
import pytest
from app.domain.graph.dfs_instruction import build_dfs_trace,build_dfs_rejection_trace
from app.domain.graph.owned_transport import OwnedTransportPool
from app.domain.graph.snapshot_pool import SnapshotPool,GraphLogicalTrace,expand_graph_trace,REFERENCE
from app.services.trace.engine import TraceEngine
from app.services.c_code_service import CCodeService
from app.routes.graph_routes import _json_safe

FIXTURES=Path(__file__).parent/'fixtures/dfs_owned_transport'
CASES=['chain3','cycle3','disconnected','self-loop','prior-marks','raw-missing-start','single-vertex-return','API-missing-start-rejection','owned-alias-input-mutation']
def wire(v):return json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=True).encode()

@pytest.mark.parametrize('case',CASES)
def test_every_c_event_and_field_matches_accepted_archive_and_legacy_transport(case):
    expected=json.loads(gzip.decompress((FIXTURES/(case+'.json.gz')).read_bytes()))
    before=copy.deepcopy(expected['steps'][0]['state_snapshot']);after=copy.deepcopy(expected['final_state']);seed=copy.deepcopy(expected);seed['steps']=[]
    builder=build_dfs_rejection_trace if case=='API-missing-start-rejection' else build_dfs_trace
    if case=='API-missing-start-rejection':seed['source_code']=CCodeService._build_graph_data()['operations']['run_dfs']
    seal=wire((seed,before,after));trace=builder(copy.deepcopy(seed),before,after)
    assert wire(trace)==wire(expected)
    assert wire((seed,before,after))==seal
    TraceEngine.validate_legacy_trace(trace,copy_value=lambda x:x)
    if case!='API-missing-start-rejection':
        assert isinstance(trace,GraphLogicalTrace)
        assert isinstance(trace.snapshot_pool,OwnedTransportPool)
        own=trace.snapshot_pool.pack(trace);legacy=SnapshotPool().pack(expected)
        assert wire(own)==wire(legacy)
        assert wire(expand_graph_trace(own))==wire(expected)
        assert wire(_json_safe(own))==wire(_json_safe(legacy))
        assert wire(trace.snapshot_pool.pack(trace))==wire(own)
        seal=wire(trace);before['nodes'].clear();after['nodes'].clear()
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
