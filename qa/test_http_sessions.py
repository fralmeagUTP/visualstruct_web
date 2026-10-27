"""HTTP/session integration over every registered non-sorting operation."""
import json
import tempfile
import unittest
from pathlib import Path
from app import create_app
from app.config import Config

class HttpSessionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp=tempfile.TemporaryDirectory(prefix='visualstruct-http-')
        class T(Config):
            TESTING=True
            SESSION_CACHE_DIR=cls.tmp.name
        cls.app=create_app(T)
        cls.matrix=json.loads((Path(__file__).resolve().parents[2]/'qa_trazas/matrix.json').read_text())['rows']
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
                self.assertEqual(response.status_code,200 if case['success'] else 400)
                result=response.get_json();self.assertEqual(result['success'],case['success'])
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
