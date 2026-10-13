from pathlib import Path
import json
from playwright.sync_api import sync_playwright
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-stats-baseline-low';B=E/'browser';B.mkdir(exist_ok=True)
s=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig');INJECT=s.split('INJECT="""')[1].split('"""')[0];SNAP=s.split('SNAP="""')[1].split('"""')[0];fixtures=json.loads((E/'report.json').read_text(encoding='utf-8'));report=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for case in ['empty','collision','sparse','destroyed']:
  row=next(x for x in fixtures if x['case']==case);c=browser.new_context();p=c.new_page();p.add_init_script(INJECT);errors=[];posts=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);p.goto('http://127.0.0.1:5051/hash/hash_table')
  p.request.post('http://127.0.0.1:5051/hash/hash_table/operate',data={'operation':'create_table','payload':{'capacity':row['created_capacity']}})
  for k,v in row['pairs']:p.request.post('http://127.0.0.1:5051/hash/hash_table/operate',data={'operation':'insert','payload':{'key':k,'value':v}})
  if case=='destroyed':p.request.post('http://127.0.0.1:5051/hash/hash_table/operate',data={'operation':'destroy_table','payload':{}})
  p.reload();forward=back=0
  for _ in range(2):
   p.select_option('#hash-operation-select','stats')
   with p.expect_response(lambda r:'/hash/hash_table/operate' in r.url and r.request.method=='POST') as response:p.click('#hash-sim-play')
   d=response.value.json();assert d['result']==row['data']['result'];trace=d['execution_trace'];count=len(posts);p.click('#hash-sim-step');shots=[]
   for i,f in enumerate(trace['steps']):
    p.evaluate('(i)=>window.__hashPlayer.seek(i)',i);shot=p.evaluate(SNAP);assert shot['state']==f['state_after'] and shot['cursor']==i
    if f['line_index']>=0:assert shot['active']==[f['line_index']]
    shots.append(shot);forward+=1
   for i in range(len(shots)-2,-1,-1):p.click('#hash-sim-prev');assert p.evaluate(SNAP)==shots[i];back+=1
   p.click('#hash-sim-step');p.click('#hash-sim-step');p.click('#hash-sim-next');assert p.evaluate(SNAP)==shots[0] and len(posts)==count;p.click('#hash-sim-step')
  last=p.evaluate('window.__hashTrace');directory=B/case;directory.mkdir(exist_ok=True);main=p.request.get('http://127.0.0.1:5051/help/source/hash_table/main').body();assert main==(E/'callers'/(case+'.c')).read_bytes();(directory/'main.c').write_bytes(main);p.screenshot(path=str(directory/'final.png'),full_page=True);count=len(posts);p.reload();assert p.evaluate('window.__hashTrace')==last and len(posts)==count and not errors;report.append({'case':case,'queries':2,'frames':forward,'back':back,'sections':p.locator('.hash-stage').count(),'JS_errors':errors,'extra_POSTs':0,'reload_trace_equal':True,'caller_stats_calls':main.count(b'th_estadisticas('),'limit':'Retained generic stub replay, not C instruction fidelity'});c.close()
 browser.close()
(B/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps(report))
