"""Scope repair must not change C source, executed instructions, allocation, or result."""
import importlib
import unittest
from pathlib import Path
from unittest.mock import patch
from qa.test_insert_scope import traces, S

MODULES={'abb':('abb_instruction','build_abb_insert_trace'),'avl':('avl_insert_instruction','build_avl_insert_trace'),'red_black':('rbt_insert_instruction','build_rbt_insert_trace'),'binary_heap':('heap_insert_instruction','build_heap_insert_trace')}
class ScopeEquivalence(unittest.TestCase):
 def test_original_instruction_and_memory_stream_is_preserved(self):
  for sid,seed,value,after in traces():
   with self.subTest(sid=sid,seed=seed,value=value):
    name,fn=MODULES[sid];module=importlib.import_module('app.domain.hierarchical.'+name)
    namespace={'__package__':'app.domain.hierarchical','__file__':module.__file__}
    source=Path(__file__).resolve().parents[2]/'scope-insert-baseline'/f'{name}.py'
    exec(compile(source.read_text(),str(source),'exec'),namespace)
    history=[{'operation':'insertar','payload':{'value':v}} for v in seed]
    with patch.object(module,fn,namespace[fn]):before=S.execute_operation(sid,'insertar',{'value':value},history)['execution_trace']
    self.assertEqual(after['source_code'],before['source_code'])
    self.assertEqual(len(after['steps']),len(before['steps']))
    for a,b in zip(after['steps'],before['steps']):
     self.assertEqual({k:v for k,v in a.items() if k!='pedagogy'},{k:v for k,v in b.items() if k!='pedagogy'})
     for key in ['memory_state','state_before','state_after','variables','memory','condition']:
      self.assertEqual(a['pedagogy'].get(key),b['pedagogy'].get(key),key)
     old_returns=[(x.get('frame_id'),x['return']) for x in b['pedagogy']['call_stack'] if x.get('return') is not None]
     new_returns=[(x.get('frame_id'),x['return']) for x in a['pedagogy']['call_stack']+a['pedagogy'].get('completed_call_stack',[]) if x.get('return') is not None]
     if sid=='abb' and a['pedagogy'].get('instruction_event',{}).get('phase')=='caller_exit':new_returns.remove(('caller','void'))
     self.assertEqual(old_returns,new_returns)
if __name__=='__main__':unittest.main(verbosity=2)
