"""Approved private atomic-successor failure contract; no public helper changes."""
from copy import deepcopy
import pytest
from app.domain.graph.c_algorithm_subset import Program,GraphMachine,NULL
from app.services.c_code_service import CCodeService
from _audit_graph_four_instruction_observer import cases_from_baseline

@pytest.mark.parametrize('algorithm,attempt',[(a,i) for a,n in [('prim',13),('dijkstra',9)] for i in range(1,n+1)])
def test_every_reached_allocation_failure_aborts_and_frees_all_owned(algorithm,attempt):
 case=cases_from_baseline(algorithm)[1 if algorithm=='prim' else 2];arcs=[]
 for a,b,w in case['e']:
  arcs.append((a,b,w))
  if not case.get('directed',True) and a!=b:arcs.append((b,a,w))
 source=CCodeService._build_graph_data()['operations']['run_'+algorithm]
 machine=GraphMachine(Program(source),case['v'],arcs,marks={v:i%2 for i,v in enumerate(case['v'])},fail_allocation=attempt)
 borrowed=deepcopy(machine.snapshot()['heap_nodes']);args=[machine.graph,case['start']]+([case['end']] if algorithm=='dijkstra' else [])
 assert machine.invoke('grafo_'+algorithm,args)==NULL
 assert machine.allocations==machine.frees
 assert machine.snapshot()['heap_nodes']==borrowed and machine.snapshot()['frames']==[]
 assert machine.attempts==attempt or attempt<= (5 if algorithm=='prim' else 4)
 failures=[e for e in machine.events if e['phase']=='allocate' and e['value']['pointer']==NULL];assert len(failures)==1
 helper_failure=[e for e in machine.events if e['function']=='grafo_sucesores_atomicos' and e['phase']=='write' and e['name']=='*correcto' and e['value']==0]
 if attempt > (5 if algorithm=='prim' else 4) and helper_failure:
  assert not any(e['phase']=='write' and e['name'] in {'arbol','camino'} and e['value']!=NULL for e in machine.events)

@pytest.mark.parametrize('algorithm',['prim','dijkstra'])
def test_complete_successor_result_and_integer_contract_preserved(algorithm):
 case=cases_from_baseline(algorithm)[1 if algorithm=='prim' else 2];arcs=[]
 for a,b,w in case['e']:
  arcs.append((a,b,w))
  if not case.get('directed',True) and a!=b:arcs.append((b,a,w))
 m=GraphMachine(Program(CCodeService._build_graph_data()['operations']['run_'+algorithm]),case['v'],arcs)
 pointer=m.invoke('grafo_'+algorithm,[m.graph,case['start']]+([case['end']] if algorithm=='dijkstra' else []));result=[]
 while pointer!=NULL:
  fields=m.heap[pointer]['fields'];result.append([fields['origen'],fields['destino'],fields['costo']]);pointer=fields['sig']
 assert result==([[3,2,2],[1,3,1]] if algorithm=='prim' else [[1,3,1],[3,2,1]])
 assert m.allocations-m.frees==2
