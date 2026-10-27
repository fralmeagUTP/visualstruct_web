"""Integration-only QA: the independent native suite certifies the underlying C engine."""
import unittest
from copy import deepcopy
from unittest.mock import patch
from app.adapters.graph_adapter import GraphAdapter
from app.domain.graph.book_c_subset import BookSession
from app.domain.graph.book_application import FUNCTIONS
from app.domain.graph.tad_wrappers import Grafo


class BookAdapterTests(unittest.TestCase):
    def seeded(self, directed=False):
        a=GraphAdapter();a.execute('create_graph',{'directed':directed})
        for x,y,w in [(1,2,1500000000),(2,3,1500000000),(1,3,2000000000)]:
            a.execute('insert_edge',dict(origin=x,target=y,weight=w))
        return a

    def test_all_operations_match_c_and_storage_order(self):
        payloads={'insert_vertex':{'vertex':4},'remove_vertex':{'vertex':2},
          'insert_edge':dict(origin=4,target=2,weight=7),'remove_edge':dict(origin=1,target=2),
          'exists_vertex':{'vertex':2},'exists_edge':dict(origin=1,target=2),
          'list_vertices':{},'list_edges':{},'neighbors':{'vertex':2},'edge_weight':dict(origin=1,target=2),
          'run_bfs':{'start':1},'run_dfs':{'start':1},'run_dijkstra':dict(start=1,end=3),
          'run_bellman_ford':dict(start=1,end=3),'run_prim':{'start':1},'run_kruskal':{}}
        for operation,payload in payloads.items():
            with self.subTest(operation=operation):
                a=self.seeded(True);g=a.graph._g
                expected=BookSession(g._vertices,g._arcos,g._marcas).call(FUNCTIONS[operation][0],[payload[k] for k in FUNCTIONS[operation][1]])
                result=a.execute(operation,deepcopy(payload));call=a._last_book_execution['calls'][0]
                for key in ['returned','status','output','result_items','ownership','graph_after']:
                    self.assertEqual(call[key],expected[key])
                self.assertEqual(a.graph._g._vertices,list(reversed(expected['graph_after']['vertices'])))
                self.assertEqual(a.graph._g._arcos,[tuple(x) for x in reversed(expected['graph_after']['arcs'])])
                self.assertEqual(result['c_status'],expected['status'])
        a=self.seeded();a.execute('clear_graph',{});self.assertEqual(a.graph._g._vertices,[])
        a.execute('generate_random_graph',{'vertices_count':4,'seed':321});self.assertEqual(len(a.graph._g._vertices),4)

    def test_zero_absent_self_longlong_and_disconnected(self):
        a=GraphAdapter();a.execute('insert_edge',dict(origin=1,target=2,weight=0))
        r=a.execute('edge_weight',dict(origin=1,target=2));self.assertEqual((r['c_return'],r['result']),(1,0))
        r=a.execute('edge_weight',dict(origin=1,target=9));self.assertEqual((r['c_return'],r['output']),(0,'sin inicializar'))
        self.assertIsNone(r['c_status'])
        r=a.execute('run_dijkstra',dict(start=1,end=1));self.assertEqual((r['c_return'],r['c_status'],r['result']['path']),('NULL',0,[1]))
        a.execute('insert_vertex',{'vertex':9})
        for op,p in [('run_prim',{'start':1}),('run_kruskal',{})]:
            r=a.execute(op,p);self.assertEqual(r['c_status'],5);self.assertIsNone(r['result']['total_weight']);self.assertEqual(r['result']['mst_edges'],[])
        b=GraphAdapter();b.execute('create_graph',{'directed':True})
        for x,y in [(1,2),(2,3)]:b.execute('insert_edge',dict(origin=x,target=y,weight=1500000000))
        for op in ['run_dijkstra','run_bellman_ford']:
            self.assertEqual(b.execute(op,dict(start=1,end=3))['result']['distance_to_destination'],3000000000)

    def test_failure_policy_atomic_first_and_partial_inverse(self):
        for failure in range(1,5):
            a=GraphAdapter();r=a.execute('insert_edge',dict(origin=1,target=2,weight=7,fail_allocation=failure))
            self.assertFalse(r['success']);self.assertEqual(r['c_status'],1)
            if failure<=3:self.assertEqual(a.graph._g._arcos,[]);self.assertEqual(len(a._last_book_execution['calls']),1)
            else:
                self.assertEqual(a.graph._g._arcos,[(1,2,7)])
                self.assertEqual(a.to_visual_state()['asymmetric_pairs'],[{'source':'1','target':'2','weight':7}])
        a=self.seeded();before=deepcopy(a.graph._g._marcas)
        r=a.execute('run_bfs',{'start':1,'fail_allocation':1})
        self.assertEqual(r['c_status'],1);self.assertEqual(a.graph._g._marcas,before)

    def test_owned_cleanup_and_streaming_no_raw_accumulation(self):
        a=self.seeded();events=[];a._book_callback=lambda event,before,after:events.append(event)
        a.execute('run_bfs',{'start':1});execution=a._last_book_execution
        self.assertGreater(len(events),50);self.assertEqual(execution['transitions'],[])
        self.assertTrue(execution['calls'][0]['released_by_caller'])
        self.assertTrue(any(e.get('function')=='grafo_liberar_vertices' for e in events))
        self.assertEqual(len(execution['memory_after']['heap_nodes']),len(a.graph._g._vertices)+len(a.graph._g._arcos))
        self.assertNotIn('memory',execution['calls'][0]);self.assertNotIn('events',execution['calls'][0])
        a.execute('list_vertices',{});self.assertNotIn('released_by_caller',a._last_book_execution['calls'][0])

    def test_no_old_semantic_calls_and_replay_seed(self):
        names=['insertar_vertice','eliminar_vertice','insertar_arista','eliminar_arista','bfs','dfs','dijkstra','bellman_ford','prim','kruskal','vecinos','peso']
        patches=[patch.object(Grafo,n,side_effect=AssertionError('legacy execution')) for n in names]
        for p in patches:p.start()
        try:
            a=GraphAdapter();p={'vertices_count':4,'seed':88};a.execute('generate_random_graph',p)
            b=GraphAdapter();b.execute('generate_random_graph',deepcopy(p));self.assertEqual(a.graph._g._arcos,b.graph._g._arcos)
            for op in ['run_bfs','run_dfs','run_prim']:a.execute(op,{'start':1})
            for op in ['run_dijkstra','run_bellman_ford']:a.execute(op,{'start':1,'end':4})
            a.execute('run_kruskal',{});a.execute('remove_vertex',{'vertex':2})
        finally:
            for p in patches:p.stop()

    def test_error_states_and_every_bfs_allocation(self):
        a=self.seeded(True)
        self.assertEqual(a.execute('run_bfs',{'start':99})['c_status'],2)
        self.assertEqual(a.execute('run_prim',{'start':1})['c_status'],6)
        a.execute('insert_edge',dict(origin=3,target=2,weight=-2000000000))
        self.assertEqual(a.execute('run_dijkstra',dict(start=1,end=3))['c_status'],3)
        self.assertEqual(a.execute('run_bellman_ford',dict(start=1,end=3))['c_status'],4)
        a=self.seeded();a.execute('run_bfs',{'start':1})
        attempts=a._last_book_execution['memory_after']['allocation_attempts']
        self.assertGreater(attempts,0)
        for failure in range(1,attempts+1):
            a=self.seeded();before=deepcopy(a.graph._g._marcas)
            result=a.execute('run_bfs',{'start':1,'fail_allocation':failure})
            self.assertEqual(result['c_status'],1)
            self.assertEqual(a.graph._g._marcas,before)
            self.assertEqual(len(a._last_book_execution['memory_after']['heap_nodes']),len(a.graph._g._vertices)+len(a.graph._g._arcos))

    def test_invalid_input_precedes_execution(self):
        a=self.seeded();before=deepcopy(a.to_visual_state());execution=a._last_book_execution
        for op,p in [('insert_vertex',{'vertex':2147483648}),('insert_edge',dict(origin=1,target=2,weight=1.5)),('generate_random_graph',{'vertices_count':16}),('run_bfs',{'start':1,'fail_allocation':0})]:
            with self.assertRaises(ValueError):a.execute(op,p)
            self.assertEqual(a.to_visual_state(),before);self.assertIs(a._last_book_execution,execution)

if __name__=='__main__':unittest.main()
