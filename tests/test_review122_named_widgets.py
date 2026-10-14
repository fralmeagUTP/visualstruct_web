"""Current named-widget behavior among the97 candidates; isolated real requests."""
from __future__ import annotations
from pathlib import Path
import json,re
from PIL import Image
from playwright.sync_api import expect
from test_controls40_real_flows import controls40_page,open_optional_panel
from test_residual58_focal_cases import residual58_app

def seed(context,base,module,sid,operations):
 for operation,payload in operations:
  response=context.request.post(f'{base}/{module}/{sid}/operate',data={'operation':operation,'payload':payload});assert response.status==200

def cursor(page,selector):
 text=page.locator(selector).inner_text();return int(re.search(r'Paso:\s*(\d+)/',text).group(1))

def test_review122_graph_type_apply_resets_private_graph(controls40_page):
 page,context,base=controls40_page;seed(context,base,'graph','graph',[('create_graph',{'directed':False}),('insert_vertex',{'vertex':7})]);page.goto(base+'/graph/graph/construccion',wait_until='networkidle');page.select_option('#graph-mode-select','true')
 with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-create-button')
 data=response.value.json();assert response.value.status==200;assert data['visual_state']['directed'] is True and data['visual_state']['nodes']==[]

def test_review122_graph_next_previous_reuse_one_trace(controls40_page):
 page,context,base=controls40_page;page.goto(base+'/graph/graph/construccion',wait_until='networkidle');page.select_option('#graph-operation-select','insert_vertex');page.locator('[name="vertex"]').fill('7');page.click('#graph-sim-step')
 with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST'):page.click('#graph-sim-play')
 expect(page.locator('#graph-sim-counter')).to_have_text(re.compile(r'Paso: 0/'))
 posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
 page.click('#graph-sim-next');expect(page.locator('#graph-sim-counter')).to_have_text(re.compile(r'Paso: 1/'))
 page.click('#graph-sim-prev');expect(page.locator('#graph-sim-counter')).to_have_text(re.compile(r'Paso: 0/'))
 assert not posts

def test_review122_hash_filter_and_addresses_are_presentation_only(controls40_page):
 page,context,base=controls40_page;seed(context,base,'hash','hash_table',[('create_table',{'capacity':3}),('insert',{'key':1,'value':7})]);page.goto(base+'/hash/hash_table',wait_until='networkidle')
 posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
 page.select_option('#hash-bucket-filter','occupied');assert page.locator('.hash-entry').count()==1
 assert page.locator('.hash-bucket').count()==1
 page.select_option('#hash-bucket-filter','all');assert page.locator('.hash-bucket').count()==3
 page.uncheck('#hash-show-addresses');assert page.locator('.hash-node-address').all_text_contents()==['nodo']
 page.check('#hash-show-addresses');assert page.locator('.hash-node-address').all_text_contents()!=['nodo']
 assert not posts

def test_review122_hash_next_reuses_trace(controls40_page):
 page,context,base=controls40_page;seed(context,base,'hash','hash_table',[('create_table',{'capacity':3})]);page.goto(base+'/hash/hash_table',wait_until='networkidle');page.select_option('#hash-operation-select','insert');page.locator('#hash-field-key').fill('1');page.locator('#hash-field-value').fill('7');page.click('#hash-sim-step')
 with page.expect_response(lambda r:r.url.endswith('/hash/hash_table/operate') and r.request.method=='POST'):page.click('#hash-sim-play')
 expect(page.locator('#hash-sim-counter')).to_have_text(re.compile(r'Paso: 0/'));page.click('#hash-sim-next');expect(page.locator('#hash-sim-counter')).to_have_text(re.compile(r'Paso: 1/'))

def test_review122_hash_real_main_download_from_results(controls40_page,tmp_path:Path):
 page,context,base=controls40_page;seed(context,base,'hash','hash_table',[('create_table',{'capacity':3}),('insert',{'key':1,'value':7})]);page.goto(base+'/hash/hash_table',wait_until='networkidle')
 toggle=page.locator('#hash-results-toggle')
 if toggle.count() and toggle.get_attribute('aria-expanded')=='false':toggle.click()
 from test_residual97_navigation import reveal_with_public_control
 reveal_with_public_control(page,page.locator('#hash-download-main'))
 with page.expect_download() as download:page.click('#hash-download-main')
 target=tmp_path/'hash-main.c';download.value.save_as(target);source=target.read_text(encoding='utf-8-sig');assert 'int main(' in source and 'th_insertar' in source and '7' in source

