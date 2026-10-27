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
    assert result['success'];trace,state=assert_logical(result)
    assert trace['C_instruction_events']
    value=state['last_result']['result']
    if operation=='run_bellman_ford':
        assert value['distances']=={1:0,2:3,3:float('inf')}
        assert all(type(k) is int for k in value['distances'])
        assert all(type(k) is int for k in value['previous'])
        assert value['path']==[1,2] and value['distance_to_destination']==3
    else:
        assert value['total_weight']==3 and value['components_count']==2
        assert value['connected'] is False
        assert len(value['mst_edges'])==1 and type(value['mst_edges'][0]) is tuple
        a,b,w=value['mst_edges'][0];assert {a,b}=={1,2} and w==3

@pytest.mark.parametrize('operation,payload',CASES)
def test_HTTP_normalizes_only_wire_and_preserves_complete_state(client,operation,payload):
    for op,data in [('create_graph',{'directed':False})]+[('insert_vertex',{'vertex':v}) for v in (1,2,3)]+[('insert_edge',{'origin':1,'target':2,'weight':3})]:
        response=client.post('/graph/graph/operate',json={'operation':op,'payload':data})
        assert response.status_code==200 and response.get_json()['success']
    response=client.post('/graph/graph/operate',json={'operation':operation,'payload':payload})
    assert response.status_code==200;body=response.get_json();assert body['success']
    wire=body['execution_trace'];assert wire['graph_snapshot_codec']=='graph-snapshot-pool/v1'
    trace=expand_graph_trace(wire);assert trace['final_state']==body['visual_state']==trace['steps'][-1]['state_after']
    assert wire['graph_snapshot_stats']['sampling'] is False
    assert len(wire['C_instruction_events'])==wire['graph_snapshot_stats']['C_events']
    for previous,current in zip(trace['steps'],trace['steps'][1:]):assert previous['state_after']==current['state_snapshot']
    value=body['visual_state']['last_result']['result']
    if operation=='run_bellman_ford':assert value['distances']=={'1':0,'2':3,'3':None}
    else:assert len(value['mst_edges'])==1 and type(value['mst_edges'][0]) is list

@pytest.mark.parametrize('operation,payload',[('run_bellman_ford',{'start':99,'end':2}),('run_prim',{'start':99})])
def test_application_rejection_has_typed_complete_state_without_C(operation,payload):
    result=GraphStructureService.execute_operation('graph',operation,payload,seed())
    assert result['success'] is False;trace,state=assert_logical(result)
    assert trace['application_rejection'] is True and trace['execution_started'] is False
    assert trace['C_instruction_events']==[]

def test_negative_cycle_error_still_has_actual_C_events_and_typed_final():
    result=GraphStructureService.execute_operation('graph','run_bellman_ford',{'start':1,'end':3},seed(True,True))
    assert result['success'] is False;trace,state=assert_logical(result)
    assert state['last_result']['result']['has_negative_cycle'] is True
    assert trace['C_instruction_events'] and trace.get('application_rejection') is not True
    assert all(type(k) is int for k in state['last_result']['result']['distances'])
