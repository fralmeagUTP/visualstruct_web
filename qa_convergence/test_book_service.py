import unittest
from copy import deepcopy
from unittest.mock import patch
from app.services.graph_structure_service import GraphStructureService as S

class BookServiceTests(unittest.TestCase):
    def test_generic_old_graph_planner_is_not_a_fallback(self):
        from app.services.execution_trace_service import ExecutionTraceService
        with self.assertRaisesRegex(ValueError,'BookTraceCollector'):
            ExecutionTraceService.build_trace(structure_id='graph',operation_name='run_bfs',
                payload={'start':1},didactic_data={},before_state={},after_state={},
                success=True,message='',mutates=False)

    def test_history_legacy_never_replayed(self):
        history=[{'operation':'insert_edge','payload':{'origin':1,'target':2,'weight':7},'extra':{'keep':True}}]
        before=deepcopy(history)
        with patch.object(S,'_rebuild_adapter',side_effect=AssertionError('legacy replay')):
            model=S.get_view_model('graph',history)
            r=S.execute_operation('graph','insert_vertex',{'vertex':3},history)
        self.assertTrue(model['suspended']);self.assertNotIn('nodes',model['visual_state'])
        self.assertTrue(r['preserve_session']);self.assertIsNone(r['execution_trace'])
        self.assertEqual(r['history'],before);self.assertEqual(history,before);self.assertEqual(model['main_c'],'')

    def test_invalid_marked_history_is_not_truncated_or_regenerated(self):
        for operation,payload in [('insert_vertex',{'vertex':2147483648}),
                                  ('generate_random_graph',{'vertices_count':3})]:
            h=[{'operation':operation,'payload':payload,'source_contract':'graph-book/v1'}]
            before=deepcopy(h)
            model=S.get_view_model('graph',h)
            self.assertTrue(model['suspended']);self.assertEqual(model['main_c'],'')
            r=S.execute_operation('graph','insert_vertex',{'vertex':2},h)
            self.assertTrue(r['preserve_session']);self.assertEqual(r['history'],before)
            self.assertEqual(h,before)

    def test_failed_c_is_history_and_trace_not_preflight(self):
        h=[]
        for op,p in [('insert_edge',dict(origin=1,target=2,weight=7)),('run_bfs',{'start':99})]:
            r=S.execute_operation('graph',op,p,h);h=r['history']
        self.assertFalse(r['success']);self.assertEqual(r['c_status'],2)
        self.assertTrue(r['execution_trace']['execution_started'])
        self.assertGreater(len(r['execution_trace']['steps']),1)
        self.assertEqual(len(h),2)
        self.assertTrue(all(x['source_contract']=='graph-book/v1' for x in h))
        self.assertEqual(S.get_view_model('graph',h)['visual_state'],r['visual_state'])

    def test_reverse_failure_replays_actual_partial_graph(self):
        r=S.execute_operation('graph','insert_edge',dict(origin=1,target=2,weight=7,fail_allocation=4),[])
        self.assertFalse(r['success'])
        self.assertEqual(len(r['visual_state']['c_arcs']),1)
        self.assertEqual(S.get_view_model('graph',r['history'])['visual_state'],r['visual_state'])

    def test_pre_c_range_reject_preserves_history(self):
        r=S.execute_operation('graph','insert_vertex',{'vertex':2147483648},[])
        self.assertFalse(r['success']);self.assertTrue(r['preserve_session'])
        self.assertFalse(r['execution_trace']['execution_started']);self.assertEqual(r['history'],[])

if __name__=='__main__':unittest.main()
