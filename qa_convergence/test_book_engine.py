import unittest
from app.domain.graph.book_c_subset import BookSession,run_book,Program,GraphMachine,Reference,NULL,UNINIT
from app.domain.graph.book_source import canonical_source,HASHES,STATUS_NAMES

V=[1,2,3];A=[(1,2,7),(2,1,7),(2,3,8),(3,2,8)]
ALGORITHMS=[('grafo_bfs',[1]),('grafo_dfs',[1]),('grafo_dijkstra',[1,3]),('grafo_bellman_ford',[1,3]),('grafo_prim',[1]),('grafo_kruskal',[])]
class BookEngineTests(unittest.TestCase):
 def test_all_functions_parse_and_source_fail_closed(self):
  p=Program(canonical_source());self.assertEqual(len(p.functions),44)
  with self.assertRaisesRegex(ValueError,'byte-exact'):Program(canonical_source()+'\n')
 def test_construction_order_and_out_parameters(self):
  s=BookSession();r=s.call('grafo_insertar_arco',[1,2,7]);self.assertEqual(r['status'],0);self.assertEqual(r['graph_after'],{'vertices':[2,1],'arcs':[[1,2,7]],'marks':{2:0,1:0}})
  r=s.call('grafo_costo_arco',[1,2]);self.assertEqual((r['returned'],r['output']),(1,7))
  r=s.call('grafo_costo_arco',[1,9]);self.assertEqual((r['returned'],r['output']),(0,UNINIT))
  r=s.call('grafo_costo_arco',[1,2],output_pointer=False);self.assertEqual(r['returned'],0)
  r=s.call('grafo_insertar_arco',[1,2,-1]);self.assertEqual(r['graph_after']['arcs'],[[1,2,-1]])
  r=s.call('grafo_eliminar_vertice',[1]);self.assertEqual(r['graph_after']['vertices'],[2]);self.assertEqual(r['graph_after']['arcs'],[])
  r=s.call('grafo_destruir');self.assertEqual(r['graph_after']['vertices'],[]);self.assertEqual(r['memory']['heap_nodes'],[])
 def test_atomic_insert_failures(self):
  for vertices,arcs,args in [([],[],[1,2,7]),([1],[],[1,2,7]),([],[],[1,1,7]),(V,A,[4,5,7])]:
   good=run_book('grafo_insertar_arco',vertices=vertices,arcs=arcs,arguments=args)
   for fault in range(1,good['memory']['allocation_attempts']+1):
    with self.subTest(vertices=vertices,args=args,fault=fault):
     r=run_book('grafo_insertar_arco',vertices=vertices,arcs=arcs,arguments=args,fail_allocation=fault)
     self.assertEqual(r['status'],1);self.assertEqual(r['graph_after']['vertices'],vertices[::-1]);self.assertEqual(r['graph_after']['arcs'],[list(a) for a in arcs[::-1]])
     self.assertEqual(len(r['memory']['heap_nodes']),len(vertices)+len(arcs))
 def test_algorithm_failure_cleanup_and_atomic_marks(self):
  for fn,args in ALGORITHMS+[('grafo_sucesores',[2]),('grafo_predecesores',[2])]:
   good=run_book(fn,vertices=V,arcs=A,arguments=args,marks={1:1,2:0,3:0})
   self.assertEqual(good['status'],0)
   for fault in range(1,good['memory']['allocation_attempts']+1):
    with self.subTest(fn=fn,fault=fault):
     r=run_book(fn,vertices=V,arcs=A,arguments=args,marks={1:1,2:0,3:0},fail_allocation=fault)
     self.assertEqual(r['status'],1);self.assertEqual(r['returned'],NULL);self.assertEqual(len(r['memory']['heap_nodes']),len(V)+len(A));self.assertEqual(r['graph_after']['marks'],{1:1,2:0,3:0})
 def test_result_ownership_and_explicit_free(self):
  for fn,args in ALGORITHMS+[('grafo_sucesores',[2]),('grafo_predecesores',[2])]:
   s=BookSession(V,A);r=s.call(fn,args);self.assertEqual(r['ownership'],'owned');self.assertEqual(s.free_result(r['returned'],r['return_type']),NULL);self.assertEqual(len(s.machine.heap),len(V)+len(A))
  s=BookSession(V,A)
  for fn in ['grafo_vertices','grafo_arcos']:
   r=s.call(fn);self.assertEqual(r['ownership'],'borrowed')
   with self.assertRaisesRegex(ValueError,'borrowed'):s.free_result(r['returned'],r['return_type'])
 def test_status_distinguishes_null_empty_and_errors(self):
  cases=[('grafo_dijkstra',[1,1],[1],[],0),('grafo_prim',[1],[1],[],0),('grafo_kruskal',[],[1],[],0),('grafo_bfs',[1],[],[],2),('grafo_dfs',[9],V,A,2),('grafo_dijkstra',[1,3],V,[(1,2,1)],2),('grafo_dijkstra',[1,3],V,[(1,2,-1)],3),('grafo_bellman_ford',[1,3],V,[(1,2,1),(2,3,-2),(3,2,1)],4),('grafo_prim',[1],V,[],5),('grafo_kruskal',[],V,[],5),('grafo_prim',[1],V,[(1,2,1)],6),('grafo_kruskal',[],V,[(1,2,1)],6)]
  for fn,args,vertices,arcs,status in cases:
   with self.subTest(fn=fn,args=args,arcs=arcs,status=status):
    r=run_book(fn,vertices=vertices,arcs=arcs,arguments=args);self.assertEqual(r['status'],status);self.assertEqual(r['returned'],NULL)
 def test_long_long_and_safe_sum(self):
  for fn in ['grafo_dijkstra','grafo_bellman_ford']:
   r=run_book(fn,vertices=V,arcs=[(1,2,2147483647),(2,3,2147483647)],arguments=[1,3]);self.assertEqual(r['status'],0);self.assertEqual(sum(x[2] for x in r['result_items']),4294967294)
  s=BookSession();holder={'value':123};ref=Reference(holder,'value','long long','qa:out')
  for x,y,ok in [((1<<63)-1,1,0),(-(1<<63),-1,0),((1<<63)-2,1,1),(-(1<<63)+1,-1,1)]:
   holder['value']=123;self.assertEqual(s.machine.invoke('sumar_seguro',[x,y,ref]),ok);self.assertEqual(holder['value'],x+y if ok else 123)
 def test_trace_and_normal_identical_semantics(self):
  for fn,args in [('grafo_insertar_arco',[3,4,2]),('grafo_bfs',[1]),('grafo_dijkstra',[1,3])]:
   a=run_book(fn,vertices=V,arcs=A,arguments=args);b=run_book(fn,vertices=V,arcs=A,arguments=args,trace=True)
   for key in ['returned','status','output','graph_after','result_items','ownership','memory']:self.assertEqual(a[key],b[key],key)
   self.assertEqual(a['events'],[]);self.assertTrue(b['events']);self.assertEqual(len(b['events']),len(b['transitions']))
   self.assertTrue(all(e['line_index']>=0 if e['C_executed'] else e['line_index']==-1 for e in b['events']))
 def test_optional_status_and_print(self):
  s=BookSession([7],[]);r=s.call('grafo_bfs',[7],state_pointer=False);self.assertIsNone(r['status']);self.assertEqual(r['result_items'],[7]);r=s.call('grafo_imprimir_vertices');self.assertIn('7',r['stdout'])

