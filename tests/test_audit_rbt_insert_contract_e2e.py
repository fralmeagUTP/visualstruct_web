"""Actual browser rejection/history/reload and downloaded C/H final caller cleanup."""
import json,re
import pytest
from test_audit_avl_main_e2e import avl_server
from test_audit_rbt_queries_main_e2e import compile_main
from test_audit_rbt_insert_main_e2e import observe_owner
pytestmark=pytest.mark.e2e

@pytest.mark.parametrize('mixed',[False,True])
def test_actual_range_rejection_and_final_owner_after_repeat_reload(avl_server,tmp_path,mixed):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
  page.goto(avl_server+'/hierarchical/red_black',wait_until='networkidle');assert page.locator('#operation-select option').count()==7
  def op(name,value=None):
   page.select_option('#operation-select',name)
   if value is not None:page.locator('[name="value"]').fill(str(value))
   with page.expect_response(lambda r:r.url.endswith('/red_black/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
   data=response.value.json();page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled");return data
  expected='';allocated=0
  if mixed:
   for v in [10,5,15]:assert op('insertar',v)['success'];expected+='\tEl numero ha sido insertado\n';allocated+=1
   for _ in range(2):assert op('inorden')['result']==[5,10,15];expected+='INORDEN: 5 10 15 \n'
   for _ in range(2):assert op('limpiar')['success'];expected+='LIMPIAR\n'
   for v in [-2147483648,2147483647]:assert op('insertar',v)['success'];expected+='\tEl numero ha sido insertado\n';allocated+=1
   assert not op('insertar',2147483647)['success']
  if not mixed:assert op('limpiar')['success'];expected+='LIMPIAR\n'
  history=None;state=None
  # Range rejection is rendered as application rejection, never as C execution.
  page.click('#hier-step-mode')
  for value in [-2147483649,2147483648]:
   bad=op('insertar',value);assert not bad['success'];t=bad['execution_trace'];assert t['application_precondition_rejected'];assert '-2147483648' in bad['message'] and '2147483647' in bad['message'];assert len(t['steps'])==1
   if history is None:history=bad['history'];state=bad['visual_state']
   else:assert bad['history']==history and bad['visual_state']==state
   assert page.locator('#hier-printf-console').text_content()==''
   n=len(posts);page.click('#hier-sim-step');page.wait_for_function("()=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: 1/')");assert page.locator('#hier-printf-console').text_content()=='';assert 'Solicitud rechazada' in page.locator('#op-pseudocode .sim-active,#op-pseudocode .sim-done').inner_text()
   page.click('#hier-sim-prev');page.wait_for_function("()=>document.querySelector('#hier-sim-counter').textContent.startsWith('Paso: 0/')");assert page.locator('#hier-printf-console').text_content()=='' and len(posts)==n
  mains=[];programs=[]
  for label in ['before','after']:
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');mains.append(main)
   body=re.sub(r'/\*.*?\*/|//[^\n]*','',main.split('int main(void)',1)[1],flags=re.S)
   assert 'rbt_liberar(arbol); arbol = NULL;' in body and '2147483648)' not in body.replace('-2147483648)','MIN)') and '-2147483649' not in body
   assert body.count('rbt_insertar(&arbol,')==allocated and body.count('rbt_liberar(arbol); arbol = NULL;')==(3 if mixed else 2)
   target=tmp_path/label;program=compile_main(main,context,avl_server,target);assert program['stdout']==expected
   owner=observe_owner(target,allocated,expected);assert owner['freed']==allocated and owner['live_at_exit']==0 and owner['executable_final_cleanup'];program['owner']=owner;programs.append(program)
   if label=='before':count=len(posts);page.reload(wait_until='networkidle');assert len(posts)==count
  assert mains[0]==mains[1] and not errors;context.close();browser.close()
 (tmp_path/'range-owner-history-review.json').write_text(json.dumps({'mixed':mixed,'programs':programs,'range_rejections':2,'repeat_cleanup':mixed,'repeat_queries':mixed,'reload_no_POST':True,'generated_main_stable':True,'errors':errors},indent=2),encoding='utf-8')