def test_review122_sorting_random_inputs_and_reset(controls40_page):
 page,context,base=controls40_page;page.goto(base+'/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-random-size').fill('3');page.locator('#sorting-random-min').fill('7');page.locator('#sorting-random-max').fill('7')
 with page.expect_response(lambda r:r.url.endswith('/api/ordenamiento/random-array') and r.request.method=='POST') as generated:page.click('#sorting-random-array')
 assert generated.value.status==200 and generated.value.json()['visual_state']['items']==[7,7,7]
 page.on('dialog',lambda dialog:dialog.accept())
 with page.expect_response(lambda r:r.url.endswith('/api/ordenamiento/reset') and r.request.method=='POST') as cleared:page.click('#sorting-reset')
 assert cleared.value.status==200 and cleared.value.json()['visual_state']['items']==[]

def test_review122_export_quality_changes_real_jpeg(controls40_page,tmp_path:Path):
 page,context,base=controls40_page;response=context.request.post(base+'/api/ordenamiento/create-array',data={'values':[7,2,9]});assert response.status==200;page.goto(base+'/sorting/visualizador',wait_until='networkidle');page.select_option('#export-jpg-scale','1');results=[]
 for quality in ['0.80','1.00']:
  page.select_option('#export-jpg-quality',quality)
  with page.expect_download() as got:page.click('#export-visual-jpg-btn')
  target=tmp_path/f'quality-{quality}.jpg';got.value.save_as(target)
  with Image.open(target) as image:assert image.format=='JPEG';results.append((image.size,target.stat().st_size))
 assert results[0][0]==results[1][0] and results[1][1]>results[0][1]

def test_review122_sequential_views_tabs_and_mode_mirror(controls40_page):
 page,context,base=controls40_page;seed(context,base,'sequential','stack',[('apilar',{'value':7})]);page.goto(base+'/sequential/stack',wait_until='networkidle')
 page.click('#stack-view-linked');assert page.locator('#stack-view-linked').get_attribute('aria-pressed')=='true';assert page.locator('#visual-state').get_attribute('data-stack-visual-mode')=='linked'
 page.click('#stack-view-current');assert page.locator('#stack-view-current').get_attribute('aria-pressed')=='true';assert page.locator('#visual-state').get_attribute('data-stack-visual-mode')=='current'
 assert not page.locator('#seq-step-toggle').is_checked();page.click('#seq-step-mode');assert page.locator('#seq-step-toggle').is_checked()
 page.set_viewport_size({'width':390,'height':844});page.click('[data-seq-tab="code"]');assert not page.locator('#seq-visual-region').is_visible();page.click('[data-seq-tab="visual"]');assert page.locator('#seq-visual-region').is_visible()

def test_review122_prediction_hint_skip_and_optin(controls40_page):
 page,context,base=controls40_page;page.goto(base+'/sequential/stack',wait_until='networkidle');open_optional_panel(page,'Predecir');page.check('#seq-predictions-enabled');page.locator('#field-value').fill('7');page.click('#seq-step-mode');page.click('#seq-sim-execute')
 for _ in range(8):
  if page.locator('#seq-prediction-panel').is_visible():break
  page.click('#seq-sim-step')
 assert page.locator('#seq-prediction-panel').is_visible();before=page.locator('#seq-prediction-feedback').inner_text();page.click('#seq-prediction-hint');assert page.locator('#seq-prediction-feedback').inner_text()!=before
 page.click('#seq-prediction-skip');assert not page.locator('#seq-prediction-panel').is_visible()
 page.uncheck('#seq-predictions-enabled');page.click('#seq-sim-step');assert not page.locator('#seq-prediction-panel').is_visible()
