"""Behavioral tests for current public flows among the40assigned controls."""
from __future__ import annotations
from pathlib import Path
import json,threading
import pytest
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from test_residual58_focal_cases import residual58_app

@pytest.fixture
def controls40_page(residual58_app):
 server=make_server('127.0.0.1',0,residual58_app,threaded=True);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
 with sync_playwright() as pw:
  browser=pw.chromium.launch();context=browser.new_context(viewport={'width':1366,'height':1000},accept_downloads=True);page=context.new_page();page.set_default_timeout(7000)
  yield page,context,f'http://127.0.0.1:{server.server_port}'
  context.close();browser.close()
 server.shutdown();thread.join(timeout=5)

@pytest.mark.e2e
@pytest.mark.parametrize('module,path,button,mirror',[
 ('graph','/graph/graph/construccion','#graph-sim-step','#graph-step-toggle'),
 ('hash','/hash/hash_table','#hash-sim-step','#hash-step-toggle'),
 ('hierarchical','/hierarchical/abb','#hier-step-mode','#hier-step-toggle'),
 ('sorting','/sorting/visualizador','#sorting-sim-step','#sorting-step-toggle'),
])
def test_controls40_public_mode_changes_internal_state(controls40_page,module:str,path:str,button:str,mirror:str)->None:
 page,context,base=controls40_page;page.goto(base+path,wait_until='networkidle')
 assert not page.locator(mirror).is_checked()
 page.click(button)
 assert page.locator(mirror).is_checked()
 assert page.locator(button).get_attribute('aria-pressed')=='true'
 page.click(button)
 assert not page.locator(mirror).is_checked()
 assert page.locator(button).get_attribute('aria-pressed')=='false'

@pytest.mark.e2e
@pytest.mark.parametrize('module,path,checkbox',[
 ('graph','/graph/graph/expansion-minima','#graph-hide-comments'),
 ('hash','/hash/hash_table','#hash-hide-comments'),
 ('hierarchical','/hierarchical/abb','#hier-hide-comments'),
])
def test_controls40_comments_hide_and_restore_real_source(controls40_page,module:str,path:str,checkbox:str)->None:
 page,context,base=controls40_page;page.goto(base+path,wait_until='networkidle')
 if module=='hash':page.select_option('#hash-operation-select','keys')
 visible="()=>[...document.querySelectorAll('#op-pseudocode .is-code-comment,#op-pseudocode .code-comment,#op-pseudocode .code-doc')].filter(e=>getComputedStyle(e).display!=='none'&&e.getClientRects().length).length"
 before=page.evaluate(visible);assert before>0,'No current source comments to exercise this control'
 page.check(checkbox);assert page.locator(checkbox).is_checked();assert page.evaluate(visible)<before
 page.uncheck(checkbox);assert page.evaluate(visible)==before

@pytest.mark.e2e
def test_controls40_graph_reset_changes_private_graph(controls40_page)->None:
 page,context,base=controls40_page
 for operation,payload in [('create_graph',{'directed':True}),('insert_vertex',{'vertex':7})]:
  response=context.request.post(base+'/graph/graph/operate',data={'operation':operation,'payload':payload});assert response.status==200
 page.goto(base+'/graph/graph/construccion',wait_until='networkidle');page.on('dialog',lambda dialog:dialog.accept())
 with page.expect_response(lambda response:response.url.endswith('/graph/graph/reset') and response.request.method=='POST') as response:page.click('#graph-reset-button')
 assert response.value.status==200;assert response.value.json()['visual_state']['nodes']==[]
 query=context.request.post(base+'/graph/graph/operate',data={'operation':'list_vertices','payload':{}});assert query.json()['result']==[]

@pytest.mark.e2e
def test_controls40_stack_main_download_contains_real_C_history(controls40_page,tmp_path:Path)->None:
 page,context,base=controls40_page
 response=context.request.post(base+'/sequential/stack/operate',data={'operation':'apilar','payload':{'value':7}});assert response.status==200
 page.goto(base+'/sequential/stack',wait_until='networkidle')
 with page.expect_download() as downloaded:page.click('#stack-main-download')
 dest=tmp_path/'main.c';downloaded.value.save_as(dest);source=dest.read_text(encoding='utf-8-sig')
 assert downloaded.value.suggested_filename=='main.c'
 assert 'int main(' in source and 'pila_apilar' in source and '7' in source
 assert 'pila_destruir' in source
def open_optional_panel(page,label:str)->None:
 toggle=page.locator('.seq-understand .seq-pilot-toggle')
 if toggle.get_attribute('aria-expanded')=='false':toggle.click()
 summary=page.locator('.seq-understand details > summary').filter(has_text=label)
 if not summary.evaluate('(e)=>e.parentElement.open'):summary.click()

@pytest.mark.e2e
def test_controls40_optional_comparison_changes_results(controls40_page)->None:
 page,context,base=controls40_page;page.goto(base+'/sequential/queue',wait_until='networkidle');open_optional_panel(page,'Comparar conceptos')
 posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
 page.select_option('#seq-compare-kind','stack-queue');page.click('#seq-compare-run')
 assert page.locator('#seq-compare-grid .seq-compare-sequence').all_text_contents()==['10, 20, 30','10, 20, 30']
 page.locator('#seq-compare-progress').fill('2')
 assert page.locator('#seq-compare-grid .seq-compare-sequence').all_text_contents()==['sale 30 (LIFO)','sale 10 (FIFO)']
 page.select_option('#seq-compare-kind','queue-priority')
 assert page.locator('#seq-compare-progress').input_value()=='0'
 assert page.locator('#seq-compare-grid h4').all_text_contents()==['Cola','Cola de prioridad']
 page.locator('#seq-compare-progress').fill('2')
 assert page.locator('#seq-compare-grid .seq-compare-sequence').all_text_contents()==['sale 10 por llegada','sale 20 por prioridad']
 assert not posts

@pytest.mark.e2e
def test_controls40_prediction_practice_and_progress_reset(controls40_page)->None:
 page,context,base=controls40_page;page.goto(base+'/sequential/stack',wait_until='networkidle');open_optional_panel(page,'Predecir')
 page.check('#seq-predictions-enabled');page.check('#seq-practice-mode')
 page.locator('#field-value').fill('7');page.click('#seq-step-mode');page.click('#seq-sim-execute')
 for _ in range(8):
  if page.locator('#seq-prediction-panel').is_visible():break
  page.click('#seq-sim-step')
 assert page.locator('#seq-prediction-panel').is_visible()
 assert page.locator('#visual-state').evaluate('(e)=>e.classList.contains("seq-practice-hidden")')
 page.uncheck('#seq-practice-mode')
 assert not page.locator('#visual-state').evaluate('(e)=>e.classList.contains("seq-practice-hidden")')
 page.locator('#seq-prediction-choices [data-answer="true"]').click()
 assert page.evaluate("JSON.parse(sessionStorage.getItem('sequential-learning-progress:stack')).attempts")==1
 page.click('#seq-reset-learning')
 assert page.evaluate("JSON.parse(sessionStorage.getItem('sequential-learning-progress:stack'))")=={'attempts':0,'correct':0,'concepts':{}}
 assert '0/0' in page.locator('#seq-concept-progress').inner_text()
