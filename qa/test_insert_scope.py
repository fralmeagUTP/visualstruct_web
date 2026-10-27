"""Insertion call scopes describe post-instruction life, not pending historical work."""
import unittest
from functools import lru_cache
from app.services.hierarchical_structure_service import HierarchicalStructureService as S

CASES=[([],5),([10],5),([10],15),([10],10),([30,20],10),([10,20],30),([30,10],20),([10,30],20),([10,5,15],1)]
@lru_cache(maxsize=1)
def trace_cases():
 return list(_traces())
def traces():return iter(trace_cases())
def _traces():
 for sid in ['abb','avl','red_black','binary_heap']:
  for seed,value in CASES:
   history=[{'operation':'insertar','payload':{'value':v}} for v in seed]
   r=S.execute_operation(sid,'insertar',{'value':value},history)
   yield sid,seed,value,r['execution_trace']

class InsertScope(unittest.TestCase):
 def test_scope_matches_post_instruction_memory(self):
  for sid,seed,value,trace in traces():
   with self.subTest(sid=sid,seed=seed,value=value):
    for step in trace['steps']:
     p=step['pedagogy']
     if 'memory_state' not in p:continue  # Rejected duplicate: generic, not instruction builder.
     m=p['memory_state'];frames=m.get('tree_frames',m.get('query_frames',[]));live={f['id'] for f in frames}
     if m.get('caller_frame'):live.add('caller')
     for f in p['call_stack']:
      self.assertIn(f['frame_id'],live,(sid,step['line_text'],f))
      self.assertFalse(f.get('scope_status','').startswith('terminado'))
     self.assertEqual({f['frame_id'] for f in p['call_stack']},live)
     for f in p.get('completed_call_stack',[]):
      self.assertNotIn(f['frame_id'],live)
      self.assertTrue(f['scope_status'].startswith('terminado'))
    if trace['steps'] and 'memory_state' in trace['steps'][-1]['pedagogy']:
     self.assertEqual(trace['steps'][-1]['pedagogy']['call_stack'],[])
 def test_abb_publication_and_void_caller(self):
  for sid,seed,value,trace in traces():
   if sid!='abb':continue
   for step in trace['steps']:
    p=step['pedagogy'];phase=p.get('instruction_event',{}).get('phase')
    if phase=='caller':
     caller=next(f for f in p['call_stack'] if f['frame_id']=='caller')
     self.assertIn('publicada',caller['continuation']);self.assertEqual(p['return_propagation']['value'],p['memory_state']['head'])
    if phase=='caller_exit':
     self.assertEqual(p['instruction_event']['return'],'void');self.assertEqual(p['return_propagation']['value'],'void')
     self.assertEqual(p['completed_call_stack'][0]['return'],'void')
 def test_rn_void_does_not_claim_pointer(self):
  for sid,seed,value,trace in traces():
   if sid!='red_black':continue
   for step in trace['steps']:
    p=step['pedagogy'];e=p['instruction_event']
    if e['phase']=='return' and e['return']=='void':
     self.assertIn('void',p['narration']['basic']);self.assertNotIn('alias retornados',p['narration']['basic']);self.assertNotIn('asignacion del caller sigue pendiente',p['narration']['basic'])
if __name__=='__main__':unittest.main(verbosity=2)
