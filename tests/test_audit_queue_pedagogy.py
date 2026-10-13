"""C pointer facts that final-state-only conformance cannot detect."""
import pytest
def _operate(client,name,payload=None):
 response=client.post('/sequential/queue/operate',json={'operation':name,'payload':payload or {}})
 return response.get_json()['execution_trace']
@pytest.mark.parametrize('seed', [[],[9],[9,-1]])
def test_queue_guard_uses_valid_queue_address_and_actual_front(client,seed):
 for value in seed:_operate(client,'encolar',{'value':value})
 trace=_operate(client,'desencolar')
 guard=next(s for s in trace['steps'] if 'q == NULL ||' in s['line_text'])
 condition=guard['pedagogy']['condition']
 assert condition['result'] is (not seed)
 assert condition['substituted']==f"&cola == NULL || {'N1' if seed else 'NULL'} == NULL"
 q=next(p for p in guard['pedagogy']['pointers'] if p['name']=='q')
 assert q['target']=='&cola' and q['type']=='struct Cola *'
@pytest.mark.parametrize('seed', [[],[9],[9,9]])
def test_enqueue_publication_preserves_aux_alias_until_function_exit(client,seed):
 for value in seed:_operate(client,'encolar',{'value':value})
 trace=_operate(client,'encolar',{'value':-1})
 published=False
 for step in trace['steps']:
  line=step['line_text']
  if 'q->delante = aux;' in line or 'q->atras->sgte = aux;' in line:published=True
  if published and ('q->delante = aux;' in line or 'q->atras' in line):
   aux=next(p for p in step['pedagogy']['pointers'] if p['name']=='aux')
   assert aux['target']==f'N{len(seed)+1}'
   assert aux['type']=='struct NodoCola *'
   assert not step['pedagogy']['heap_transition']['freed']
   if 'q->delante = aux;' in line:
    front=next(p for p in step['pedagogy']['pointers'] if p['name']=='delante')
    assert front['target']==aux['target']
 assert published
 assert 'aux' not in trace['final_state']
