"""Clear and readonly query: independently observed heap/scopes/buffer per C line."""
import pytest
from test_audit_sublist_child_source_native import sublist_native_review,sublist_identity_map
CASES=[13,14,15,21,16,22]

@pytest.mark.parametrize('case',CASES)
def test_clear_query_native_intermediate_heap_scopes_output_and_returns(sublist_native_review,case):
 rows=[r for r in sublist_native_review['rows'] if r['native']['case']==case];assert rows;mapping=sublist_identity_map(rows);query=case in [13,14,15,21];initial_heap=rows[0]['native']['nodes'];returns=[]
 for row in rows:
  e=row['native'];step=row['step'];assert not row['issues'],row
  before=e['line'].startswith(('if ','while ','return ')) or e['condition'] in {-3,-6}
  state=step['state_snapshot'] if before else step['state_after'];ped=step['pedagogy'];memory=ped['memory_state']
  expected=[{'id':mapping[n['id']],'kind':'parent' if n['type']==1 else 'child','value':n['value'],'next':mapping[n['next']],**({'sub':mapping[n['sub']]} if n['type']==1 else {})} for n in e['nodes']]
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted(expected,key=lambda n:n['id'])
  assert state['head']==mapping[e['root']]
  assert len(state['sublist_frames'])==len(e['frames'])==e['depth']+1
  for observed,frame in zip(e['frames'],state['sublist_frames']):
   assert frame['function']==observed['function']
   for name,slot in {'actual':1,'next':3,'padre':4}.items():
    alias=observed['aliases'][slot]
    if alias==-2:continue
    value='indeterminado (liberado)' if alias<=-100 else mapping[alias]
    assert {**frame['parameters'],**frame['locals']}[name]==value
   if observed['usados']!=-2:assert frame['locals']['usados']==observed['usados']
   if observed['capacidad']!=-2:assert frame['parameters']['capacidad']==observed['capacidad']==1024
   if observed['owner']:
    assert frame['parameters']['lista_hijos']=='&'+mapping[observed['owner']]+'.sub'
  current={(f['function'],name):value for f in memory['sublist_frames'] for name,value in {**f['parameters'],**f['locals']}.items()}
  variables={(v['scope'],v['name']):v for v in ped['variables']}
  for key,value in current.items():assert variables[key]['value']==value and variables[key]['scope_state']!='fuera de ámbito'
  for key,v in variables.items():
   if key not in current:assert v['value']=='fuera de ámbito'
  if query:
   assert e['nodes']==initial_heap and e['root']==rows[0]['native']['root']
   assert state['buffer_capacity']==1024
   assert state['buffer_values']==[write['value'] for write in e['writes']]
   assert [write['index'] for write in e['writes']]==list(range(len(state['buffer_values'])))
   assert not ped['heap_transition']['freed']
   if e['line']=='destino[usados] = actual->nro;':
    assert ped['concept']=='assignment';assert state['usados']==len(state['buffer_values'])-1
    assert all("copia" in text.lower() and "destino" in text and "link" not in text for text in ped["narration"].values())
   if e['line']=='usados++;':assert state['usados']==len(state['buffer_values']) and ped['concept']=='assignment'
   for v in ped['variables']:
    if v['name']=='destino':assert v['type']=='int *'
    if v['scope']=='sublista_copiar_hijos' and v['name']=='actual':assert v['type']=='const Sublista *'
   if e['function']=='sublista_copiar_hijos' and e['line']=='return usados;':
    assert memory['returned']==e['return_value']==len(state['buffer_values'])
   if e['function']=='sublista_obtener_hijos' and (e['condition']==-4 or e['line']=='return -1;'):
    assert type(memory['returned']) is int and type(ped['call_stack'][-1]['return']) is int
    assert memory['returned']==e['return_value'];assert ped['call_stack'][-1]['return']==e['return_value'];assert not memory['sublist_frames'];returns.append(e['return_value'])
  else:
   freed=ped['heap_transition']['freed'];assert [n['id'] for n in freed]==([mapping[e['freed']]] if e['line']=='free(actual);' else [])
   if e['function']=='destruir_hijos':assert state['owner_parent']==mapping[e['owner']] and state['sub_head']==mapping[e['child_root']]
   if e['condition']==-6:
    assert ped['concept']=='return';assert ped['call_stack'][-1]['function']==e['function'];assert ped['call_stack'][-1]['return'] is None
 if query:assert returns==[3 if case==13 else 0 if case==14 else -1]
 else:assert not rows[-1]['step']['pedagogy']['memory_state']['heap_nodes'] and not rows[-1]['step']['pedagogy']['memory_state']['sublist_frames']
