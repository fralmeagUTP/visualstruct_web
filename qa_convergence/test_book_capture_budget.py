import unittest
from copy import deepcopy
from unittest.mock import patch
from app.adapters.graph_adapter import GraphAdapter
from app.services.graph_structure_service import GraphStructureService as S

class CaptureBudgetTests(unittest.TestCase):
    def test_exact_boundary_and_normal_fallback(self):
        payload={'origin':1,'target':2,'weight':7}
        a=GraphAdapter();a._book_event_limit=4000;a.execute('insert_edge',deepcopy(payload))
        count=a._last_book_execution['event_count']
        self.assertGreater(count,20)
        with patch('app.domain.graph.trace_budget.MAX_TRACE_EVENTS',count):
            r=S.execute_operation('graph','insert_edge',deepcopy(payload),[])
            self.assertTrue(r['success']);self.assertTrue(r['trace_available'])
            self.assertEqual(len(r['execution_trace']['steps']),count+1)
        with patch('app.domain.graph.trace_budget.MAX_TRACE_EVENTS',count-1):
            # Preflight is count-only: rejecting a capture never snapshots C memory.
            with patch('app.domain.graph.book_c_subset.GraphMachine.snapshot',side_effect=AssertionError('snapshot in preflight')):
                denied=S.execute_operation('graph','insert_edge',deepcopy(payload),[])
            self.assertTrue(denied['preserve_session']);self.assertEqual(denied['history'],[])
            self.assertIsNone(denied['execution_trace'])
            normal=S.execute_operation('graph','insert_edge',deepcopy(payload),[],execution_mode='normal')
        self.assertTrue(normal['success']);self.assertFalse(normal['trace_available'])
        self.assertIn('se ejecutó en modo normal',normal['trace_unavailable_reason'])
        self.assertNotIn('Puedes ejecutar',normal['trace_unavailable_reason'])
        self.assertIsNone(normal['execution_trace']);self.assertEqual(normal['visual_state'],r['visual_state'])
        self.assertEqual(normal['history'],r['history']);self.assertEqual(normal['main_c'],r['main_c'])

    def test_normal_c_failure_without_trace_is_still_executed_history(self):
        h=[]
        for vertex in [1,2]:
            h=S.execute_operation('graph','insert_vertex',{'vertex':vertex},h)['history']
        with patch('app.domain.graph.trace_budget.MAX_TRACE_EVENTS',1):
            result=S.execute_operation('graph','run_kruskal',{},h,execution_mode='normal')
        self.assertFalse(result['success']);self.assertEqual(result['c_status'],5)
        self.assertTrue(result['execution_started']);self.assertIsNone(result['execution_trace'])
        self.assertEqual(len(result['history']),3)
        self.assertIn('grafo_kruskal',result['main_c'])

    def test_random_seed_preflight_exact_replay(self):
        r=S.execute_operation('graph','generate_random_graph',{'vertices_count':3},[],execution_mode='normal')
        self.assertIsInstance(r['history'][0]['payload']['seed'],int)
        self.assertEqual(S.get_view_model('graph',r['history'])['visual_state'],r['visual_state'])

if __name__=='__main__':unittest.main()
