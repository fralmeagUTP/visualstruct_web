"""Final host receipt describes the actual C pointer, including NULL."""
import importlib,unittest
from pathlib import Path
from unittest.mock import patch
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph.snapshot_pool import expand_graph_trace

def history(edges, directed=True):
 return [{'operation':'create_graph','payload':{'directed':directed}}]+[{'operation':'insert_vertex','payload':{'vertex':v}} for v in [1,2,3]]+[{'operation':'insert_edge','payload':{'origin':a,'target':b,'weight':w}} for a,b,w in edges]
CASES=[('run_bellman_ford',{'start':1,'end':3},[(1,2,1),(2,3,-3),(3,2,1)]),('run_bellman_ford',{'start':1,'end':3},[(1,2,1)]),('run_bellman_ford',{'start':1,'end':3},[(1,2,1),(2,3,2)]),('run_dijkstra',{'start':1,'end':3},[(1,2,1)]),('run_dijkstra',{'start':1,'end':3},[(1,2,1),(2,3,2)]),('run_kruskal',{},[]),('run_prim',{'start':1},[])]
def get(op,p,edges):return expand_graph_trace(S.execute_operation('graph',op,p,history(edges,op not in {'run_prim','run_kruskal'}))['execution_trace'])
class Receipt(unittest.TestCase):
 def test_null_and_owned_receipt(self):
     """Current graph-book/v1 acceptance; literal prior source is preserved."""
     from qa_convergence._graph_contract_migration import assert_graph_contract_migration
     from pathlib import Path as _MigrationPath
     assert_graph_contract_migration(_MigrationPath(__file__).resolve().parents[1])
     from qa_convergence.test_current_graph_numeric_receipt import Receipt as CurrentContract
     CurrentContract.test_null_and_owned_receipt(self)
 def test_only_receipt_description_changes(self):
  m=importlib.import_module('app.domain.graph.numeric_instruction');ns={'__package__':m.__package__,'__file__':m.__file__};p=Path(__file__).resolve().parents[2]/'numeric-null-baseline.py';exec(compile(p.read_text(),str(p),'exec'),ns)
  fn='build_graph_numeric_trace'
  for op,p,edges in CASES:
   a=get(op,p,edges)
   with patch.object(m,fn,ns[fn]):b=get(op,p,edges)
   sa,sb=a['steps'][-1],b['steps'][-1];sb['debug']['note']=sa['debug']['note'];sb['pedagogy']['narration']=sa['pedagogy']['narration'];sb['pedagogy']['phase']['goal']=sa['pedagogy']['phase']['goal']
   self.assertEqual(a,b)
if __name__=='__main__':unittest.main(verbosity=2)
