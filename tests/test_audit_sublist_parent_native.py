"""Independent downloaded-C observation of six visible parent-removal cases."""
from _instruction_context_contract import context_stack
import re
import pytest
from test_audit_sublist_child_source_native import sublist_native_review,sublist_identity_map

PARENT_CASES=[4,5,6,7,19,23]
SLOTS={'actual':1,'anterior':2,'next':3}

@pytest.mark.parametrize('case',PARENT_CASES)
def test_parent_removal_native_heap_all_scopes_types_return_and_source(sublist_native_review,case):
 review=sublist_native_review;rows=[r for r in review['rows'] if r['native']['case']==case];assert rows
 mapping=sublist_identity_map(rows);source=rows[0]['step']['source_code'] if 'source_code' in rows[0]['step'] else None
 seen_returns=[];seen_child_frees=[]
 for row in rows:
  event=row['native'];step=row['step'];assert not row['issues'],row
  before=event['line'].startswith(('if ','while ','return ')) or event['condition'] in {-3,-6}
  state=step['state_snapshot'] if before else step['state_after'];ped=step['pedagogy'];memory=ped['memory_state']
  expected=[{'id':mapping[n['id']],'kind':'parent' if n['type']==1 else 'child','value':n['value'],'next':mapping[n['next']],**({'sub':mapping[n['sub']]} if n['type']==1 else {})} for n in event['nodes']]
  actual=[{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']]
  assert sorted(actual,key=lambda n:n['id'])==sorted(expected,key=lambda n:n['id'])
  assert state['head']==mapping[event['root']]
  assert len(state['sublist_frames'])==len(event['frames'])==event['depth']+1
  for observed,frame in zip(event['frames'],state['sublist_frames']):
   assert frame['function']==observed['function']
   for name,slot in SLOTS.items():
    alias=observed['aliases'][slot]
    if alias==-2:continue
    target='indeterminado (liberado)' if alias<=-100 else mapping[alias]
    assert frame['locals'][name]==target,(case,event,frame,name,target)
   if frame['function']=='destruir_hijos':
    assert frame['parameters']['lista_hijos']=='&'+mapping[observed['owner']]+'.sub'
  if event['function']=='destruir_hijos':
   assert state['owner_parent']==mapping[event['owner']]
   assert state['sub_head']==mapping[event['child_root']]
   assert state['sublist_frames'][0]['locals']['actual']==mapping[event['owner']]
  current={(f['function'],name):value for f in memory['sublist_frames'] for name,value in {**f['parameters'],**f['locals']}.items()}
  variables={(v['scope'],v['name']):v for v in ped['variables']}
  for key,value in current.items():
   assert variables[key]['value']==value
   expected_type='int' if key[1]=='valor_padre' else 'Sublista **' if key[1]=='lista_hijos' else 'Nodo **' if key[1]=='lista' else 'Sublista *' if key[0]=='destruir_hijos' else 'Nodo *'
   assert variables[key]['type']==expected_type
   assert variables[key]['scope_state']!='fuera de ámbito'
  for key,variable in variables.items():
   if key not in current:assert variable['value']=='fuera de ámbito'
  if len(memory['sublist_frames'])==2:
   outer=variables[('sublista_eliminar_padre_primero','actual')]
   assert outer['scope_state']=='suspendido durante llamada'
   assert outer['value'].startswith('P') and outer['type']=='Nodo *'
  freed=ped['heap_transition']['freed']
  assert [n['id'] for n in freed]==([mapping[event['freed']]] if event['line']=='free(actual);' else [])
  if freed:
   freed_id=freed[0]['id'];live={n['id'] for n in memory['heap_nodes']};assert freed_id not in live
   if freed_id.startswith('H'):seen_child_frees.append(freed_id)
   else:
    assert not any(n['id'].startswith('H'+freed_id[1:]+'.') for n in memory['heap_nodes'])
  if event['condition']==-6:
   assert ped['concept']=='return';assert context_stack(ped)[-1]['function']=='destruir_hijos'
   assert context_stack(ped)[-1]['return'] is None
   assert [f['function'] for f in ped['call_stack_after']]==['sublista_eliminar_padre_primero']
  if event['function']=='sublista_eliminar_padre_primero' and event['line'].startswith('return '):
   assert event['return_value'] in (0,1)
   assert memory['returned']==bool(event['return_value'])
   assert context_stack(ped)[-1]['return']==bool(event['return_value'])
   assert not ped['call_stack_after'] and not memory['sublist_frames'];seen_returns.append(event['return_value'])
 assert seen_returns==([0] if case in [7,19] else [1])
