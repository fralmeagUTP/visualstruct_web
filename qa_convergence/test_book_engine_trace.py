import unittest,json,time,resource
from app.domain.graph.book_c_subset import BookSession
from app.domain.graph.book_source import canonical_source
from app.domain.graph.book_trace import BookTraceCollector,build_book_trace
from app.domain.graph.snapshot_pool import expand_graph_trace

def visual(vertices,arcs,marks=None):
 return {'structure':'graph','directed':True,'weighted':True,'nodes':[{'id':str(v),'label':str(v),'value':str(v),'marked':(marks or {}).get(v,0)} for v in vertices],'edges':[{'source':str(a),'target':str(b),'weight':w} for a,b,w in arcs],'metadata':{'vertices_count':len(vertices),'edges_count':len(arcs),'is_empty':not vertices},'last_operation':None,'last_result':None}
V=[1,2,3];A=[(1,2,7),(2,1,7),(2,3,8),(3,2,8)]
CASES=[('insert_vertex','grafo_insertar_vertice',[4]),('remove_vertex','grafo_eliminar_vertice',[2]),('run_bfs','grafo_bfs',[1]),('run_dfs','grafo_dfs',[1]),('run_dijkstra','grafo_dijkstra',[1,3]),('run_bellman_ford','grafo_bellman_ford',[1,3]),('run_prim','grafo_prim',[1]),('run_kruskal','grafo_kruskal',[])]
class BookTraceTests(unittest.TestCase):
 def test_streaming_and_replay_equal_no_missing_or_future_events(self):
  for operation,fn,args in CASES:
   with self.subTest(operation=operation):
    before=visual(V,A);c=BookTraceCollector(operation_name=operation,payload={},before_state=before);session=BookSession(V,A,callback=c.callback);r=session.call(fn,args)
    g=r['graph_after'];after=visual(g['vertices'][::-1],g['arcs'][::-1],g['marks']);after['last_result']={'status':r['status'],'result':r['result_items']}
    trace=c.finish(after_state=after,message='Resultado host separado')
    raw=BookSession(V,A,trace=True);raw.call(fn,args);replay=build_book_trace(operation_name=operation,payload={},before_state=before,after_state=after,execution={'transitions':raw.transitions})
    # Only the explicitly supplied host message differs.
    replay=build_book_trace(operation_name=operation,payload={},before_state=before,after_state=after,execution={'transitions':raw.transitions},message='Resultado host separado')
    self.assertEqual(trace,replay);self.assertEqual(len(trace['steps']),len(raw.transitions)+1);self.assertEqual(session.transitions,[]);self.assertEqual(session.machine.events,[])
    self.assertEqual(trace['source_code'],canonical_source());self.assertEqual(trace['steps'][0]['state_snapshot'],before);self.assertEqual(trace['steps'][-1]['state_after'],after)
    for i,step in enumerate(trace['steps']):
     event=step['pedagogy']['instruction_event']
     if event['C_executed']:self.assertEqual(step['line_text'],canonical_source().splitlines()[step['line_index']])
     else:self.assertIsNone(step['line_index']);self.assertEqual(step['line_text'],'')
     if i:self.assertEqual(trace['steps'][i-1]['state_after'],step['state_snapshot']);self.assertEqual(trace['steps'][i-1]['pedagogy']['instruction_state_after'],step['pedagogy']['instruction_state_before'])
     self.assertEqual(step['pedagogy']['memory_state'],step['pedagogy']['instruction_state_after'])
    encoded=trace.snapshot_pool.pack(trace);self.assertEqual(expand_graph_trace(encoded),trace)
 def test_multicall_and_error_keep_real_c_execution(self):
  before=visual([],[]);c=BookTraceCollector(operation_name='insert_edge',payload={},before_state=before);s=BookSession(callback=c.callback,fail_allocation=1)
  r=s.call('grafo_insertar_arco',[1,2,3]);self.assertEqual(r['status'],1)
  trace=c.finish(after_state=before,success=False,message='GRAFO_MEMORIA')
  self.assertTrue(trace['execution_started']);self.assertTrue(trace['C_instruction_events']);self.assertIn('GRAFO_MEMORIA',trace['steps'][-2]['pedagogy']['narration']['basic'])
  with self.assertRaisesRegex(ValueError,'finished'):c.finish(after_state=before)
 def test_rejection_has_no_fabricated_c(self):
  before=visual(V,A);c=BookTraceCollector(operation_name='run_dijkstra',payload={},before_state=before);trace=c.finish(after_state=before,success=False,message='Entrada rechazada antes del TAD')
  self.assertFalse(trace['execution_started']);self.assertEqual(trace['C_instruction_events'],[]);self.assertEqual(len(trace['steps']),1);self.assertIsNone(trace['steps'][0]['line_index'])
 def test_actual_trabajo_and_long_long_projection(self):
  a=[(1,2,2147483647),(2,3,2147483647)];before=visual(V,a);c=BookTraceCollector(operation_name='run_dijkstra',payload={},before_state=before);s=BookSession(V,a,callback=c.callback);r=s.call('grafo_dijkstra',[1,3]);trace=c.finish(after_state=before)
  distances=[step['pedagogy']['table']['distances'].get('3') for step in trace['steps']]
  self.assertIn(4294967294,distances);self.assertNotIn(2147483647+1,distances)
  self.assertTrue(any(v['type']=='Trabajo' for step in trace['steps'] for v in step['pedagogy']['variables']))
 def test_asymmetric_undirected_caller_does_not_invent_reverse_arc(self):
  before=visual([],[]);before['directed']=False;c=BookTraceCollector(operation_name='insert_edge',payload={},before_state=before);s=BookSession(callback=c.callback,fail_allocation=4)
  first=s.call('grafo_insertar_arco',[1,2,9]);second=s.call('grafo_insertar_arco',[2,1,9]);self.assertEqual(first['status'],0);self.assertEqual(second['status'],1)
  trace=c.finish(after_state=before,success=False)
  frame=trace['steps'][-2]['pedagogy'];self.assertEqual(frame['representation']['adjacency']['1'],[{'vertex':'2','weight':9}]);self.assertEqual(frame['representation']['adjacency']['2'],[]);self.assertTrue(frame['representation']['asymmetric_pairs'])

 def test_caller_ownership_and_cost_output_are_not_conflated(self):
  for op,fn,args,text in [('list_vertices','grafo_vertices',[],'lista prestada'),('successors','grafo_sucesores',[1],'lista propia'),('edge_weight','grafo_costo_arco',[1,2],'salida entera: 7')]:
   before=visual(V,A);c=BookTraceCollector(operation_name=op,payload={},before_state=before);s=BookSession(V,A,callback=c.callback);s.call(fn,args);t=c.finish(after_state=before)
   self.assertIn(text,t['steps'][-2]['pedagogy']['narration']['basic']);self.assertEqual(t['steps'][0]['pedagogy']['initial_frame']['instruction_event']['phase'],'initial')

if __name__=='__main__':unittest.main(verbosity=2)
