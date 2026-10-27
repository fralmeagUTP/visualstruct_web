"""Additional Graph10 lifetime/rejection invariants; no Graph6 or closed callers."""
import pytest
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph.book_c_subset import BookSession,NULL

EDGE=[{'operation':'create_graph','payload':{'directed':True}},{'operation':'insert_edge','payload':{'origin':11,'target':12,'weight':-1}}]
for row in EDGE:row['source_contract']='graph-book/v1'

@pytest.mark.parametrize('operation,payload',[
 ('exists_vertex',{'vertex':11}),('exists_edge',{'origin':11,'target':12}),
 ('edge_weight',{'origin':11,'target':12}),('list_vertices',{}),('list_edges',{})])
def test_queries_keep_graph_borrowed_and_no_future_API_result(operation,payload):
 data=S.execute_operation('graph',operation,payload,EDGE);trace=data['execution_trace']
 assert data['success'];assert len(data['history'])==len(EDGE)+1
 assert data['history'][-1]['source_contract']=='graph-book/v1'
 graph_objects=trace['steps'][0]['pedagogy']['instruction_state_before']['heap_nodes']
 for step in trace['steps'][:-1]:
  frame=step['pedagogy'];assert step['state_after']['last_result'] is None
  assert frame['memory_state']['heap_nodes']==graph_objects
  assert not frame['memory']['allocated'] and not frame['memory']['freed']
 assert trace['steps'][-1]['pedagogy']['instruction_event']['C_executed'] is False
 if operation in ['list_vertices','list_edges']:
  memory=trace['steps'][-1]['pedagogy']['memory_state'];assert memory['returned']==memory['graph']['v' if operation=='list_vertices' else 'a']

@pytest.mark.parametrize('operation,payload',[
 ('edge_weight',{'origin':12,'target':11}),('insert_edge',{'origin':'invalid','target':2}),
 ('generate_random_graph',{'vertices_count':0})])
def test_host_rejection_is_distinct_from_real_absent_cost_query(operation,payload):
 data=S.execute_operation('graph',operation,payload,EDGE);trace=data['execution_trace']
 assert not data['success']
 if operation=='edge_weight':
  assert trace['C_instruction_events'] and trace['execution_started']
  assert data['c_return']==0 and data['output']=='sin inicializar'
  assert data['history'][:-1]==EDGE
 else:
  assert trace['C_instruction_events']==[] and not trace['execution_started']
  assert data['history']==EDGE
 assert trace['steps'][0]['pedagogy']['initial_frame']['memory_state']['frames']==[]

@pytest.mark.parametrize('operation,payload',[('clear_graph',{}),('create_graph',{'directed':False})])
def test_caller_cleanup_records_retired_aliases_without_reading_them(operation,payload):
 data=S.execute_operation('graph',operation,payload,EDGE);steps=data['execution_trace']['steps']
 frees=[s for s in steps if s['pedagogy']['instruction_event']['phase']=='free']
 assert len(frees)==3
 for step in frees:
  memory=step['pedagogy']['memory_state'];retired={n['id'] for n in memory['retired_objects']}
  assert not retired.intersection(n['id'] for n in memory['heap_nodes'])
  assert all(s['pedagogy']['memory']['dangling_references_checked'] is False for s in steps)
 final=steps[-1]['pedagogy']['memory_state'];assert final['heap_nodes']==[] and final['frees']==3
 assert final['graph']=={'v':NULL,'a':NULL}

@pytest.mark.parametrize('failed', [1,2,3])
def test_raw_insertion_allocator_failure_is_atomic_in_canonical_C(failed):
 session=BookSession(fail_allocation=failed,trace=True)
 result=session.call('grafo_insertar_arco',[21,22,7])
 assert result['status']==1 and result['status_name']=='GRAFO_MEMORIA'
 assert result['graph_after']=={'vertices':[],'arcs':[],'marks':{}}
 assert result['memory']['allocation_attempts']==failed
 assert result['memory']['allocations']==result['memory']['frees']
 assert result['memory']['heap_nodes']==[] and result['memory']['graph']=={'v':NULL,'a':NULL}

def test_constructor_helper_call_stack_has_one_active_frame_and_initial_has_no_function():
 data=S.execute_operation('graph','insert_edge',{'origin':31,'target':32,'weight':6},[])
 trace=data['execution_trace'];initial=trace['steps'][0]['pedagogy']['initial_frame']
 assert initial['source']['function'] is None and initial['phase']['label']=='Estado inicial'
 nested=[s['pedagogy'] for s in trace['steps'] if len(s['pedagogy']['call_stack'])>1]
 assert nested
 for frame in nested:
  stack=frame['call_stack'];assert all(f['scope_status']=='suspendido' for f in stack[:-1])
  assert stack[-1]['scope_status'] in ['activo','terminado (contexto del retorno)']
  if frame['instruction_event']['function']!=stack[-1]['function']:
   assert frame['instruction_event']['phase'] in {'return','scope_exit'}
   assert any(f['function']==frame['instruction_event']['function'] for f in frame['completed_call_stack'])
