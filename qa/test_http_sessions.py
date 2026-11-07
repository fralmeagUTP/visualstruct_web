"""HTTP/session integration over every registered non-sorting operation."""
import json
import tempfile
import unittest
from pathlib import Path
from app import create_app
from app.config import Config
from qa.independent_inputs import independent_input_path

class HttpSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='visualstruct-http-')
        class T(Config):
            TESTING=True
            SESSION_CACHE_DIR=cls.tmp.name
        cls.app=create_app(T)
        cls.matrix=json.loads((independent_input_path('qa_trazas/matrix.json')).read_text())['rows']
    @classmethod
    def tearDownClass(cls):cls.tmp.cleanup()
    def test_all_operation_routes_refresh_and_reset(self):
        for case in self.matrix:
            if case['scenario']!='populated':continue
            module,sid=case['module'],case['structure']
            with self.subTest(module=module,structure=sid,operation=case['operation']):
                client=self.app.test_client();base=f'/{module}/{sid}'
                for seed in self.matrix:
                    if seed['module']==module and seed['structure']==sid and seed['scenario']=='seed':
                        response=client.post(base+'/operate',json={'operation':seed['operation'],'payload':seed['payload']})
                        self.assertEqual(response.status_code,200 if seed['success'] else 400)
                response=client.post(base+'/operate',json={'operation':case['operation'],'payload':case['payload']})
                # The archived seed includes isolated vertex 4. The book C
                # rejects a disconnected MST rather than returning a forest.
                disconnected_mst = module == 'graph' and case['operation'] in {'run_prim','run_kruskal'}
                expected_success = False if disconnected_mst else case['success']
                self.assertEqual(response.status_code,200 if expected_success else 400,case)
                result=response.get_json();self.assertEqual(result['success'],expected_success)
                if disconnected_mst:
                    seeds=[s for s in self.matrix if s['module']=='graph' and s['scenario']=='seed']
                    vertices={s['payload']['vertex'] for s in seeds if s['operation']=='insert_vertex'}
                    endpoints={s['payload'][k] for s in seeds if s['operation']=='insert_edge' for k in ['origin','target']}
                    self.assertEqual(vertices,{1,2,3,4});self.assertEqual(vertices-endpoints,{4})
                    self.assertTrue(case['success'])  # Retain and identify the superseded observation.
                    self.assertEqual((result['c_status'],result['c_status_name'],result['c_return']),(5,'GRAFO_DESCONECTADO','NULL'))
                    self.assertEqual(result['result']['mst_edges'],[])
                    self.assertFalse(result['result']['connected'])
                self.assertIsInstance(result['visual_state'],dict)
                self.assertEqual(client.get(base,follow_redirects=True).status_code,200)
                self.assertEqual(client.post(base+'/reset').status_code,200)
                self.assertEqual(client.get(base,follow_redirects=True).status_code,200)
    def test_all_landing_and_phase_pages(self):
        paths=['/','/healthz','/sequential/','/hierarchical/','/graph/','/hash/','/sorting/','/sorting/visualizador','/help/manual']
        paths += ['/graph/graph/'+x for x in ['construccion','recorridos','camino-minimo','expansion-minima']]
        client=self.app.test_client()
        for path in paths:
            with self.subTest(path=path):self.assertEqual(client.get(path).status_code,200)

if __name__=='__main__':unittest.main(verbosity=2)
