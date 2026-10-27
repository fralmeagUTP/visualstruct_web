import unittest,tempfile
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch
from app import create_app
from app.config import Config
from app.services.session_service import SESSION_KEY

class BookHttpTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        class C(Config):
            TESTING=True
            SESSION_CACHE_DIR=self.temp.name
            SESSION_COOKIE_NAME='book_qa_http'
            SESSION_REFRESH_EACH_REQUEST=False
        self.app=create_app(C);self.client=self.app.test_client()
    def tearDown(self):self.temp.cleanup()
    def test_legacy_get_export_post_no_write_and_reset(self):
        legacy=[{'operation':'insert_vertex','payload':{'vertex':17},'unknown':['preserve',42]}]
        record={'schema_version':1,'history':legacy,'checkpoint':{'old':'preserve'}}
        with self.client.session_transaction() as session:session[SESSION_KEY]={'graph::graph':record}
        from app.services.graph_structure_service import GraphStructureService
        with patch.object(GraphStructureService,'_rebuild_adapter',side_effect=AssertionError('legacy replay')):
            for url in ['/graph/graph/construccion','/graph/graph/history','/help/source/graph/main']:
                response=self.client.get(url)
                self.assertEqual(response.status_code,409 if url.endswith('/main') else 200)
                self.assertNotIn('Set-Cookie',response.headers)
            response=self.client.post('/graph/graph/operate',json={'operation':'insert_vertex','payload':{'vertex':3}})
            self.assertEqual(response.status_code,400);self.assertTrue(response.json['preserve_session'])
            self.assertNotIn('Set-Cookie',response.headers)
        with self.client.session_transaction() as session:self.assertEqual(session[SESSION_KEY]['graph::graph'],record)
        self.assertEqual(self.client.get('/graph/graph/history').json['history'],legacy)
        self.assertEqual(self.client.post('/graph/graph/reset').status_code,200)
        response=self.client.post('/graph/graph/operate',json={'operation':'insert_vertex','payload':{'vertex':3}})
        self.assertEqual(response.status_code,200)
        self.assertEqual(response.json['history'][0]['source_contract'],'graph-book/v1')
        self.assertEqual(self.client.get('/help/source/graph/main').status_code,200)
    def test_failure_trace_and_source_downloads(self):
        response=self.client.post('/graph/graph/operate',json={'operation':'run_bfs','payload':{'start':99}})
        self.assertEqual(response.status_code,400);self.assertEqual(response.json['c_status'],2)
        self.assertTrue(response.json['execution_trace']['execution_started'])
        for kind,suffix in [('source','c'),('header','h')]:
            response=self.client.get('/help/source/graph/'+kind)
            self.assertEqual(response.data,Path('docs/tads_C/tad_grafo.'+suffix).read_bytes())
            response.close()

if __name__=='__main__':unittest.main()
