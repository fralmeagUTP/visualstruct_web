"""Typed numeric Graph service state and exact public JSON boundaries."""
from __future__ import annotations
import pytest
from app.services.graph_structure_service import GraphStructureService
from app.domain.graph.snapshot_pool import GraphLogicalTrace, expand_graph_trace
from app.services.trace.engine import TraceEngine

CASES=[('run_bellman_ford',{'start':1,'end':2}),('run_prim',{'start':1}),('run_kruskal',{})]

def seed(directed=False, cycle=False):
    history=[]
    operations=[('create_graph',{'directed':directed})]+[('insert_vertex',{'vertex':v}) for v in (1,2,3)]
    edges=[(1,2,1),(2,3,-3),(3,1,1)] if cycle else [(1,2,3)]
    operations += [('insert_edge',{'origin':a,'target':b,'weight':w}) for a,b,w in edges]
    for op,payload in operations:
        result=GraphStructureService.execute_operation('graph',op,payload,history)
        assert result['success'];history=result['history']
    return history

def assert_logical(result):
    trace=result['execution_trace'];state=result['visual_state']
    assert isinstance(trace,GraphLogicalTrace) and 'graph_snapshot_codec' not in trace
    assert trace['final_state']==state==trace['steps'][-1]['state_after']
    assert len(TraceEngine.validate_legacy_trace(trace))==len(trace['steps'])
    for previous,current in zip(trace['steps'],trace['steps'][1:]):
        assert previous['state_after']==current['state_snapshot']
    return trace,state

@pytest.mark.parametrize('operation,payload',CASES)
def test_service_preserves_complete_typed_numeric_state(operation,payload):
    result=GraphStructureService.execute_operation('graph',operation,payload,seed())
    assert result['success'] is (operation=='run_bellman_ford');assert result['c_status']==(0 if operation=='run_bellman_ford' else 5);trace,state=assert_logical(result)
    assert trace['C_instruction_events']
    value=state['last_result']['result']
    if operation=='run_bellman_ford':
        assert value['path']==[1,2] and value['distance_to_destination']==3
        assert value['path_arcs']==[[1,2,3]] and value['path_edges']==[[1,2]]
        assert value['reachable'] is True and value['has_negative_cycle'] is False
        assert all(type(v) is int for v in value['path'])
        assert all(type(v) is int for arc in value['path_arcs'] for v in arc)
    else:
        assert value['total_weight'] is None and value['connected'] is False
        assert value['kind']=='error' and value['mst_edges']==[]
    assert result['history'][-1]['source_contract']=='graph-book/v1'

@pytest.mark.parametrize('operation,payload',CASES)
def test_HTTP_normalizes_only_wire_and_preserves_complete_state(client,operation,payload):
    for op,data in [('create_graph',{'directed':False})]+[('insert_vertex',{'vertex':v}) for v in (1,2,3)]+[('insert_edge',{'origin':1,'target':2,'weight':3})]:
        response=client.post('/graph/graph/operate',json={'operation':op,'payload':data})
        assert response.status_code==200 and response.get_json()['success']
    response=client.post('/graph/graph/operate',json={'operation':operation,'payload':payload})
    assert response.status_code==(200 if operation=='run_bellman_ford' else 400);body=response.get_json();assert body['success'] is (operation=='run_bellman_ford');assert body['c_status']==(0 if operation=='run_bellman_ford' else 5)
    wire=body['execution_trace'];assert wire['graph_snapshot_codec']=='graph-snapshot-pool/v1'
    trace=expand_graph_trace(wire);assert trace['final_state']==body['visual_state']==trace['steps'][-1]['state_after']
    assert wire['graph_snapshot_stats']['sampling'] is False
    assert len(wire['C_instruction_events'])==wire['graph_snapshot_stats']['C_events']
    for previous,current in zip(trace['steps'],trace['steps'][1:]):assert previous['state_after']==current['state_snapshot']
    value=body['visual_state']['last_result']['result']
    if operation=='run_bellman_ford':
        assert value['path']==[1,2] and value['path_arcs']==[[1,2,3]]
        assert value['distance_to_destination']==3 and value['reachable'] is True
        assert all(type(v) is int for arc in value['path_arcs'] for v in arc)
    else:assert value['mst_edges']==[] and value['total_weight'] is None and value['connected'] is False

@pytest.mark.parametrize('operation,payload',[('run_bellman_ford',{'start':99,'end':2}),('run_prim',{'start':99})])
def test_absent_vertex_has_typed_complete_C_failure_state(operation,payload):
    result=GraphStructureService.execute_operation('graph',operation,payload,seed())
    assert result['success'] is False;trace,state=assert_logical(result)
    assert result['c_status']==2 and result['history'][-1]['source_contract']=='graph-book/v1'
    assert trace.get('application_rejection') is not True
    assert trace['C_instruction_events'] and trace['execution_started'] is True

def test_negative_cycle_error_still_has_actual_C_events_and_typed_final():
    result=GraphStructureService.execute_operation('graph','run_bellman_ford',{'start':1,'end':3},seed(True,True))
    assert result['success'] is False;trace,state=assert_logical(result)
    assert state['last_result']['result']['has_negative_cycle'] is True
    assert trace['C_instruction_events'] and trace.get('application_rejection') is not True
    value=state['last_result']['result']
    assert result['c_status']==4 and value['path']==[] and value['path_arcs']==[]
    assert value['distance_to_destination'] is None and value['reachable'] is False
