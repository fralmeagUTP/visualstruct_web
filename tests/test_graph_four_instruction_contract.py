"""Finite instruction contracts: scopes/ownership, API rejection and early return."""
from copy import deepcopy
from app.domain.graph.snapshot_pool import expand_graph_trace
import pytest
from app.domain.graph.c_algorithm_subset import Program,GraphMachine,UNINIT
from app.services.c_code_service import CCodeService

@pytest.mark.parametrize('algorithm',['bellman_ford','prim','dijkstra','kruskal'])
def test_actual_instruction_snapshots_ownership_and_scope_boundaries(algorithm):
 source=CCodeService._build_graph_data()['operations']['run_'+algorithm]
 arcs=[(1,2,1),(2,3,2)]
 if algorithm in {'prim','kruskal'}:arcs += [(2,1,1),(3,2,2)]
 snapshots=[]
 machine=GraphMachine(Program(source),[1,2,3],arcs,marks={1:1,2:0,3:1},callback=lambda event,old,new:snapshots.append((deepcopy(event),old,new)))
 borrowed=deepcopy(machine.snapshot()['heap_nodes'])
 args=[machine.graph]+([1,3] if algorithm in {'bellman_ford','dijkstra'} else [1] if algorithm=='prim' else [])
 result=machine.invoke('grafo_'+algorithm,args);final=machine.snapshot()
 assert snapshots[0][0]['phase']=='enter' and snapshots[0][1]['frames']==[]
 assert final['frames']==[] and final['returned']==result
 assert [n for n in final['heap_nodes'] if n['borrowed']]==borrowed
 own=[n for n in final['heap_nodes'] if not n['borrowed']]
 assert own and all(n['kind']=='struct NodoA' for n in own)
 assert machine.allocations-machine.frees==len(own)
 retired={n['id'] for n in final['retired_objects']}
 assert retired.isdisjoint(n['id'] for n in final['heap_nodes'])
 for event,old,new in snapshots:
  assert source.splitlines()[event['line_index']]
  if event['phase']=='enter':assert len(new['frames'])==len(old['frames'])+1
  if event['phase']=='return':assert new['frames'][-1]['status']=='returning'
  if event['phase']=='allocate' and event['value']['pointer']!='NULL':
   node=next(n for n in new['heap_nodes'] if n['id']==event['value']['pointer'])
   if 'items' in node:
    assert all(v==0 for v in node['items']) if event['value']['zeroed'] else all(v==UNINIT for v in node['items'])
  if event['phase']=='free' and event['value']!='NULL':
   assert event['value'] not in {n['id'] for n in new['heap_nodes']}
   assert event['value'] in {n['id'] for n in new['retired_objects']}
 # Retired identities are records, never dereferenceable memory.
 with pytest.raises(ValueError):machine.pointee(next(iter(retired)))

@pytest.mark.parametrize('operation,payload,directed,weight',[
 ('run_dijkstra',{'start':1,'end':2},True,-1),
 ('run_bellman_ford',{'start':999,'end':2},True,1),
 ('run_prim',{'start':1},True,1),
 ('run_kruskal',{},True,1),
 ('run_dijkstra',{'start':'bad','end':2},True,1),
 ('run_bellman_ford',{'start':1},True,1),
])
def test_api_rejection_has_no_fabricated_C_execution(client,operation,payload,directed,weight):
 def post(op,p):return client.post('/graph/graph/operate',json={'operation':op,'payload':p}).get_json()
 post('create_graph',{'directed':directed});prior=post('insert_edge',{'origin':1,'target':2,'weight':weight})['history']
 data=post(operation,payload);trace=expand_graph_trace(data['execution_trace']);assert not data['success'] and data['history']==prior
 assert trace['execution_started'] is False and trace['C_instruction_events']==[] and len(trace['steps'])==1
 frame=trace['steps'][0]['pedagogy'];assert frame['instruction_event']['C_executed'] is False
 assert frame['call_stack']==frame['variables']==trace['steps'][0]['console']==[]
 assert frame['condition'] is None

@pytest.mark.parametrize('algorithm',['bellman_ford','dijkstra'])
def test_missing_integer_destination_preserves_no_route_and_C_early_return(client,algorithm):
 def post(op,p):return client.post('/graph/graph/operate',json={'operation':op,'payload':p}).get_json()
 post('create_graph',{'directed':True});post('insert_edge',{'origin':1,'target':2,'weight':1})
 data=post('run_'+algorithm,{'start':1,'end':999});assert data['success'] and data['result']['path_edges']==[]
 trace=expand_graph_trace(data['execution_trace']);assert trace['execution_started'] and trace['returned_arcs']==[]
 events=trace['C_instruction_events'];assert not any(e['phase']=='write' and e['name']=='u' for e in events)
 assert not any(e['function']=='grafo_costo_arco' for e in events)
 assert trace['numeric_C_memory']['heap_nodes'] and all(n['borrowed'] for n in trace['numeric_C_memory']['heap_nodes'])
 assert trace['numeric_C_memory']['frames']==[]
 assert sum(h['operation']=='run_'+algorithm for h in data['history'])==1
 assert all(s['state_after']['last_result'] is None for s in trace['steps'][:-1])
