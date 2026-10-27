"""Actual visible deletion histories compile/download/reload and free ownership."""
import json,re
import pytest
from test_audit_avl_main_e2e import avl_server
from test_audit_rbt_queries_main_e2e import compile_main
from test_audit_rbt_insert_main_e2e import observe_owner
pytestmark=pytest.mark.e2e
@pytest.mark.parametrize('seed,value',[([10],10),([10,5],10),([10,5,15],10),([11,2,14,1,7,15,5,8,4],11)])
def test_delete_actual_history_main_rejection_repeat_reload(avl_server,tmp_path,seed,value):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];errors=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  for v in seed:assert context.request.post(avl_server+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
  page.goto(avl_server+'/hierarchical/red_black',wait_until='networkidle');assert page.locator('#operation-select option').count()==7;page.select_option('#operation-select','eliminar');page.locator('[name="value"]').fill(str(value))
  def remove():
   with page.expect_response(lambda r:r.url.endswith('/red_black/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
   data=response.value.json();page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled");return data
  success=remove();assert success['success'];page.click('#hier-step-mode');failure=remove();assert not failure['success'] and failure['history']==success['history'] and failure['visual_state']==success['visual_state']
  assert failure['execution_trace']['application_precondition_rejected'];assert page.locator('#hier-printf-console').text_content()=='';n=len(posts);page.click('#hier-sim-step');page.wait_for_function("()=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: 1/')");assert 'rbt_eliminar NO fue invocado' in page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').inner_text();assert page.locator('#hier-printf-console').text_content()==''
  page.click('#hier-sim-prev');page.wait_for_function("()=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: 0/')");assert page.locator('#hier-printf-console').text_content()=='' and len(posts)==n
  mains=[];programs=[]
  for label in ['before','after']:
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');mains.append(main);body=re.sub(r'/\*.*?\*/|//[^\n]*','',main.split('int main(void)',1)[1],flags=re.S)
   assert list(map(int,re.findall(r'rbt_insertar\(&arbol,\s*(-?\d+)\);',body)))==seed;assert re.findall(r'rbt_eliminar\(&arbol,\s*(-?\d+)\);',body)==[str(value)];assert 'rbt_liberar(arbol); arbol = NULL;' in body
   target=tmp_path/label;program=compile_main(main,context,avl_server,target);expected='\tEl numero ha sido insertado\n'*len(seed)+'ELIMINAR invocado: '+str(value)+'\n';assert program['stdout']==expected;program['owner']=observe_owner(target,len(seed),expected);assert program['owner']['freed']==len(seed) and program['owner']['live_at_exit']==0;programs.append(program)
   if label=='before':n=len(posts);page.reload(wait_until='networkidle');assert len(posts)==n
  assert mains[0]==mains[1] and not errors;context.close();browser.close()
 (tmp_path/'delete-actual-main-review.json').write_text(json.dumps({'seed':seed,'value':value,'programs':programs,'duplicate_delete_excluded':True,'reload_no_POST':True,'native_delete_printf':False,'caller_output_separate':True,'success_instruction_UI_pending':True,'errors':errors},indent=2),encoding='utf-8');print('RBT delete actual main verified',seed,value,flush=True)
