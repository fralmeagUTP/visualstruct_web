"""Compare the exact previous Graph builders and lossless HTTP transport."""
import importlib.util,json
from copy import deepcopy
from pathlib import Path
import pytest
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph import construction_instruction as construction,vertex_instruction as vertex,bfs_instruction as bfs
from app.domain.graph.snapshot_pool import SnapshotPool,expand_graph_trace
from app.routes.graph_routes import _json_safe
ROOT=Path(__file__).parents[1]
BEFORE=ROOT/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-QA18-graph-boundary-optimization-low/before'

from scripts.published_test_inputs import audit_input_path
def load(file):
    spec=importlib.util.spec_from_file_location('app.domain.graph._baseline_'+file,audit_input_path(BEFORE/'app/domain/graph'/f'{file}.py'))
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module

BASE={construction:load('construction_instruction'),vertex:load('vertex_instruction'),bfs:load('bfs_instruction')}
H=[{'operation':'create_graph','payload':{'directed':True}},
   {'operation':'insert_edge','payload':{'origin':1,'target':2,'weight':1}}]
CASES=[(construction,'build_graph_construction_trace','insert_edge',{'origin':2,'target':3,'weight':2}),
       (construction,'build_graph_construction_trace','list_edges',{}),
       (construction,'build_graph_construction_trace','edge_weight',{'origin':2,'target':1}),
       (vertex,'build_graph_vertex_trace','insert_vertex',{'vertex':3}),
       (vertex,'build_graph_vertex_trace','remove_vertex',{'vertex':1}),
       (bfs,'build_bfs_trace','run_bfs',{'start':1})]

def canonical(value):return json.dumps(_json_safe(value),sort_keys=True,separators=(',',':'))

def transport_canonical(value):
    # JSON object keys are text; normalize that boundary before ordering keys.
    value=json.loads(json.dumps(_json_safe(value)))
    return json.dumps(value,sort_keys=True,separators=(',',':'))

@pytest.mark.parametrize('module,fn,op,payload',CASES)
def test_all_events_frames_memory_callers_and_order_equal_previous_builder(monkeypatch,module,fn,op,payload):
    current=getattr(module,fn)
    monkeypatch.setattr(module,fn,getattr(BASE[module],fn))
    expected=S.execute_operation('graph',op,payload,H)
    monkeypatch.setattr(module,fn,current)
    actual=S.execute_operation('graph',op,payload,H)
    assert canonical(actual)==canonical(expected)
    assert actual['execution_trace']['steps']==expected['execution_trace']['steps']
    original=actual['execution_trace'];packed=original.snapshot_pool.pack(original)
    assert canonical(expand_graph_trace(packed))==canonical(original)
    assert packed['graph_snapshot_stats']['sampling'] is False
    assert len(packed['steps'])==len(original['steps'])

from _graph_snapshot_cases import CASES,arguments
from app.domain.graph import numeric_instruction as numeric
OLDPOOL=load('snapshot_pool')
class CopyOnlyReferencePool:
    # Independent logical oracle: preserve exact values/types; no interning/codec.
    def __init__(self, *, preserve_tuples=False):
        assert preserve_tuples is True
    def intern(self,value):
        return deepcopy(value)

def exact_typed_signature(value):
    if isinstance(value,dict):
        return (type(value).__name__,tuple((exact_typed_signature(k),exact_typed_signature(v)) for k,v in value.items()))
    if isinstance(value,(list,tuple)):
        return (type(value).__name__,tuple(exact_typed_signature(v) for v in value))
    if isinstance(value,float):
        return ('float',value.hex())
    return (type(value).__name__,value)


@pytest.mark.parametrize('case',CASES)
def test_numeric_complete_logical_trace_matches_immediate_before_pool(monkeypatch,case):
    current_pool=numeric.SnapshotPool;current_finish=numeric.finish_graph_trace
    monkeypatch.setattr(numeric,'SnapshotPool',CopyOnlyReferencePool)
    monkeypatch.setattr(numeric,'finish_graph_trace',OLDPOOL.finish_graph_trace)
    expected=expand_graph_trace(numeric.build_graph_numeric_trace(**arguments(case),_compact=False))
    monkeypatch.setattr(numeric,'SnapshotPool',current_pool)
    monkeypatch.setattr(numeric,'finish_graph_trace',current_finish)
    actual=expand_graph_trace(numeric.build_graph_numeric_trace(**arguments(case),_compact=False))
    assert (canonical(actual)==canonical(expected)) is True
    assert exact_typed_signature(actual)==exact_typed_signature(expected)
    packed=actual.snapshot_pool.pack(actual)
    assert transport_canonical(expand_graph_trace(packed))==transport_canonical(expected)
    assert len(packed['steps'])==len(expected['steps']) and packed['graph_snapshot_stats']['sampling'] is False

from _audit_graph_bfs_native_observer import CASES as BFS_CASES

@pytest.mark.parametrize('case',range(len(BFS_CASES)))
def test_bfs_all_recorded_input_shapes_equal_previous_builder_without_rerunning_C(monkeypatch,case):
    record=BFS_CASES[case]
    history=[{'operation':'create_graph','payload':{'directed':True}},
        *[{'operation':'insert_vertex','payload':{'vertex':v}} for v in record['vertices']],
        *[{'operation':'insert_edge','payload':{'origin':a,'target':b,'weight':1}} for a,b in record['edges']]]
    current=bfs.build_bfs_trace;current_reject=bfs.build_bfs_rejection_trace
    for _ in range(2 if record.get('repeat') else 1):
        monkeypatch.setattr(bfs,'build_bfs_trace',BASE[bfs].build_bfs_trace)
        monkeypatch.setattr(bfs,'build_bfs_rejection_trace',BASE[bfs].build_bfs_rejection_trace)
        expected=S.execute_operation('graph','run_bfs',{'start':record['start']},history)
        monkeypatch.setattr(bfs,'build_bfs_trace',current)
        monkeypatch.setattr(bfs,'build_bfs_rejection_trace',current_reject)
        actual=S.execute_operation('graph','run_bfs',{'start':record['start']},history)
        assert (canonical(actual)==canonical(expected)) is True
        assert actual['execution_trace']['steps']==expected['execution_trace']['steps']
        logical=actual['execution_trace'];pool=getattr(logical,'snapshot_pool',None) or SnapshotPool()
        assert (transport_canonical(expand_graph_trace(pool.pack(logical)))==transport_canonical(logical)) is True
        history=expected['history']
