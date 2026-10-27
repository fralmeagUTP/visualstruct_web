"""Terminal equivalent caller does not promise an unmodelled assignment."""
import importlib,unittest
from pathlib import Path
from unittest.mock import patch
from app.services.hierarchical_structure_service import HierarchicalStructureService as S

class QueryReturn(unittest.TestCase):
 def test_root_and_list_terminal_vs_callee(self):
  for op in ['raiz','a_lista']:
   for seed in [[],[5],[5,20,40,50,30]]:
    with self.subTest(op=op,seed=seed):
     history=[{'operation':'insertar','payload':{'value':v}} for v in seed]
     trace=S.execute_operation('binary_heap',op,{},history)['execution_trace']
     returns=[s['pedagogy'] for s in trace['steps'] if s['pedagogy']['instruction_event']['phase']=='return']
     self.assertGreater(len(returns),1)
     for p in returns:
      if p['instruction_event']['scope']=='caller':
       self.assertEqual(p['memory_state']['query_frames'],[])
       for text in p['narration'].values():
        self.assertNotIn('pendiente',text);self.assertIn('Finaliza',text)
      else:
       self.assertTrue(p['memory_state']['query_frames'])
       for text in p['narration'].values():self.assertIn('pendiente de asignacion',text)
 def test_only_terminal_narration_changes(self):
  m=importlib.import_module('app.domain.hierarchical.heap_query_instruction')
  old={'__package__':m.__package__,'__file__':m.__file__};path=Path(__file__).resolve().parents[2]/'heap-query-return-baseline.py';exec(compile(path.read_text(),str(path),'exec'),old)
  fn='build_heap_query_trace'
  for op in ['raiz','a_lista']:
   for seed in [[],[5],[5,20,40,50,30]]:
    history=[{'operation':'insertar','payload':{'value':v}} for v in seed]
    after=S.execute_operation('binary_heap',op,{},history)['execution_trace']
    with patch.object(m,fn,old[fn]):before=S.execute_operation('binary_heap',op,{},history)['execution_trace']
    for a,b in zip(after['steps'],before['steps']):
     if a['pedagogy']['instruction_event']=={'scope':'caller','phase':'return','condition':None,'return':a['pedagogy']['instruction_event']['return']}:
      b['pedagogy']['narration']=a['pedagogy']['narration']
    self.assertEqual(after,before)
if __name__=='__main__':unittest.main(verbosity=2)
