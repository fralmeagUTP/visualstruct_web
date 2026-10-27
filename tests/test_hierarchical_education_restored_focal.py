"""Authorized educational functions in four structures, five stages, manual playback."""
import json,re
from pathlib import Path
import pytest
from test_residual58_focal_cases import residual58_app
from test_controls40_real_flows import controls40_page
R=Path(__file__).resolve().parents[1]
FAMILIES=['abb','avl','red_black','binary_heap']

def open_panel(page,label):
 if page.locator('#hier-understand-toggle').get_attribute('aria-expanded')=='false':page.click('#hier-understand-toggle')
 summary=page.locator('details.hier-learning-disclosure > summary').filter(has_text=re.compile('^'+label+'$'));summary.focus();summary.press('Space')
 assert summary.locator('..').get_attribute('open') is not None
 assert page.evaluate('document.activeElement.tagName')=='SUMMARY'

@pytest.mark.e2e
@pytest.mark.parametrize('family',FAMILIES)
def test_restored_education_real_functions_and_manual_navigation(controls40_page,tmp_path,family):
 page,context,base=controls40_page
 script=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig').split('INJECT="""')[1].split('"""')[0].replace("localStorage.setItem('didactic-mode','full');",'').replace('__hash','__edu');page.add_init_script(script)
 errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
 page.goto(base+'/hierarchical/'+family);assert page.locator('#hier-learning-level').is_visible() and page.locator('#hier-guided-example').is_visible()
 assert page.locator('#hier-learning-level').locator('xpath=ancestor::section[1]').get_attribute('id')=='hier-code-region'
 assert page.locator('#hier-guided-example').locator('xpath=ancestor::section[1]').get_attribute('aria-labelledby')=='hier-prepare-title'
 headings=page.locator('h3').evaluate_all(r"els=>els.map(e=>e.textContent.replace(/\s+/g,' ').trim()).filter(t=>/^[1-5] /.test(t))")
 assert headings==['1 Preparar y controlar ejecución','2 Visualizar y ejecutar','3 Relacionar con código','4 Comprender','5 Resultados de ejecución']
 assert page.locator('input[type=range]').count()==0 and page.locator('#hier-sim-repeat').count()==0
 examples=page.evaluate('window.HIER_VIEW_MODEL.guided_examples');example=next(x for x in examples if x['id']=='single') if family=='binary_heap' else min(examples,key=lambda x:len(x.get('seed',[])));page.select_option('#hier-guided-example',example['id']);assert page.locator('#hier-example-lesson').inner_text()==example['lesson'];count=len(posts);page.click('#hier-load-example');page.wait_for_function("()=>document.querySelector('#message-box').textContent.startsWith('Ejemplo preparado:')")
 assert len(posts)-count==1+len(example.get('seed',[]));assert page.locator('#operation-select').input_value()==example['operation']
 for name,value in example.get('payload',{}).items():assert page.locator('#h-field-'+name).input_value()==str(value)
 if not page.locator('#hier-step-toggle').is_checked():page.click('#hier-step-mode')
 with page.expect_response(lambda r:r.url.endswith('/hierarchical/'+family+'/operate') and r.request.method=='POST') as response:page.click('#hier-sim-play')
 data=response.value.json();assert data['success'];page.wait_for_function('()=>window.__eduTrace?.steps?.length>0');trace=data['execution_trace'];count=len(posts)
 page.click('#hier-sim-step');assert page.evaluate('window.__eduPlayer.getCursor()')==0
 for level in ['basic','advanced','intermediate']:
  page.select_option('#hier-learning-level',level);assert trace['steps'][0]['pedagogy']['narration'][level] in page.locator('#hier-pedagogy-summary').inner_text()
 open_panel(page,'Predecir');assert page.locator('#hier-prediction').is_visible();page.check('#hier-practice-mode');assert 'hier-practice-hidden' in page.locator('#visual-state').get_attribute('class')
 page.select_option('#hier-prediction','none');page.click('#hier-check-prediction');assert page.locator('#hier-prediction-feedback').inner_text().startswith('Correcto:');assert '1 aciertos de 1 intentos' in page.locator('#hier-progress-summary').inner_text();assert 'hier-practice-hidden' not in page.locator('#visual-state').get_attribute('class')
 for expected in ['Pista 1:','Pista 2:','Pista 3:']:
  page.click('#hier-hint');assert page.locator('#hier-prediction-feedback').inner_text().startswith(expected)
 page.click('#hier-skip-prediction');assert 'sin responder' in page.locator('#hier-prediction-feedback').inner_text();assert '1 aciertos de 1 intentos' in page.locator('#hier-progress-summary').inner_text();page.click('#hier-reset-progress');assert '0 aciertos de 0 intentos' in page.locator('#hier-progress-summary').inner_text();page.uncheck('#hier-practice-mode')
 open_panel(page,'Comparar');before=page.evaluate('window.HIER_VIEW_MODEL.visual_state');kind='abb-heap' if family=='binary_heap' else 'avl-red-black' if family in ['avl','red_black'] else 'abb-avl';page.select_option('#hier-compare-kind',kind);page.fill('#hier-compare-values','9, 3, 7')
 with page.expect_response(lambda r:'/hierarchical/compare' in r.url and r.request.method=='POST') as response:page.click('#hier-compare-run')
 comparison=response.value.json();assert comparison['success'] and comparison['input']==[9,3,7];page.wait_for_function("()=>document.querySelector('#hier-compare-position-label').textContent.startsWith('Paso 1')");assert page.locator('#hier-compare-grid .hier-compare-card').count()==2;initial=page.locator('#hier-compare-grid').inner_text();n=len(posts);page.click('#hier-compare-next');assert page.locator('#hier-compare-grid').inner_text()!=initial;page.click('#hier-compare-prev');assert page.locator('#hier-compare-grid').inner_text()==initial;assert len(posts)==n and page.evaluate('window.HIER_VIEW_MODEL.visual_state')==before
 assert page.locator('#hier-compare-progress').get_attribute('type')=='hidden';assert page.locator('input[type=range]').count()==0
 # Education did not dispatch the main operation or change its cached cursor/state.
 assert page.evaluate('window.__eduPlayer.getCursor()')==0;page.click('#hier-sim-step');second=page.evaluate('window.__eduRendered');assert page.evaluate('window.__eduPlayer.getCursor()')==1;page.click('#hier-sim-prev');assert page.evaluate('window.__eduPlayer.getCursor()')==0;assert page.evaluate('window.__eduRendered')==trace['steps'][0]['state_after'];page.click('#hier-sim-step');assert page.evaluate('window.__eduRendered')==second;assert len(posts)==count+1 and not errors
 (tmp_path/'education-restored-proof.json').write_text(json.dumps({'family':family,'example':example['id'],'example_public_calls':1+len(example.get('seed',[])),'levels':['basic','advanced','intermediate'],'prediction':'1correct/1attempt;hint1-3;skip noattempt;reset0','practice':'conceal/reveal','comparison_kind':kind,'comparison_input':[9,3,7],'comparison_manual_cached':True,'main_next_prev_cached':True,'five_stages':headings,'native_disclosures_keyboard_space':True,'sliders':0,'JS_errors':errors},indent=2),encoding='utf-8')
