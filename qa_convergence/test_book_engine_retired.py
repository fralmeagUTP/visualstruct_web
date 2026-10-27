import json,unittest
from pathlib import Path
from app.domain.graph.book_c_subset import BookSession
from app.domain.graph.book_trace import BookTraceCollector
class RetiredProjectionTests(unittest.TestCase):
 def test_live_alias_after_free_is_historical_without_changing_raw_memory(self):
  before={'structure':'graph','directed':False,'nodes':[{'id':'1'},{'id':'2'}],'edges':[{'source':'1','target':'2','weight':7}],'metadata':{},'last_result':None,'last_operation':None}
  c=BookTraceCollector(operation_name='remove_vertex',payload={'vertex':1},before_state=before);s=BookSession([1,2],[(1,2,7),(2,1,7)],callback=c.callback);r=s.call('grafo_eliminar_vertice',[1]);trace=c.finish(after_state=before)
  freed=next(step['pedagogy'] for step in trace['steps'] if step['pedagogy']['instruction_event']['phase']=='free' and step['pedagogy']['instruction_event']['value']=='E2')
  alias=next(v for v in freed['variables'] if v['name']=='actual')
  self.assertEqual(alias['scope_status'],'vivo');self.assertEqual(alias['value'],{'historical_identity':'E2','usable':False,'value_status':'indeterminate_after_free'});self.assertFalse(alias['usable']);self.assertEqual(alias['change_reason'],'lifetime_ended_not_pointer_write')
  raw=[cell['value'] for frame in freed['memory_state']['frames'] for scope in frame['scopes'] for name,cell in scope['variables'].items() if name=='actual'];self.assertEqual(raw,['E2'])
  self.assertEqual(freed['memory_state'],freed['instruction_state_after']);self.assertFalse(freed['memory']['dangling_references_checked']);self.assertTrue(any('E2' in x['identities'] for x in freed['memory']['retired_references']))
  self.assertEqual(trace['steps'][-1]['pedagogy']['memory']['retired_references'],[])
  Path('qa_convergence/book_retired_fixture.json').write_text(json.dumps(freed,ensure_ascii=False))
if __name__=='__main__':unittest.main(verbosity=2)
