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
 ('graph','/graph/graph/recorridos','#graph-hide-comments'),
 ('hash','/hash/hash_table','#hash-hide-comments'),
 ('hierarchical','/hierarchical/abb','#hier-hide-comments'),
])
def test_controls40_comments_hide_and_restore_real_source(controls40_page,module:str,path:str,checkbox:str)->None:
 page,context,base=controls40_page;page.goto(base+path,wait_until='networkidle')
 # Source comments are exercised in the explicitly enabled technical view.
 page.locator('label[for="didactic-mode-switch"]').click()
 page.wait_for_function("document.documentElement.getAttribute('data-didactic-mode') === 'full'")
 if module=='graph':page.select_option('#graph-algorithm-select','run_bfs')
 if module=='hash':page.select_option('#hash-operation-select','keys')
 visible="()=>[...document.querySelectorAll('#op-pseudocode .is-code-comment,#op-pseudocode .code-comment,#op-pseudocode .code-doc')].filter(e=>getComputedStyle(e).display!=='none'&&e.getClientRects().length).length"
 before=page.evaluate(visible);assert before>0,'No current source comments to exercise this control'
 page.check(checkbox);assert page.locator(checkbox).is_checked();assert page.evaluate(visible)<before
 page.uncheck(checkbox);assert page.evaluate(visible)==before

@pytest.mark.e2e
def test_controls40_graph_comments_toggle_preserves_prim_scope(controls40_page)->None:
 page,context,base=controls40_page
 posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
 page.goto(base+'/graph/graph/expansion-minima',wait_until='networkidle')
 page.locator('label[for="didactic-mode-switch"]').click()
 page.wait_for_function("document.documentElement.getAttribute('data-didactic-mode') === 'full'")
 page.select_option('#graph-algorithm-select','run_prim')
 code=page.locator('#op-pseudocode')
 assert code.get_attribute('data-operation')=='run_prim'
 rows=code.locator('.code-line')
 native_rows=rows.evaluate_all("rows=>rows.map(row=>[row.getAttribute('data-line'),row.textContent])")
 assert [int(row[0]) for row in native_rows]==list(range(len(native_rows)))
 bfs_comment=code.locator('.code-line[data-line="323"]')
 assert 'prev se usa aqui como cola de indices, con capacidad n' in bfs_comment.text_content()
 excluded=code.locator('.graph-code-excluded')
 excluded_indices=excluded.evaluate_all("rows=>rows.map(row=>row.getAttribute('data-line'))")
 assert '323' in excluded_indices
 for hidden in (False,True,False):
  page.locator('#graph-hide-comments').set_checked(hidden)
  assert page.locator('#graph-hide-comments').is_checked()==hidden
  assert code.get_attribute('data-operation')=='run_prim'
  assert excluded.evaluate_all("rows=>rows.map(row=>row.getAttribute('data-line'))")==excluded_indices
  assert excluded.evaluate_all("rows=>rows.every(row=>getComputedStyle(row).display==='none' && !row.getClientRects().length)")
  assert not bfs_comment.is_visible()
  assert rows.evaluate_all("rows=>rows.map(row=>[row.getAttribute('data-line'),row.textContent])")==native_rows
 assert not posts

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
 page.locator('label[for="didactic-mode-switch"]').click()
 page.wait_for_function("document.documentElement.getAttribute('data-didactic-mode') === 'full'")
 page.get_by_role('tab',name='Estructura del TAD',exact=True).click()
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

def prediction_graph_snapshot(page):
 # Pila uses real HTML memory nodes; include SVG drawings when a view has them.
 graph=page.locator('#visual-state')
 assert graph.is_visible()
 graph.locator('[data-stack-push-root]').wait_for(state='visible')
 assert graph.locator('[data-stack-push-root]').count()==1
 return graph.locator('[data-stack-push-root],[data-stack-push-aux-valid],.stack-linked-chain,svg').evaluate_all("nodes=>nodes.map(node=>node.outerHTML)")

def assert_prediction_aids_masked(page):
 for selector in ('#seq-code-region','#seq-pedagogy-summary','.seq-c-semantics','#seq-printf-console','#action-history'):
  node=page.locator(selector)
  assert node.count()==1
  assert not node.is_visible()
  assert node.get_attribute('aria-hidden')=='true'

