"""Typed logical Graph service and normalized JSON transport boundary regressions."""
import json
import pytest
from app.services.graph_structure_service import GraphStructureService
from app.domain.graph.snapshot_pool import SnapshotPool, expand_graph_trace, GraphLogicalTrace
from app.services.trace.engine import TraceEngine

def seed_service():
    history=[]
    for operation,payload in [('create_graph',{'directed':True}),('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),('insert_vertex',{'vertex':3}),('insert_edge',{'origin':1,'target':2,'weight':3})]:
        result=GraphStructureService.execute_operation('graph',operation,payload,history)
        assert result['success'];history=result['history']
    return history

def test_dijkstra_service_preserves_typed_complete_logical_trace():
    result=GraphStructureService.execute_operation('graph','run_dijkstra',{'start':1,'end':2},seed_service())
    trace=result['execution_trace'];state=result['visual_state']
    assert trace['final_state']==state
    assert trace['steps'][-1]['state_after']==state
    assert isinstance(trace,GraphLogicalTrace) and 'graph_snapshot_codec' not in trace
    assert all(type(k) is int for k in state['last_result']['result']['distances'])
    assert state['last_result']['result']['distances']=={1:0,2:3,3:float('inf')}
    assert state['last_result']['result']['path']==[1,2]
    assert state['last_result']['result']['distance_to_destination']==3
    assert len(TraceEngine.validate_legacy_trace(trace))==len(trace['steps'])
    for previous,current in zip(trace['steps'],trace['steps'][1:]):assert previous['state_after']==current['state_snapshot']

def test_real_HTTP_transport_decodes_to_complete_JSON_state(client):
    for operation,payload in [('create_graph',{'directed':True}),('insert_vertex',{'vertex':1}),('insert_vertex',{'vertex':2}),('insert_vertex',{'vertex':3}),('insert_edge',{'origin':1,'target':2,'weight':3})]:
        assert client.post('/graph/graph/operate',json={'operation':operation,'payload':payload}).status_code==200
    response=client.post('/graph/graph/operate',json={'operation':'run_dijkstra','payload':{'start':1,'end':2}})
    assert response.status_code==200
    body=response.get_json();wire=body['execution_trace'];assert wire['graph_snapshot_codec']=='graph-snapshot-pool/v1'
    trace=expand_graph_trace(wire)
    assert trace['final_state']==trace['steps'][-1]['state_after']==body['visual_state']
    assert body['visual_state']['last_result']['result']['distances']=={'1':0,'2':3,'3':None}
    assert body['visual_state']['last_result']['result']['path']==[1,2]
    assert wire['graph_snapshot_stats']['sampling'] is False
    assert len(wire['C_instruction_events'])==wire['graph_snapshot_stats']['C_events']
    for previous,current in zip(trace['steps'],trace['steps'][1:]):assert previous['state_after']==current['state_snapshot']

@pytest.mark.parametrize('key,text',[(1,'1'),(True,'true'),(None,'null')])
def test_typed_snapshot_rejects_keys_that_collide_on_JSON_wire(key,text):
    with pytest.raises(ValueError,match='Duplicate normalized snapshot keys'):
        SnapshotPool(preserve_tuples=True).intern({key:'typed',text:'text'})

def test_typed_pool_retains_logical_types_and_JSON_wire_normalization():
    pool=SnapshotPool(preserve_tuples=True)
    state={'distances':{-1:0,2:3},'tuple':(1,2),'types':[True,1,1.0]}
    interned=pool.intern(state)
    assert interned==state and type(interned['tuple']) is tuple and all(type(k) is int for k in interned['distances'])
    packet=pool.pack({'steps':[{'state_snapshot':interned,'state_after':interned,'console':[]}], 'final_state':interned})
    wire=json.loads(json.dumps(packet,allow_nan=False));restored=expand_graph_trace(wire)
    assert restored['steps'][-1]['state_after']==restored['final_state']=={'distances':{'-1':0,'2':3},'tuple':[1,2],'types':[True,1,1.0]}
    assert [type(x) for x in restored['final_state']['types']]==[bool,int,float]


def test_dijkstra_rejection_keeps_logical_boundary_without_executing_C():
    previous=GraphStructureService.execute_operation('graph','run_dijkstra',{'start':1,'end':2},seed_service())
    rejected=GraphStructureService.execute_operation('graph','run_dijkstra',{'start':99,'end':2},previous['history'])
    trace=rejected['execution_trace']
    assert rejected['success'] is False
    assert isinstance(trace,GraphLogicalTrace) and 'graph_snapshot_codec' not in trace
    assert trace['application_rejection'] is True and trace['execution_started'] is False
    assert trace['C_instruction_events']==[]
    assert trace['final_state']==trace['steps'][-1]['state_after']==rejected['visual_state']
    assert TraceEngine.validate_legacy_trace(trace)
