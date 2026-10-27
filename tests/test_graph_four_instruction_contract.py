"""Finite instruction contracts: scopes/ownership, API rejection and early return."""
from copy import deepcopy
from app.domain.graph.snapshot_pool import expand_graph_trace
import pytest
from app.domain.graph.book_c_subset import BookSession,Reference,UNINIT,NULL
from app.domain.graph.book_source import canonical_source

@pytest.mark.parametrize('algorithm',['bellman_ford','prim','dijkstra','kruskal'])
def test_actual_instruction_snapshots_ownership_and_scope_boundaries(algorithm):
 source=canonical_source()
 arcs=[(1,2,1),(2,3,2)]
 if algorithm in {'prim','kruskal'}:arcs += [(2,1,1),(3,2,2)]
 session=BookSession([1,2,3],arcs,marks={1:1,2:0,3:1},trace=True)
 machine=session.machine
 borrowed=deepcopy(machine.snapshot()['heap_nodes'])
 args=([1,3] if algorithm in {'bellman_ford','dijkstra'} else [1] if algorithm=='prim' else [])
 called=session.call('grafo_'+algorithm,args);result=called['returned'];final=machine.snapshot()
 assert called['status']==0
 snapshots=[(row['event'],row['before'],row['after']) for row in called['transitions']]
 assert snapshots[0][0]['C_executed'] is False and snapshots[0][1]['frames']==[]
 assert final['frames']==[] and final['returned']==result
 borrowed_ids={node['id'] for node in borrowed}
 assert [n for n in final['heap_nodes'] if n['id'] in borrowed_ids]==borrowed
 own=[n for n in final['heap_nodes'] if n['id'] not in borrowed_ids]
 assert own and all(n['kind']=='struct NodoA' for n in own)
 assert machine.allocations-machine.frees==len(own)
 retired={n['id'] for n in final['retired_objects']}
 assert retired.isdisjoint(n['id'] for n in final['heap_nodes'])
 for event,old,new in snapshots:
  if not event['C_executed']:
   assert event['line_index']==-1 and event['source_role']=='caller'
   continue
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
 with pytest.raises(ValueError,match='Indeterminate'):
  machine.read(Reference({'value':next(iter(retired))},'value','ListaArco','retired-native-allocation'))
 session.free_result(result,called['return_type'])
 assert machine.snapshot()['heap_nodes']==borrowed

@pytest.mark.parametrize('operation,payload,directed,weight',[
 ('run_dijkstra',{'start':1,'end':2},True,-1),
 ('run_bellman_ford',{'start':999,'end':2},True,1),
 ('run_prim',{'start':1},True,1),
 ('run_kruskal',{},True,1),
 ('run_dijkstra',{'start':'bad','end':2},True,1),
 ('run_bellman_ford',{'start':1},True,1),
])
def test_host_rejection_and_C_status_failure_are_distinct(client,operation,payload,directed,weight):
 def post(op,p):return client.post('/graph/graph/operate',json={'operation':op,'payload':p}).get_json()
 post('create_graph',{'directed':directed});prior=post('insert_edge',{'origin':1,'target':2,'weight':weight})['history']
 data=post(operation,payload);trace=expand_graph_trace(data['execution_trace']);assert not data['success']
 host_rejected=payload.get('start')=='bad' or (operation=='run_bellman_ford' and 'end' not in payload)
 if not host_rejected:
  assert data['c_status'] in {2,3,6} and trace['execution_started']
  assert trace['C_instruction_events'] and data['history'][:-1]==prior
  assert data['history'][-1]['source_contract']=='graph-book/v1'
  return
 assert data['history']==prior
 assert trace['execution_started'] is False and trace['C_instruction_events']==[] and len(trace['steps'])==1
 frame=trace['steps'][0]['pedagogy'];assert frame['instruction_event']['C_executed'] is False
 assert frame['call_stack']==frame['variables']==trace['steps'][0]['console']==[]
 assert frame['condition'] is None

@pytest.mark.parametrize('algorithm',['bellman_ford','dijkstra'])
def test_missing_integer_destination_preserves_no_route_and_C_early_return(client,algorithm):
 def post(op,p):return client.post('/graph/graph/operate',json={'operation':op,'payload':p}).get_json()
 post('create_graph',{'directed':True});post('insert_edge',{'origin':1,'target':2,'weight':1})
 data=post('run_'+algorithm,{'start':1,'end':999});assert not data['success'] and data['c_status']==2 and data['result']['path_edges']==[]
 trace=expand_graph_trace(data['execution_trace']);assert trace['execution_started'] and data['result']['path_arcs']==[]
 events=trace['C_instruction_events'];assert not any(e['phase']=='write' and e['name']=='u' for e in events)
 assert not any(e['function']=='grafo_costo_arco' for e in events)
 memory=trace['steps'][-1]['pedagogy']['memory_state']
 assert len(memory['heap_nodes'])==3 and memory['allocations']==memory['frees']
 assert memory['frames']==[]
 assert sum(h['operation']=='run_'+algorithm for h in data['history'])==1
 assert all(s['state_after']['last_result'] is None for s in trace['steps'][:-1])
