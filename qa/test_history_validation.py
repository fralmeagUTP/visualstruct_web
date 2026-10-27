"""Legacy out-of-C-range history remains inspectable, never silently migrated."""
import copy
import tempfile
import unittest
from app import create_app
from app.config import Config
from app.services.structure_service import StructureService
from app.services.hierarchical_structure_service import HierarchicalStructureService
from app.services.session_service import SESSION_KEY

class HistoryValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cache=tempfile.TemporaryDirectory(prefix='visualstruct-history-')
        class T(Config):
            TESTING=True
            SESSION_CACHE_DIR=cls.cache.name
        cls.app=create_app(T)
    @classmethod
    def tearDownClass(cls):cls.cache.cleanup()
    def test_legacy_states_preserved_new_execution_blocked_and_reset_recovers(self):
        cases=[('sequential','stack','apilar'),('sequential','queue','encolar'),
            ('sequential','priority_queue','encolar'),('sequential','linked_list','insertar_final'),
            ('sequential','circular_list','insertar_final'),('sequential','sublist','insertar_padre'),
            ('hierarchical','abb','insertar'),('hierarchical','avl','insertar'),('hierarchical','binary_heap','insertar')]
        for module,kind,operation in cases:
            with self.subTest(module=module,kind=kind):
                key='parent' if kind=='sublist' else 'value'
                history=[{'operation':operation,'payload':{key:v,**({'priority':1} if kind=='priority_queue' else {})}} for v in [10,2147483648,20]]
                original=copy.deepcopy(history)
                service=StructureService if module=='sequential' else HierarchicalStructureService
                view=service.get_view_model(kind,history)
                self.assertEqual(view['history'],original)
                self.assertFalse(view['history_compatible'])
                self.assertIn('historial',view['history_warning'])
                payload={key:30,**({'priority':1} if kind=='priority_queue' else {})}
                response=service.execute_operation(structure_id=kind,operation_name=operation,payload=payload,history=history)
                self.assertFalse(response['success']);self.assertEqual(response['history'],original)
                self.assertEqual(response['visual_state'],view['visual_state'])
                self.assertEqual(response['execution_trace']['steps'],[])
                self.assertFalse(response['execution_trace']['execution_started'])
                self.assertEqual(history,original)
                client=self.app.test_client();session_key=kind if module=='sequential' else f'hierarchical::{kind}'
                with client.session_transaction() as session:session[SESSION_KEY]={session_key:copy.deepcopy(history)}
                page=client.get(f'/{module}/{kind}')
                self.assertEqual(page.status_code,200);self.assertIn(b'2147483648',page.data);self.assertIn(b'role="alert"',page.data)
                result=client.post(f'/{module}/{kind}/operate',json={'operation':operation,'payload':payload})
                self.assertEqual(result.status_code,400);self.assertEqual(result.get_json()['history'],original)
                self.assertEqual(client.post(f'/{module}/{kind}/reset').status_code,200)
                self.assertEqual(client.post(f'/{module}/{kind}/operate',json={'operation':operation,'payload':payload}).status_code,200)
    def test_incompatible_history_does_not_expose_saved_stack_trace(self):
        import hashlib,json
        history=[{'operation':'apilar','payload':{'value':2147483648}}]
        digest=hashlib.sha256(json.dumps(history,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        client=self.app.test_client()
        with client.session_transaction() as session:
            session[SESSION_KEY]={'stack':history}
            session['stack_push_prepared_v1']={'history_digest':digest,'trace':{'structure_id':'stack','operation_name':'apilar','steps':[{'sentinel':'IMPOSSIBLE_SAVED_TRACE'}]}}
        page=client.get('/sequential/stack');self.assertEqual(page.status_code,200)
        self.assertNotIn(b'IMPOSSIBLE_SAVED_TRACE',page.data)
        with client.session_transaction() as session:self.assertIn('stack_push_prepared_v1',session)
    def test_comparison_frontier_keeps_c_int_validation(self):
        client=self.app.test_client()
        for kind in ['abb-avl','avl-red-black','abb-heap','traversals']:
            for values in [[10,20],[-2147483648,2147483647],[2147483648],[-2147483649]]:
                with self.subTest(kind=kind,values=values):
                    response=client.post('/hierarchical/compare',json={'kind':kind,'values':values})
                    self.assertEqual(response.status_code,200 if all(-2147483648<=v<=2147483647 for v in values) else 400)

    def test_new_int32_boundaries_and_rejection(self):
        for service,kind,op in [(StructureService,'stack','apilar'),(HierarchicalStructureService,'abb','insertar')]:
            for value in [-2147483648,2147483647,-2147483649,2147483648]:
                with self.subTest(kind=kind,value=value):
                    result=service.execute_operation(structure_id=kind,operation_name=op,payload={'value':value},history=[])
                    self.assertEqual(result['success'],-2147483648<=value<=2147483647)
                    if not result['success']:self.assertEqual(result['execution_trace']['steps'],[])

if __name__=='__main__':unittest.main(verbosity=2)
