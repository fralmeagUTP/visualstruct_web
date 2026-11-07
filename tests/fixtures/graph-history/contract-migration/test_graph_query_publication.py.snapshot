"""Scalar versus borrowed-list return explanation at host publication only."""
import importlib,unittest
from pathlib import Path
from unittest.mock import patch
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph.snapshot_pool import expand_graph_trace
H=[{'operation':'insert_vertex','payload':{'vertex':v}} for v in [1,2]]+[{'operation':'insert_edge','payload':{'origin':1,'target':2,'weight':9}}]
CASES=[('exists_vertex',{'vertex':1},'booleano'),('exists_vertex',{'vertex':9},'booleano'),('exists_edge',{'origin':1,'target':2},'booleano'),('exists_edge',{'origin':2,'target':9},'booleano'),('edge_weight',{'origin':1,'target':2},'entero'),('edge_weight',{'origin':1,'target':9},None),('list_vertices',{},'prestada'),('list_edges',{},'prestada')]
def get(op,p,h):return expand_graph_trace(S.execute_operation('graph',op,p,h)['execution_trace'])
class Publication(unittest.TestCase):
 def test_typed_results(self):
  for op,p,kind in CASES:
   with self.subTest(op=op,p=p):
    t=get(op,p,H);f=t['steps'][-1]['pedagogy'];self.assertFalse(f['instruction_event']['C_executed'])
    if kind is None:self.assertEqual(f['instruction_event']['phase'],'input_validation');continue
    for text in f['narration'].values():
     self.assertIn(kind,text);self.assertIn('API',text)
     if kind!='prestada':self.assertNotIn('lista',text)
 def test_only_successful_query_final_narration_changes(self):
  m=importlib.import_module('app.domain.graph.construction_instruction');ns={'__package__':m.__package__,'__file__':m.__file__};path=Path(__file__).resolve().parents[2]/'graph-query-note-baseline.py';exec(compile(path.read_text(),str(path),'exec'),ns)
  fn='build_graph_construction_trace'
  for op,p,kind in CASES:
   for h in [H,[]]:
    a=get(op,p,h)
    with patch.object(m,fn,ns[fn]):b=get(op,p,h)
    if a['steps'][-1]['phase']=='api_publication':b['steps'][-1]['pedagogy']['narration']=a['steps'][-1]['pedagogy']['narration']
    self.assertEqual(a,b)
if __name__=='__main__':unittest.main(verbosity=2)