@pytest.mark.e2e
def test_controls40_prediction_practice_and_progress_reset(controls40_page)->None:
 page,context,base=controls40_page;page.goto(base+'/sequential/stack',wait_until='networkidle');open_optional_panel(page,'Predecir')
 page.locator('label[for="didactic-mode-switch"]').click()
 page.wait_for_function("document.documentElement.getAttribute('data-didactic-mode') === 'full'")
 page.check('#seq-predictions-enabled');page.check('#seq-practice-mode')
 page.locator('#field-value').fill('7');page.click('#seq-step-mode');page.click('#seq-sim-execute')
 previous=prediction_graph_snapshot(page)
 for _ in range(8):
  if page.locator('#seq-prediction-panel').is_visible():break
  previous=prediction_graph_snapshot(page)
  page.click('#seq-sim-step')
 assert page.locator('#seq-prediction-panel').is_visible()
 assert prediction_graph_snapshot(page)==previous
 assert_prediction_aids_masked(page)
 page.uncheck('#seq-practice-mode')
 assert prediction_graph_snapshot(page)==previous
 assert page.locator('#seq-code-region').is_visible()
 assert page.locator('#seq-pedagogy-summary').get_attribute('aria-hidden')!='true'
 page.locator('#seq-prediction-choices [data-answer="true"]').click()
 assert page.evaluate("JSON.parse(sessionStorage.getItem('sequential-learning-progress:stack')).attempts")==1
 page.click('#seq-reset-learning')
 assert page.evaluate("JSON.parse(sessionStorage.getItem('sequential-learning-progress:stack'))")=={'attempts':0,'correct':0,'concepts':{}}
 assert '0/0' in page.locator('#seq-concept-progress').inner_text()

@pytest.mark.e2e
@pytest.mark.parametrize('decision',['answer','skip'])
def test_prediction_publication_preserves_previous_until_decision(controls40_page,decision):
 page,context,base=controls40_page
 page.goto(base+'/sequential/stack',wait_until='networkidle');open_optional_panel(page,'Predecir')
 page.locator('label[for="didactic-mode-switch"]').click()
 page.wait_for_function("document.documentElement.getAttribute('data-didactic-mode') === 'full'")
 page.check('#seq-practice-mode')
 page.click('#seq-reset-learning')
 page.locator('#field-value').fill('7');page.click('#seq-step-mode')
 with page.expect_response(lambda r:r.url.endswith('/sequential/stack/operate') and r.request.method=='POST') as response:
  page.click('#seq-sim-execute')
 body=response.value.json();assert response.value.status==200 and body['success']
 steps=body['execution_trace']['steps']
 # Choose a real root-publication event, not a condition with identical pictures.
 target=next(i for i,step in enumerate(steps) if step['event_type']=='root_assigned')
 assert target>0
 detail=page.locator('#seq-progress-detail')
 assert target<len(steps)<=10
 page.wait_for_function("document.querySelector('#seq-progress-detail').textContent.startsWith('Paso 0 ·')")
 for position in range(1,target+1):
  page.click('#seq-sim-step')
  page.wait_for_function("n=>document.querySelector('#seq-progress-detail').textContent.startsWith('Paso '+n+' ·')",arg=position)
 before=prediction_graph_snapshot(page)
 assert page.locator('[data-stack-push-root]').get_attribute('data-stack-push-root')=='NULL'
 assert page.locator('[data-stack-push-status="temporary"]').count()==1
 page.click('#seq-sim-step')
 page.wait_for_function("n=>document.querySelector('#seq-progress-detail').textContent.startsWith('Paso '+n+' ·')",arg=target+1)
 after=prediction_graph_snapshot(page)
 assert page.locator('[data-stack-push-root]').get_attribute('data-stack-push-root')=='push-new'
 assert page.locator('[data-stack-push-status="linked"]').count()==1
 assert page.locator('[data-stack-push-field="nro"] strong').inner_text()=='7'
 assert before!=after,'The chosen root publication must change the actual displayed memory'
 page.click('#seq-sim-prev')
 page.wait_for_function("n=>document.querySelector('#seq-progress-detail').textContent.startsWith('Paso '+n+' ·')",arg=target)
 assert prediction_graph_snapshot(page)==before
 posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
 page.check('#seq-predictions-enabled')
 page.click('#seq-sim-step')
 assert page.locator('#seq-prediction-panel').is_visible()
 assert f'Antes del paso {target+1}:' in page.locator('#seq-prediction-question').inner_text()
 assert detail.inner_text().startswith(f'Paso {target} ·')
 assert prediction_graph_snapshot(page)==before
 assert_prediction_aids_masked(page)
 # Safe hints must not render the target event either, even after repeated clicks.
 for _ in range(3):page.click('#seq-prediction-hint')
 assert 'Sí existe una transición registrada.' not in page.locator('#seq-prediction-feedback').inner_text()
 assert prediction_graph_snapshot(page)==before
 assert detail.inner_text().startswith(f'Paso {target} ·')
 button=page.locator('#seq-prediction-choices [data-answer="true"]' if decision=='answer' else '#seq-prediction-skip')
 assert button.is_visible()
 # Retain the same actual button for two immediate activations; no state injection.
 button.evaluate('(button)=>{button.click();button.click();}')
 page.wait_for_function("n=>document.querySelector('#seq-progress-detail').textContent.startsWith('Paso '+n+' ·')",arg=target+1)
 assert not page.locator('#seq-prediction-panel').is_visible()
 assert prediction_graph_snapshot(page)==after
 progress=page.evaluate("JSON.parse(sessionStorage.getItem('sequential-learning-progress:stack'))")
 assert progress==({'attempts':1,'correct':1,'concepts':{'assignment':1}} if decision=='answer' else {'attempts':0,'correct':0,'concepts':{}})
 assert detail.inner_text().startswith(f'Paso {target+1} ·')
 assert not posts