def test_review122_counting_small_paged_controls(controls40_page):
 page,context,base=controls40_page
 response=context.request.post(base+'/api/ordenamiento/create-array',data={'values':[1000,0]});assert response.status==200
 response=context.request.post(base+'/api/ordenamiento/run',data={'algorithm_id':'counting_sort','mode':'step_by_step'});assert response.status==200
 assert response.json()['execution_trace']['schema']=='counting-paged-trace/v1'
 page.goto(base+'/sorting/visualizador',wait_until='networkidle')
 if not page.locator('#sorting-step-toggle').is_checked():page.click('#sorting-sim-step')
 page.locator('#sorting-counting-jump').fill('10');page.click('#sorting-counting-go')
 expect(page.locator('#sorting-sim-counter')).to_have_text(re.compile(r'Paso: 10/'))
 runs=[];page.on('request',lambda req:runs.append(req.url) if req.url.endswith('/api/ordenamiento/run') else None)
 page.click('#sorting-counting-replay');page.wait_for_function("parseInt(document.querySelector('#sorting-sim-counter').textContent.match(/Paso:\\s*(\\d+)/)[1],10)>10")
 page.click('#sorting-counting-pause');page.wait_for_timeout(100);stopped=page.locator('#sorting-sim-counter').inner_text();page.wait_for_timeout(300);assert page.locator('#sorting-sim-counter').inner_text()==stopped
 assert not runs

def test_review122_sorting_comments_use_real_source(controls40_page):
 page,context,base=controls40_page;page.goto(base+'/sorting/visualizador',wait_until='networkidle')
 visible="()=>[...document.querySelectorAll('#sorting-code .is-code-comment,#sorting-code .code-comment')].filter(e=>getComputedStyle(e).display!=='none'&&e.getClientRects().length).length"
 before=page.evaluate(visible);assert before>0
 page.check('#sorting-hide-comments');assert page.evaluate(visible)<before;page.uncheck('#sorting-hide-comments');assert page.evaluate(visible)==before

def test_review122_sequential_comments_use_real_source(controls40_page):
 page,context,base=controls40_page;page.goto(base+'/sequential/stack',wait_until='networkidle')
 visible="()=>[...document.querySelectorAll('#op-pseudocode .is-code-comment,#op-pseudocode .code-comment')].filter(e=>getComputedStyle(e).display!=='none'&&e.getClientRects().length).length"
 before=page.evaluate(visible);assert before>0
 page.check('#seq-hide-comments');assert page.evaluate(visible)<before;page.uncheck('#seq-hide-comments');assert page.evaluate(visible)==before

def test_review122_current_hierarchical_clear_button(controls40_page):
 page,context,base=controls40_page;seed(context,base,'hierarchical','abb',[('insertar',{'value':7})]);page.goto(base+'/hierarchical/abb',wait_until='networkidle')
 target=page.locator('#reset-button');assert target.count()==1
 from test_residual97_navigation import reveal_with_public_control
 reveal_with_public_control(page,target)
 page.on('dialog',lambda dialog:dialog.accept())
 with page.expect_response(lambda r:r.url.endswith('/hierarchical/abb/reset') and r.request.method=='POST') as reset:target.click()
 assert reset.value.status==200;query=context.request.post(base+'/hierarchical/abb/operate',data={'operation':'inorden','payload':{}});assert query.json()['result']==[]

def test_review122_current_sequential_clear_button(controls40_page):
 page,context,base=controls40_page;seed(context,base,'sequential','stack',[('apilar',{'value':7})]);page.goto(base+'/sequential/stack',wait_until='networkidle')
 target=page.locator('#reset-button');assert target.count()==1
 from test_residual97_navigation import reveal_with_public_control
 reveal_with_public_control(page,target)
 page.on('dialog',lambda dialog:dialog.accept())
 with page.expect_response(lambda r:r.url.endswith('/sequential/stack/reset') and r.request.method=='POST') as reset:target.click()
 assert reset.value.status==200;assert reset.value.json()['visual_state']['size']==0
def test_review122_legacy_sequential_purposes_preserved_by_keyboard(controls40_page):
 page,context,base=controls40_page;page.goto(base+'/sequential/stack',wait_until='networkidle');page.locator('#field-value').fill('7');page.click('#seq-step-mode')
 with page.expect_response(lambda r:r.url.endswith('/sequential/stack/operate') and r.request.method=='POST'):page.click('#seq-sim-execute')
 posts=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
 page.locator('#seq-sim-counter').click();page.keyboard.press('Alt+End');assert cursor(page,'#seq-sim-counter')>0
 page.keyboard.press('Alt+Home');assert cursor(page,'#seq-sim-counter')==0
 page.keyboard.press('Alt+r');page.wait_for_function("parseInt(document.querySelector('#seq-sim-counter').textContent.match(/Paso:\\s*(\\d+)/)[1],10)>0")
 page.keyboard.press('Alt+p');page.wait_for_timeout(100);paused=page.locator('#seq-sim-counter').inner_text();page.wait_for_timeout(300);assert page.locator('#seq-sim-counter').inner_text()==paused
 assert not posts
