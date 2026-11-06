"""Real hierarchy renderer and ClassroomView observer, not a browser/layout claim."""
from copy import deepcopy
import json,subprocess
from pathlib import Path
import pytest
from e2e_hierarchical_contract import same_nodes,memory_cards,color_label,assert_stack_records
from test_audit_avl_validate_e2e import COLLECT
from app.services.hierarchical_structure_service import HierarchicalStructureService as S

@pytest.mark.parametrize('family,operation,payload',[
 ('abb','minimo',{}),('abb','validar',{}),('abb','eliminar',{'value':3}),
 ('avl','insertar',{'value':4}),('avl','eliminar',{'value':3}),('avl','validar',{}),
 ('avl','altura',{}),('avl','buscar',{'value':5}),
 ('red_black','insertar',{'value':4}),('red_black','eliminar',{'value':3}),('red_black','buscar',{'value':5}),
])
def test_real_hierarchical_renderer_keeps_identity_and_ended_scopes(tmp_path,family,operation,payload):
 history=[]
 for v in [7,3,9,1,5]:
  data=S.execute_operation(family,'insertar',{'value':v},history);assert data['success'];history=data['history']
 data=S.execute_operation(family,operation,payload,history);assert data['success']
 trace=data['execution_trace'];path=tmp_path/'input.json'
 collect=COLLECT
 if operation in ['insertar','eliminar'] and family in ['avl','red_black']:
  import importlib
  module='test_audit_'+('rbt' if family=='red_black' else 'avl')+('_insert' if operation=='insertar' else '_delete')+('_instruction' if family=='red_black' else '')+'_e2e'
  collect=importlib.import_module(module).COLLECT
 path.write_text(json.dumps({'family':family,'trace':trace,'collect':collect}))
 root=Path(__file__).resolve().parents[1]
 run=subprocess.run(['node','qa/emit_e2e_hierarchical_records.js',str(path)],cwd=root,capture_output=True,text=True,timeout=60)
 assert run.returncode==0,run.stderr
 rows=json.loads(run.stdout);assert len(rows)==2*len(trace['steps'])
 for row in rows:
  ped=trace['steps'][row['index']]['pedagogy'] if row['index']>=0 else trace['steps'][0]['pedagogy']['initial_frame']
  state=ped['memory_state'];assert row['state']==state
  same_nodes(row['nodes'],[{k:n[k] for k in ['id','value','left','right','status']} for n in state['heap_nodes']])
  for node,card in memory_cards(row,state['heap_nodes']):
   if family=='avl':assert 'padre: '+node['parent'] in card and 'FE: '+str(node['balance_factor']) in card
   if family=='red_black':assert 'padre: '+node['parent'] in card and 'color: '+color_label(node['color']) in card
  assert_stack_records(row['stackRecords'],ped)
  if 'svgNodes' in row:
   if family=='avl':assert row['svgNodes']==[{'id':n['id'],'status':n['status'],'parent':str(n['parent']),'fe':str(n['balance_factor'])} for n in state['heap_nodes']]
   else:assert row['svgNodes']==[{'id':n['id'],'parent':n['parent'],'color':n['color'],'initialized':n['initialized'],'red':n['color']=='RED','black':n['color']=='BLACK'} for n in state['heap_nodes']]
  if 'retiredNodes' in row:
   same_nodes(row['retiredNodes'],[{'id':n['id'],'value':n['value']} for n in state['freed_nodes']])
 # The mounted renderer replaces old optional memory asynchronously. The old
 # collector observes duplicates before that microtask, instead of a paintable DOM.
 if family=='avl' and operation=='eliminar':
  path.write_text(json.dumps({'family':family,'trace':trace,'collect':collect.replace('   await new Promise(resolve=>requestAnimationFrame(resolve));\n','')}))
  run=subprocess.run(['node','qa/emit_e2e_hierarchical_records.js',str(path)],cwd=root,capture_output=True,text=True,timeout=60)
  assert run.returncode==0,run.stderr
  old=json.loads(run.stdout)
  assert any(len(r['nodes'])!=len(r['state']['heap_nodes']) for r in old)

@pytest.mark.parametrize('damage',['missing','duplicate','value','root','link','status'])
def test_identity_observer_rejects_corrupted_or_duplicated_memory(damage):
 expected=[dict(id='N1',value=7,left='N2',right='NULL',status='linked'),dict(id='N2',value=3,left='NULL',right='NULL',status='linked')]
 actual=deepcopy(expected[::-1]);assert same_nodes(actual,expected)
 if damage=='missing':actual.pop()
 elif damage=='duplicate':actual.append(deepcopy(actual[0]))
 else:actual[0][{'root':'id','link':'left'}.get(damage,damage)]='FORGED'
 with pytest.raises(AssertionError):same_nodes(actual,expected)

@pytest.mark.parametrize('damage',['active','history','root','return','function'])
def test_scope_observer_rejects_missing_or_corrupted_frames(damage):
 frame={'call_stack':[],'completed_call_stack':[{'function':'f','local_root':'N1','return':7}]}
 row={'live':[],'completed':['f · ámbito terminado (registro histórico)raíz local registrada: N1retorno: 7'],'details':1}
 assert_stack_records(row,frame)
 if damage=='active':row['live']=row['completed'][:]
 elif damage=='history':row['completed']=[]
 else:row['completed'][0]=row['completed'][0].replace({'root':'N1','return':'7','function':'f ·'}[damage],'FORGED')
 with pytest.raises(AssertionError):assert_stack_records(row,frame)


def test_abb_documentation_compiles_real_downloads_and_still_rejects_bad_docs(tmp_path):
 from app import create_app
 from test_audit_abb_validate_e2e import compile_main
 class Response:
  def __init__(self,data):self.data=data
  def body(self):return self.data
 class Context:
  def __init__(self):self.request=self
  def get(self,url):
   with create_app().test_client() as client:
    response=client.get(url);assert response.status_code==200
    return Response(response.data)
 main='#include "tad_abb.h"\n/** @brief Comprueba la descarga. @return Cero. */\nint main(void){return 0;}\n'
 assert compile_main(main,Context(),'',tmp_path/'good')==''
 broken=main.replace('@return Cero.', '@param nonexistent No existe este parámetro. @return Cero.')
 with pytest.raises(AssertionError):compile_main(broken,Context(),'',tmp_path/'bad')
