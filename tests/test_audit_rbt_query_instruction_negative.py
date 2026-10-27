"""Negative finite validator paths; test-only trees, not newly reachable UI features."""
from copy import deepcopy
import pytest
from app import create_app
from app.services.hierarchical_structure_service import HierarchicalStructureService as S
from app.services.c_code_service import CCodeService
from app.domain.hierarchical.rbt_query_instruction import build_rbt_query_trace
from _audit_rbt_query_native_observer import observe
from test_audit_rbt_query_instruction_native import match
@pytest.mark.parametrize('kind',['root_red','duplicate','ancestor_order','red_red'])
def test_rbt_validator_negative_instruction_short_circuit(tmp_path,kind):
 seed=[10,5,15,3,7];history=[{'operation':'insertar','payload':{'value':x}} for x in seed];data=S.execute_operation('red_black','validar',{},history);state=deepcopy(S.get_view_model('red_black',history)['visual_state']);nodes=[]
 def visit(n):
  if n is None:return
  nodes.append(n);visit(n['left']);visit(n['right'])
 visit(state['root'])
 index,field,value={'root_red':(0,'color','RED'),'duplicate':(1,'value',10),'ancestor_order':(2,'value',20),'red_red':(1,'color','RED')}[kind];nodes[index][field]=value
 mutation=f'nodes[{index}]->'+('rbt_color=ROJO;' if field=='color' else 'nro='+str(value)+';')
 trace=deepcopy(data['execution_trace']);trace['source_code']=CCodeService.get_structure_data('red_black')['operations']['validar'];after=deepcopy(state);after['validation']=False;trace=build_rbt_query_trace(trace,state,after)
 client=create_app().test_client();events=observe(trace['source_code'],'validar',seed,0,client.get('/help/source/red_black/source').data,client.get('/help/source/red_black/header').data,tmp_path,mutation)
 match(trace,events);assert events[-1]['wrapper']==0 and trace['steps'][-1]['pedagogy']['memory_state']['wrapper_result']==0
 # Root failure must not enter the recursive helper; a left-subtree failure skips the root right call.
 if kind=='root_red':assert not any(any(f['function']=='rbt_validar_altura_negra' for f in e['frames']) for e in events)
 else:assert not any(any(f['function']=='rbt_validar_altura_negra' and f['parameters']['nodo']==5 for f in e['frames']) for e in events)
