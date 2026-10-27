"""Host publication must describe the selected vertex operation, never imaginary C."""
import importlib,unittest
from pathlib import Path
from unittest.mock import patch
from app.services.graph_structure_service import GraphStructureService as S
from app.domain.graph.snapshot_pool import expand_graph_trace
H=[{'operation':'insert_vertex','payload':{'vertex':v}} for v in [1,2]]+[{'operation':'insert_edge','payload':{'origin':1,'target':2,'weight':3}}]
CASES=[('insert_vertex',3,H),('insert_vertex',1,H),('remove_vertex',1,H),('remove_vertex',9,H),('insert_vertex',1,[])]
def get(op,v,h):return expand_graph_trace(S.execute_operation('graph',op,{'vertex':v},h)['execution_trace'])
class Publication(unittest.TestCase):
 def test_operation_specific_boundary(self):
  for op,v,h in CASES:
   with self.subTest(op=op,v=v):
    trace=get(op,v,h);s=trace['steps'][-1];p=s['pedagogy'];self.assertFalse(p['instruction_event']['C_executed'])
    if s['phase']=='input_validation':self.assertIn('sin invocar C',p['narration']['basic']);continue
    if op=='insert_vertex':
     self.assertNotIn('retira',p['narration']['basic']);self.assertNotIn('retirada',p['narration']['basic']);self.assertIn('conserva',p['narration']['basic']);self.assertNotIn('eliminar',s['line_text']);self.assertEqual(len(s['state_after']['edges']),1 if h else 0)
    else:self.assertIn('caller',p['narration']['basic']);self.assertEqual(s['state_after']['edges'],[])
 def test_executed_source_and_all_states_unchanged(self):
  m=importlib.import_module('app.domain.graph.vertex_instruction');ns={'__package__':m.__package__,'__file__':m.__file__};path=Path(__file__).resolve().parents[2]/'graph-vertex-note-baseline.py';exec(compile(path.read_text(),str(path),'exec'),ns)
  for op,v,h in CASES:
   a=get(op,v,h)
   with patch.object(m,'build_graph_vertex_trace',ns['build_graph_vertex_trace']):b=get(op,v,h)
   self.assertEqual(a['C_instruction_events'],b['C_instruction_events'])
   self.assertEqual(a['final_state'],b['final_state']);self.assertEqual(len(a['steps']),len(b['steps']))
   for sa,sb in zip(a['steps'],b['steps']):
    for key in ['state_snapshot','state_after','console']:self.assertEqual(sa[key],sb[key])
    for key in ['memory_state','instruction_state_before','instruction_state_after','variables','condition','instruction_event']:self.assertEqual(sa['pedagogy'].get(key),sb['pedagogy'].get(key))
    if sa['pedagogy']['instruction_event']['C_executed']:self.assertEqual(sa,sb)
   self.assertEqual(a['source_code'].splitlines()[:-1],b['source_code'].splitlines()[:-1])
if __name__=='__main__':unittest.main(verbosity=2)
