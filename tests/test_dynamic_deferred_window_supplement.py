"""Single sparse Counting window creator/gesture witness, not algorithm campaign."""
import pytest
import json
from pathlib import Path
from test_residual58_focal_cases import residual58_app
from test_controls40_real_flows import controls40_page

@pytest.mark.e2e
def test_sparse_window_index_and_follow_preserve_cached_cursor(controls40_page,tmp_path):
 page,context,base=controls40_page
 assert context.request.post(base+'/api/ordenamiento/create-array',data={'values':[700,0]}).status==200
 response=context.request.post(base+'/api/ordenamiento/run',data={'algorithm_id':'counting_sort','mode':'step_by_step'});assert response.status==200;assert response.json()['execution_trace']['schema']=='counting-paged-trace/v1'
 page.goto(base+'/sorting/visualizador',wait_until='networkidle')
 if not page.locator('#sorting-step-toggle').is_checked():page.click('#sorting-sim-step')
 generated=False;chosen=None
 for cursor in [20,30,40,50]:
  page.locator('#sorting-counting-jump').fill(str(cursor));page.click('#sorting-counting-go')
  if page.locator('[data-count-window-index]').count():generated=True;chosen=cursor;break
 assert generated,'No sparsewindow generated in selected initialized-count frames'
 before=page.locator('#sorting-sim-counter').inner_text();requests=[];page.on('request',lambda r:requests.append(r.url) if r.url.endswith('/api/ordenamiento/run') else None)
 target=page.locator('[data-count-window-index]');target.fill('10');target.press('Tab')
 assert page.locator('[data-count-window-index]').input_value()=='10'
 assert page.locator('[data-count-index="10"]').count()==1 and page.locator('#sorting-sim-counter').inner_text()==before
 page.click('[data-count-window-follow]');assert page.locator('#sorting-sim-counter').inner_text()==before
 assert page.locator('[data-count-window-index]').input_value()!='10' and not requests
 (tmp_path/'counting-window-proof.json').write_text(json.dumps({'input':[700,0],'creator':'sorting.js STRING_MARKUP data-count-window-index/follow','chosen_initialized_frame':chosen,'manual_start':10,'manual_window_cells_present':True,'follow_active_restores_auto_window':True,'cursor_unchanged':True,'extra_runs':0,'limit':'One required sparsewindow UIflow;notnominalsortingconformance,notmaxrangeorbenchmark.'},indent=2),encoding='utf-8')


@pytest.mark.e2e
def test_hash_native_disclosure_creator_keyboard_without_operation(controls40_page,tmp_path):
 page,context,base=controls40_page;page.goto(base+'/hash/hash_table',wait_until='networkidle');posts=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None)
 summaries=page.locator('details > summary');records=[]
 for i in range(summaries.count()):
  summary=summaries.nth(i)
  if not summary.is_visible():continue
  parent=summary.locator('..');before=parent.get_attribute('open') is not None;summary.focus();summary.press('Space');after=parent.get_attribute('open') is not None
  assert after!=before;assert summary.evaluate('(n)=>n===document.activeElement');summary.press('Space');assert(parent.get_attribute('open') is not None)==before
  records.append({'label':summary.inner_text(),'Space_toggle_and_restore':True,'focus_preserved':True})
 assert records and not posts
 (tmp_path/'hash-native-summary-proof.json').write_text(json.dumps({'records':records,'extra_POSTs':0,'limits':'Visible native summary instances atinitialHash;standard disclosure notmemoryinstructioncoverage.'},ensure_ascii=False,indent=2),encoding='utf-8')
