"""Visible insertion: independently observed allocation masks, identities and call scopes."""
from _instruction_context_contract import context_stack
import pytest
from test_audit_sublist_child_source_native import sublist_native_review,sublist_identity_map
CASES=[0,17,1,2,3,18]

def insertion_identity_map(rows):
 mapping=sublist_identity_map(rows)
 for row in rows:
  e=row['native']
  for n in e['nodes']:
   if n['id'] in mapping:continue
   if n['type']==1:
    mapping[n['id']]='P'+str(1+sum(v.startswith('P') for v in mapping.values()))
   else:
    owners=[f['aliases'][4] for f in e['frames'] if f['aliases'][4]>0]
    assert owners,e
    owner=mapping[owners[-1]];prefix='H'+owner[1:]+'.'
    mapping[n['id']]=prefix+str(1+sum(v.startswith(prefix) for v in mapping.values()))
 return mapping

@pytest.mark.parametrize('case',CASES)
def test_visible_insertions_native_heap_initialization_scopes_and_returns(sublist_native_review,case):
 rows=[r for r in sublist_native_review['rows'] if r['native']['case']==case];assert rows
 mapping=insertion_identity_map(rows)
 for row in rows:
  e=row['native'];step=row['step'];assert not row['issues'],row
  before=e['line'].startswith(('if ','while ','return ')) or e['condition']==-3
  state=step['state_snapshot'] if before else step['state_after'];ped=step['pedagogy'];memory=ped['memory_state']
  expected=[]
  for n in e['nodes']:
   mask=n['mask'];node={'id':mapping[n['id']],'kind':'parent' if n['type']==1 else 'child','value':n['value'] if mask&1 else 'sin inicializar','next':mapping[n['next']] if mask&2 else 'sin inicializar'}
   if n['type']==1:node['sub']=mapping[n['sub']] if mask&4 else 'sin inicializar'
   expected.append(node)
  assert sorted([{k:v for k,v in n.items() if k!='status'} for n in state['heap_nodes']],key=lambda n:n['id'])==sorted(expected,key=lambda n:n['id']),(case,e,state)
  assert state['head']==mapping[e['root']]
  assert len(state['sublist_frames'])==len(e['frames'])==e['depth']+1
  for observed,frame in zip(e['frames'],state['sublist_frames']):
   assert frame['function']==observed['function']
   for name,slot in {'nuevo':0,'actual':1,'padre':4}.items():
    alias=observed['aliases'][slot]
    if alias==-2:continue
    assert {**frame['parameters'],**frame['locals']}[name]==mapping[alias],(e,name,frame)
  assert not ped['heap_transition']['freed']
  current={(f['function'],name):value for f in memory['sublist_frames'] for name,value in {**f['parameters'],**f['locals']}.items()}
  variables={(v['scope'],v['name']):v for v in ped['variables']}
  for key,value in current.items():assert variables[key]['value']==value and variables[key]['scope_state']!='fuera de ámbito'
  for key,v in variables.items():
   if key not in current:assert v['value']=='fuera de ámbito'
   if key[1]=='nuevo':assert v['type']==('Sublista *' if key[0] in {'crear_hijo','sublista_insertar_hijo_final'} else 'Nodo *')
  if e['line']=='return nuevo;':
   assert memory['returned']==mapping[e['return_pointer']]
   assert context_stack(ped)[-1]['return']==mapping[e['return_pointer']]
  if e['condition']==-4 or e['line'] in {'return true;','return false;'}:
   assert memory['returned']==bool(e['return_value'])
  if 'malloc(sizeof(' in e['line']:
   assert ped['concept']=='allocation' and ped['heap_transition']['kind']=='allocate'
   allocated=state['heap_nodes'][-1];assert allocated['value']==allocated['next']=='sin inicializar'
   if allocated['kind']=='parent':assert allocated['sub']=='sin inicializar'
   assert allocated['status']=='detached'
  if e['line'] in {'*lista = nuevo;','actual->sgte = nuevo;','padre->sub = nuevo;'}:assert ped['concept']=='link' and ped['heap_transition']['kind']=='link'
 assert not rows[-1]['step']['pedagogy']['memory_state']['sublist_frames']
