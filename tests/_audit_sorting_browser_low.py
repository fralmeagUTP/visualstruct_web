"""Actual sorting UI baseline; no actual main is assumed when absent."""
from pathlib import Path
import sys,json,threading
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();rows=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  for alg in ['burbuja','mergesort','radixsort']:
   context=browser.new_context();page=context.new_page();posts=[];errors=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_port}/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-manual-values').fill('3,1,2')
   with page.expect_response(lambda r:r.url.endswith('/create-array')):page.click('#sorting-create-array')
   with page.expect_response(lambda r:r.url.endswith('/algorithm')):page.select_option('#sorting-algorithm',alg)
   page.locator('#sorting-step-toggle').uncheck();responses=[]
   for _ in range(2):
    with page.expect_response(lambda r:r.url.endswith('/run')) as resp:page.click('#sorting-sim-play')
    d=resp.value.json();assert d['success'];responses.append(d)
   before=page.locator('#sorting-action-history').text_content();count=len(posts)
   page.reload(wait_until='networkidle');after=page.locator('#sorting-action-history').text_content();state=context.request.get(f'http://127.0.0.1:{server.server_port}/api/ordenamiento/state').json();assert len(posts)==count
   row={'algorithm':alg,'actual_runs':2,'before_history':before,'after_history':after,'before_history_run_entries':before.count('Ejecutar:'),'after_history_run_entries':after.count('Ejecutar:'),'state_array_after_reload':state['visual_state']['items'],'saved_runs':sum(e['operation']=='run' for e in state['history']),'main_elements':page.locator('.didactic-history-main').count(),'reload_extra_POSTs':len(posts)-count,'page_errors':errors,'first_trace_input':responses[0]['execution_trace']['steps'][0]['state_snapshot']['items'],'second_trace_input':responses[1]['execution_trace']['steps'][0]['state_snapshot']['items']};rows.append(row);(OUT/(alg+'.json')).write_text(json.dumps({'row':row,'responses':responses},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(row,ensure_ascii=False),flush=True);context.close()
  browser.close()
finally:server.shutdown();thread.join(timeout=5)
(OUT/'report.json').write_text(json.dumps({'rows':rows,'scope':'actual history/reload and current main presence; actual C17 download proof belongs main-low evidence'},ensure_ascii=False,indent=2),encoding='utf-8')