class BookSafetyTests(unittest.TestCase):
 def test_dead_heap_and_stack_references_are_rejected(self):
  from app.domain.graph.book_c_subset import Token
  s=BookSession();m=s.machine
  for owner in [{'_alive':False},{'alive':False}]:
   ref=Reference({'value':7},'value','int','expired',owner)
   with self.assertRaisesRegex(ValueError,'Expired'):m.read(ref)
  with self.assertRaisesRegex(ValueError,'Uninitialized'):m.read(Reference({'value':UNINIT},'value','int','unset'))
  r=s.call('grafo_insertar_vertice',[1]);pointer=m.graph['v'];s.call('grafo_eliminar_vertice',[1])
  with self.assertRaisesRegex(ValueError,'Indeterminate'):m.read(Reference({'value':pointer},'value','ListaVertice','dangling'))
 def test_seed_validation_and_wide_integer_encoding(self):
  for vertices,arcs in [([1,1],[]),([1],[(1,2,3)]),([2147483648],[]),([1,2],[(1,2,3),(1,2,4)])]:
   with self.assertRaises(ValueError):BookSession(vertices,arcs)
  m=BookSession().machine
  self.assertEqual(m.encoded((1<<63)-1),{'exact_integer':'9223372036854775807'})
  with self.assertRaisesRegex(ValueError,'overflow'):m.cast(1<<63,'long long')
 def test_real_scope_lifetime_and_external_state_snapshot(self):
  s=BookSession(trace=True);r=s.call('grafo_insertar_arco',[1,2,3]);self.assertEqual(r['memory']['external']['estado']['value'],0)
  self.assertTrue(any(t['after']['external']['estado']['value']==0 for t in r['transitions']))
  self.assertEqual(r['memory']['frames'],[])
  # The original source position is retained, rather than an AST pretty-print.
  for event in r['events']:
   if event['C_executed']:self.assertTrue(r['source_code'].splitlines()[event['line_index']].strip())

 def test_abi_profile_matches_native_compiler(self):
  import subprocess,tempfile
  from pathlib import Path
  root=Path(__file__).resolve().parents[1]
  code='#include "'+str(root/'docs/tads_C/tad_grafo.c')+'"\n'
  for typ,size in [('int',4),('long long',8),('size_t',8),('GrafoEstado',4),('Grafo',16),('ListaVertice',8),('ListaArco',8),('struct NodoV',24),('struct NodoA',24),('Trabajo',48),('Conjunto',16)]:
   code+=f'_Static_assert(sizeof({typ}) == {size}, "ABI {typ}");\n'
  code+='int main(void) { return 0; }\n'
  with tempfile.TemporaryDirectory() as directory:
   src=Path(directory)/'abi.c';exe=Path(directory)/'abi';src.write_text(code)
   subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic',str(src),'-o',str(exe)],check=True,capture_output=True)
   subprocess.run([str(exe)],check=True)

class BookTraceContinuityTests(unittest.TestCase):
 def test_each_snapshot_and_multicall_boundary_is_explicit(self):
  for fault in [None,1,2,3]:
   session=BookSession(trace=True,fail_allocation=fault)
   session.call('grafo_insertar_arco',[1,2,3]);session.call('grafo_insertar_arco',[2,1,3]);session.call('grafo_destruir');session.call('grafo_crear')
   for previous,current in zip(session.transitions,session.transitions[1:]):self.assertEqual(previous['after'],current['before'],current['event'])
   self.assertEqual(session.transitions[-1]['after'],session.machine.snapshot())
   host=[t['event'] for t in session.transitions if not t['event']['C_executed']]
   self.assertEqual(len(host),8);self.assertTrue(all(e['line_index']==-1 and e['source_role']=='caller' for e in host))

if __name__=='__main__':unittest.main(verbosity=2)
