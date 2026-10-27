"""Book guide contracts and the scope of the shared-template edit."""
import re,unittest,tempfile
from pathlib import Path
from app import create_app
from app.config import Config
from app.services.graph_help_service import GraphHelpService
ROOT=Path(__file__).resolve().parents[1]
FROZEN=ROOT/'qa_convergence/checkpoint_fixture'
class BookGuide(unittest.TestCase):
 @classmethod
 def setUpClass(cls):
  import json,hashlib
  manifest=json.loads((FROZEN/'manifest.json').read_text())
  for name,digest in manifest['files'].items():
   if hashlib.sha256((FROZEN/name).read_bytes()).hexdigest()!=digest:
    raise AssertionError('Frozen checkpoint fixture changed: '+name)
 def test_book_contract_content(self):
  data=GraphHelpService.get_structure_help('graph');text=' '.join(data['book_contract'])
  for item in ['GrafoEstado','7 RANGO','NULL con GRAFO_OK','int *salida','long long','no se usa como infinito','no repite esa eliminación','no se liberan','No hay transacción conjunta']:
   self.assertIn(item,text)
  self.assertIn('cola de índices', ' '.join(GraphHelpService.get_module_help()['tips']))
 def test_other_shared_template_blocks_unchanged(self):
  old=(FROZEN/'templates/help/_operation_contracts.html').read_text();new=(ROOT/'templates/help/_operation_contracts.html').read_text()
  pattern=r'{% if structure_id == "graph" %}[\s\S]*?{% endif %}'
  self.assertEqual(re.sub(pattern,'GRAPH_BLOCK',old),re.sub(pattern,'GRAPH_BLOCK',new))
 def test_rendered_guide(self):
  with tempfile.TemporaryDirectory() as folder:
   class T(Config):TESTING=True;SESSION_CACHE_DIR=folder
   response=create_app(T).test_client().get('/help/graph/graph')
   self.assertEqual(response.status_code,200);html=response.get_data(as_text=True)
   self.assertIn('GRAFO_DESCONECTADO',html);self.assertNotIn('pueden devolver un bosque',html)
   self.assertNotIn('conserva los arcos al retornar',html);self.assertNotIn('usa INT_MAX como infinito',html)
   self.assertNotIn('descarga también sus archivos',html)
   self.assertEqual(html.count('id="graph-canonical-source"'),1)
   self.assertEqual(html.count('id="graph-canonical-code"'),1)
   self.assertEqual(html.count('data-book-function="grafo_bfs"'),1)
   self.assertNotIn('data-book-function="fijar_estado"',html)
   import html as html_module
   code=re.search(r'<pre id="graph-canonical-code"[^>]*>([\s\S]*?)</pre>',html).group(1)
   self.assertEqual(html_module.unescape(code),(ROOT/'docs/tads_C/tad_grafo.c').read_text())
   for name in re.findall(r'data-book-function="([^"]+)"',html):
    self.assertRegex(code,rf'\b{re.escape(name)}\s*\(')
 def test_non_graph_enrichment_unchanged(self):
  import ast,copy
  import app.routes.help_routes as current
  original=(FROZEN/'app/routes/help_routes.py').read_text();tree=ast.parse(original)
  node=next(n for n in tree.body if isinstance(n,ast.FunctionDef) and n.name=='_enrich_help_with_c_code')
  namespace=dict(vars(current));exec('\n'.join(original.splitlines()[node.lineno-1:node.end_lineno]),namespace)
  previous=namespace['_enrich_help_with_c_code']
  for structure in ['stack','queue','priority_queue','linked_list','circular_list','sublist','abb','avl','red_black','binary_heap','hash_table','sorting_array']:
   with self.subTest(structure=structure):
    data={'title':structure,'supported_operations':[]}
    self.assertEqual(previous(copy.deepcopy(data),structure),current._enrich_help_with_c_code(copy.deepcopy(data),structure))
if __name__=='__main__':unittest.main(verbosity=2)
