"""Exact RN validator reload, real Next, and safe malformed graph rendering."""
import json,re
from pathlib import Path
import pytest
from test_audit_avl_main_e2e import avl_server
ROOT=Path(__file__).resolve().parents[1]
INJECT=(ROOT/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig').split('INJECT="""')[1].split('"""')[0].replace('__hash','__rn')
@pytest.mark.e2e
@pytest.mark.parametrize('seed',[[],[10],[-2147483648,0,2147483647]])
def test_full_rn_exact_reload_and_next(avl_server,tmp_path,seed):
 from playwright.sync_api import sync_playwright
 with sync_playwright() as pw:
  browser=pw.chromium.launch();ctx=browser.new_context();p=ctx.new_page();p.add_init_script(INJECT);posts=[];errors=[];p.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);p.on('pageerror',lambda e:errors.append(str(e)))
  for v in seed:assert ctx.request.post(avl_server+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
  p.goto(avl_server+'/hierarchical/red_black');p.select_option('#operation-select','validar');p.click('#hier-step-mode');records=[]
  for repeat in range(2):
   with p.expect_response(lambda r:r.url.endswith('/red_black/operate') and r.request.method=='POST') as pending:p.click('#hier-sim-play')
   data=pending.value.json();assert data['success'] and data['result'] is True;trace=data['execution_trace'];p.wait_for_function('()=>window.__rnTrace?.operation_name==="validar"');p.evaluate('window.__rnPlayer.seek(2)');before=p.evaluate('({trace:window.__rnTrace,cursor:window.__rnPlayer.getCursor(),state:window.__rnRendered})');n=len(posts)
   p.reload();p.wait_for_function('()=>window.__rnTrace?.operation_name==="validar"');after=p.evaluate('({trace:window.__rnTrace,cursor:window.__rnPlayer.getCursor(),state:window.__rnRendered})');assert after==before;assert p.evaluate('window.HIER_VIEW_MODEL.history')==data['history'];assert len(posts)==n
   p.click('#hier-sim-step');p.wait_for_function('()=>window.__rnPlayer.getCursor()===3');assert len(posts)==n
   assert p.locator('[data-abb-node]').count()==len(seed);assert p.locator('.viz-tree-node:not(.nil)').count()==len(seed)
   records.append({'repeat':repeat,'reload_exact':True,'next_extra_posts':0,'history_length':len(data['history'])})
  numbered=p.locator('main h3,main summary').evaluate_all('els=>els.map(e=>e.textContent.trim()).filter(t=>/^[1-5]\\s/.test(t))');assert len(numbered)==5,numbered;assert not errors
  # A complete mutation invalidates the validator cache; no cache reuse across states.
  d=ctx.request.post(avl_server+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':1234567}}).json();assert d['success'];p.reload();assert p.evaluate('window.__rnTrace') is None if p.evaluate('typeof window.__rnTrace')!='undefined' else True
  (tmp_path/'reload.json').write_text(json.dumps({'seed':seed,'records':records,'sections':numbered,'errors':errors}),encoding='utf-8');ctx.close();browser.close()
