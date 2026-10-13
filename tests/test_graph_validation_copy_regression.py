"""Graph read-only validation preserves the old contract and public isolation."""
from copy import deepcopy
import importlib.util
from pathlib import Path
import pytest
from app.domain.graph.snapshot_pool import validate_graph_logical_trace
from app.services.trace.compatibility import LegacyTraceAdapter
from app.services.trace.models import TraceStep

BASE = Path(__file__).parents[1] / 'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-QA18-graph-boundary-optimization-low/before/app/domain/graph/snapshot_pool.py'
spec = importlib.util.spec_from_file_location('graph_validation_before', BASE)
before = importlib.util.module_from_spec(spec)
spec.loader.exec_module(before)

def trace():
    state={'nodes':[{'id':1}], 'edges':[]}
    memory={'heap':[{'id':'V1','fields':{'dato':1,'sig':'NULL'}}]}
    return {'steps':[{'line_index':0,'line_text':'return g;', 'state_snapshot':state,
        'state_after':state,'debug':{'stage':'return','memory':memory},
        'pedagogy':{'memory':memory,'states':[state]*100},'console':[]}],
        'final_state':state,'source_code':'return g;'}

def outcome(fn, value):
    try:fn(value);return None
    except (ValueError,TypeError,KeyError) as error:return type(error),str(error)

@pytest.mark.parametrize('damage',['none','index','text','state_type','final','continuity','empty','event'])
def test_same_success_and_exact_errors_as_before_without_mutating_graph(damage):
    value=trace()
    if damage=='index':value['steps'][0]['line_index']=2
    if damage=='text':value['steps'][0]['line_text']='future();'
    if damage=='state_type':value['steps'][0]['state_snapshot']=[]
    if damage=='final':value['final_state']={'nodes':[]}
    if damage=='continuity':
        value['steps'].append(deepcopy(value['steps'][0]));value['steps'][1]['state_snapshot']={'nodes':[]}
    if damage=='empty':value['steps']=[]
    if damage=='event':value['steps'][0]['event_type']=' '
    original=deepcopy(value)
    assert outcome(validate_graph_logical_trace,value)==outcome(before.validate_graph_logical_trace,value)
    assert value==original

def test_roundtrip_check_still_rejects_changed_public_fields(monkeypatch):
    original=LegacyTraceAdapter.round_trip
    def corrupt(raw,**kwargs):
        result=deepcopy(original(raw,**kwargs));result[0]['console']=['future stdout'];return result
    monkeypatch.setattr(LegacyTraceAdapter,'round_trip',corrupt)
    assert outcome(validate_graph_logical_trace,trace())==outcome(before.validate_graph_logical_trace,trace())
    assert outcome(validate_graph_logical_trace,trace()) is not None

def test_default_copy_still_detaches_public_and_semantic_consumers():
    value=trace()['steps'][0];semantic=TraceStep.from_legacy(value)
    public=LegacyTraceAdapter.to_public(semantic)
    public['pedagogy']['memory']['heap'][0]['fields']['dato']=99
    semantic.before_state['nodes'][0]['id']=2
    assert value['pedagogy']['memory']['heap'][0]['fields']['dato']==1
    assert value['state_snapshot']['nodes'][0]['id']==1

def test_graph_readonly_conversions_do_not_copy_repeated_pedagogy(monkeypatch):
    calls=[];original=TraceStep.from_legacy.__func__
    def observe(cls,step,**kwargs):
        result=original(cls,step,**kwargs);calls.append(result.metadata['legacy_step'] is step);return result
    monkeypatch.setattr(TraceStep,'from_legacy',classmethod(observe))
    validate_graph_logical_trace(trace())
    assert calls==[True,True] # Both conversion paths, all contract checks above.
