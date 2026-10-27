"""Additional Graph10 lifetime/rejection invariants; no Graph6 or closed callers."""
import pytest
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph.construction_instruction import ConstructionProgram,ConstructionMachine,NULL

EDGE=[{'operation':'create_graph','payload':{'directed':True}},{'operation':'insert_edge','payload':{'origin':11,'target':12,'weight':-1}}]

@pytest.mark.parametrize('operation,payload',[
 ('exists_vertex',{'vertex':11}),('exists_edge',{'origin':11,'target':12}),
 ('edge_weight',{'origin':11,'target':12}),('list_vertices',{}),('list_edges',{})])
def test_queries_keep_graph_borrowed_and_no_future_API_result(operation,payload):
 data=S.execute_operation('graph',operation,payload,EDGE);trace=data['execution_trace']
 assert data['success'];assert len(data['history'])==len(EDGE)
 for step in trace['steps'][:-1]:
  frame=step['pedagogy'];assert step['state_after']['last_result'] is None
  assert all(node['borrowed'] for node in frame['memory_state']['heap_nodes'])
  assert not frame['memory']['allocated'] and not frame['memory']['freed']
 assert trace['steps'][-1]['pedagogy']['instruction_event']['C_executed'] is False
 if operation in ['list_vertices','list_edges']:
  memory=trace['steps'][-1]['pedagogy']['memory_state'];assert memory['returned']==memory['graph']['v' if operation=='list_vertices' else 'a']

@pytest.mark.parametrize('operation,payload',[
 ('edge_weight',{'origin':12,'target':11}),('insert_edge',{'origin':'invalid','target':2}),
 ('generate_random_graph',{'vertices_count':0})])
def test_API_rejection_has_zero_C_events_and_initial_frame(operation,payload):
 data=S.execute_operation('graph',operation,payload,EDGE);trace=data['execution_trace']
 assert not data['success'];assert trace['C_instruction_events']==[] and not trace['execution_started']
 assert trace['steps'][0]['pedagogy']['initial_frame']['memory_state']['frames']==[]
 assert data['history']==EDGE

@pytest.mark.parametrize('operation,payload',[('clear_graph',{}),('create_graph',{'directed':False})])
def test_caller_cleanup_records_retired_aliases_without_reading_them(operation,payload):
 data=S.execute_operation('graph',operation,payload,EDGE);steps=data['execution_trace']['steps']
 frees=[s for s in steps if s['pedagogy']['instruction_event']['phase']=='free']
 assert len(frees)==3
 for step in frees:
  memory=step['pedagogy']['memory_state'];retired={n['id'] for n in memory['retired_objects']}
  assert not retired.intersection(n['id'] for n in memory['heap_nodes'])
  assert all(not s['pedagogy']['memory']['dangling_references'] for s in steps)
 final=steps[-1]['pedagogy']['memory_state'];assert final['heap_nodes']==[] and final['frees']==3
 assert final['graph']=={'v':NULL,'a':NULL}

@pytest.mark.parametrize('failed', [1,2,3])
def test_raw_insertion_allocator_failure_preserves_actual_partial_C_graph(failed):
 data=S.execute_operation('graph','insert_edge',{'origin':21,'target':22,'weight':7},[{'operation':'create_graph','payload':{'directed':True}}])
 machine=ConstructionMachine(ConstructionProgram(data['execution_trace']['source_code']),[],[],fail_allocation=failed)
 returned=machine.invoke('audit_graph_operation',[machine.graph]);assert machine.attempts==3
 assert machine.allocations==2 and machine.frees==0
 # The raw C may allocate the arc after failing to create an endpoint; no rollback
 # or invented API malloc contract is asserted by this isolated symbolic fixture.
 kinds=[n['kind'] for n in machine.heap.values()]
 assert kinds.count('struct NodoA')==(0 if failed==3 else 1)
 assert (returned['a']==NULL)==(failed==3)

def test_constructor_helper_call_stack_has_one_active_frame_and_initial_has_no_function():
 data=S.execute_operation('graph','insert_edge',{'origin':31,'target':32,'weight':6},[])
 trace=data['execution_trace'];initial=trace['steps'][0]['pedagogy']['initial_frame']
 assert initial['source']['function'] is None and initial['phase']['label']=='Estado inicial'
 nested=[s['pedagogy'] for s in trace['steps'] if len(s['pedagogy']['call_stack'])>1]
 assert nested
 for frame in nested:
  stack=frame['call_stack'];assert all(f['scope_status']=='suspendido' for f in stack[:-1])
  assert stack[-1]['scope_status'] in ['activo','terminado (retorno)']
  assert frame['instruction_event']['function']==stack[-1]['function']
