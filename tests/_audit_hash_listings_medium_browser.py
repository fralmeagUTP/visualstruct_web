from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-listings-instructions-medium';B=E/'browser';B.mkdir(exist_ok=True)
q=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig');INJECT=q.split('INJECT="""')[1].split('"""')[0];SNAP=q.split('SNAP="""')[1].split('"""')[0];fixtures=json.loads((E/'report.json').read_text(encoding='utf-8'))
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True);reports=[]
 for case in ['mixed','extremes','sparse']:
  selected=[r for r in fixtures if r['case']==case];context=browser.new_context();page=context.new_page();page.add_init_script(INJECT);errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);page.goto('http://127.0.0.1:5051/hash/hash_table');page.wait_for_selector('#hash-operation-select')
  page.request.post('http://127.0.0.1:5051/hash/hash_table/operate',data={'operation':'create_table','payload':{'capacity':selected[0]['capacity']}})
  for k,v in selected[0]['pairs']:page.request.post('http://127.0.0.1:5051/hash/hash_table/operate',data={'operation':'insert','payload':{'key':k,'value':v}})
  page.reload();page.wait_for_selector('#hash-operation-select');forward=back=0
  for item in selected+selected:
   page.select_option('#hash-operation-select',item['operation'])
   with page.expect_response(lambda r:'/hash/hash_table/operate' in r.url and r.request.method=='POST') as response:page.click('#hash-sim-play')
   d=response.value.json();assert response.value.status==200 and d['success'] and d['result']==item['expected_projection'];trace=d['execution_trace'];n=len(trace['steps']);assert len(d['history'])==1+len(item['pairs']);post_count=len(posts);page.click('#hash-sim-step');snapshots=[]
   for i,f in enumerate(trace['steps']):
    page.evaluate('(i)=>window.__hashPlayer.seek(i)',i);snap=page.evaluate(SNAP);assert snap['state']==f['state_after'];assert snap['cursor']==i
    if f['line_index']>=0:assert snap['active']==[f['line_index']]
    snapshots.append(snap);forward+=1
   for i in range(n-2,-1,-1):page.click('#hash-sim-prev');assert page.evaluate(SNAP)==snapshots[i];back+=1
   page.click('#hash-sim-step');page.click('#hash-sim-step');page.click('#hash-sim-next');assert page.evaluate(SNAP)==snapshots[0];assert len(posts)==post_count;page.evaluate('window.__hashPlayer.seek(window.__hashPlayer.getTotalSteps()-1)');page.click('#hash-sim-step')
  last=page.evaluate('window.__hashTrace');before=len(posts);directory=B/case;directory.mkdir(exist_ok=True);response=page.request.get('http://127.0.0.1:5051/help/source/hash_table/main');assert response.status==200;(directory/'main.c').write_bytes(response.body());page.screenshot(path=str(directory/'final.png'),full_page=True);page.reload();page.wait_for_selector('#hash-operation-select');assert page.evaluate('window.__hashTrace')==last;assert len(posts)==before;assert not errors;assert response.body().count(b'th_formatear(')==6
  reports.append({'case':case,'operations':6,'forward_frames':forward,'backward_restorations':back,'extra_navigation_POSTs':0,'page_errors':errors,'sections':page.locator('.hash-stage').count(),'reload_trace_equal':True,'actual_main_formatter_calls':response.body().count(b'th_formatear('),'limit':'Finite UI replay; C observer verifies formatter writes separately'});context.close()
 browser.close();(B/'report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8');print(json.dumps(reports))
