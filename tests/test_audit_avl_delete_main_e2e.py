"""Actual visible deletion history and downloaded void C caller."""
from pathlib import Path
import pytest,json
from test_audit_avl_main_e2e import avl_server,compile_main
pytestmark=pytest.mark.e2e
@pytest.mark.parametrize('seed,value', [([10],10),([10,5],10),([40,20,60,10,30,50,70,45,55],40),([5,2,6,4],6)])
def test_avl_delete_actual_history_reload_void_and_downloaded_tree(avl_server,tmp_path,seed,value):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];errors=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  for v in seed:assert context.request.post(avl_server+'/hierarchical/avl/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
  page.goto(avl_server+'/hierarchical/avl',wait_until='networkidle');page.select_option('#operation-select','eliminar');page.locator('[name="value"]').fill(str(value))
  with page.expect_response(lambda response:response.url.endswith('/avl/operate') and response.request.method=='POST') as response:page.click('#hier-sim-play')
  data=response.value.json();assert data['success'];mains=[];programs=[]
  def printed(n,depth=0):return '' if n is None else printed(n['right'],depth+1)+'   '*depth+str(n['value'])+'\n'+printed(n['left'],depth+1)
  for label in ['before','after']:
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert main.count('avl_eliminar(&arbol,')==1 and main.count('avl_insertar(&arbol,')==len(seed);mains.append(main)
   # Append a real read of the resulting C tree before cleanup; no expected snapshot is injected.
   assert main.count('avl_liberarAVL(arbol);')==1
   actual=compile_main(main,context,avl_server,tmp_path/('actual-'+label));assert actual['stdout'].splitlines()==['INSERTAR invocado: '+str(v) for v in seed]+['ELIMINAR invocado: '+str(value)];programs.append(actual)
   assert '// avl_liberarAVL(arbol);' in main
   tree_main=main.replace('// avl_liberarAVL(arbol);','puts("AUDIT_TREE_BEGIN");\n    avl_verArbol(arbol, 0);\n    puts("AUDIT_TREE_END");\n    avl_liberarAVL(arbol);')
   program=compile_main(tree_main,context,avl_server,tmp_path/('main-'+label));tree_output=program['stdout'].split('AUDIT_TREE_BEGIN\n',1)[1].split('AUDIT_TREE_END\n',1)[0];assert tree_output==printed(data['visual_state']['root']);programs.append(program)
   if label=='before':count=len(posts);page.reload(wait_until='networkidle');assert len(posts)==count
  assert mains[0]==mains[1], 'Downloaded operation history changed after reload';assert not errors
  context.close();browser.close()
 (tmp_path/'avl-delete-main-review.json').write_text(json.dumps({'seed':seed,'value':value,'programs':programs,'main_stable_after_reload':True,'extra_reload_posts':0,'errors':errors},indent=2),encoding='utf-8')
