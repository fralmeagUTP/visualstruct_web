from pathlib import Path
import json
from playwright.sync_api import sync_playwright
E=Path('openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-get-contains-baseline-low');B=E/'browser';B.mkdir(exist_ok=True)
with sync_playwright() as p:
 browser=p.chromium.launch(headless=True);page=browser.new_page();page.add_init_script("localStorage.setItem('didactic-mode','full')");errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);page.goto('http://127.0.0.1:5051/hash/hash_table');page.wait_for_selector('#hash-operation-select')
 def execute(op,values):
  page.select_option('#hash-operation-select',op)
  for k,v in values.items():page.fill('#hash-field-'+k,str(v))
  with page.expect_response(lambda r:'/operate' in r.url and r.request.method=='POST') as response:page.click('#hash-sim-play')
  return {'status':response.value.status,'data':response.value.json()}
 execute('create_table',{'capacity':3})
 for key in [-6,1,4,7]:execute('insert',{'key':key,'value':key*10})
 result=[]
 for op,key in [('get',-6),('contains',-6),('get',10),('get',4),('get',4)]:result.append(execute(op,{'key':key}))
 initial_posts=len(posts);page.click('#hash-sim-step');page.click('#hash-sim-next');page.click('#hash-sim-prev');page.click('#hash-sim-step');assert len(posts)==initial_posts;main=page.request.get('http://127.0.0.1:5051/help/source/hash_table/main');(B/'main.c').write_bytes(main.body());page.screenshot(path=str(B/'queries.png'),full_page=True);page.reload();page.wait_for_selector('#hash-operation-select');model=page.evaluate('window.HASH_VIEW_MODEL');report={'queries':result,'reload_last_operation':model.get('execution_trace',{}).get('operation_name'),'mutating_history_length':len(model['history']),'download_status':main.status,'download_get_calls':main.body().count(b'th_buscar('),'download_contains_calls':main.body().count(b'th_contiene('),'extra_navigation_POSTs':len(posts)-initial_posts,'sections':page.locator('.hash-stage').count(),'page_errors':errors,'caller_limit':'Caller currently documents mutating confirmed history only; queries omitted intentionally. Query reproduction coverage remains pending, not an ownership leak proof.'};(B/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');browser.close();print({k:v for k,v in report.items() if k!='queries'})
