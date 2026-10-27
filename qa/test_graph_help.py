import tempfile,unittest
from app import create_app
from app.config import Config
from app.domain.graph.educational_capacity import MAX_VERTICES
from app.services.graph_help_service import GraphHelpService
class GraphHelpTests(unittest.TestCase):
 def test_rendered_contract_matches_real_limit_and_controls(self):
  with tempfile.TemporaryDirectory() as folder:
   class T(Config):TESTING=True;SESSION_CACHE_DIR=folder
   client=create_app(T).test_client();r=client.get('/help/graph/graph');self.assertEqual(r.status_code,200);text=r.get_data(as_text=True)
   self.assertIn(f'aplicación es {MAX_VERTICES} vértices',text);self.assertNotIn('200 vértices',text);self.assertIn('no es un límite del TAD C',text)
   self.assertIn('Cola FIFO</a>',text);self.assertNotIn('>queue</a>',text)
   for op in ['exists_vertex','exists_edge','clear_graph']:
    self.assertIn(f'{op} — API/auxiliar; no es una opción independiente del selector',text)
   self.assertIn('grafo_existe_vertice',text);self.assertIn('grafo_existe_arco',text)
   self.assertEqual(GraphHelpService.get_structure_help('graph')['max_vertices'],MAX_VERTICES)
   self.assertIn(str(MAX_VERTICES),GraphHelpService.get_module_help()['tips'][0])
if __name__=='__main__':unittest.main()
