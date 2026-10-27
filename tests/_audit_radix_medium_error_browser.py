from pathlib import Path
import json,sys,threading
ROOT=Path.cwd();sys.path.insert(0,str(ROOT))
from app import create_app
from app.domain.sorting.radix_instructions import SimulatedRadixAllocationFailure
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-instructions/browser-errors';E.mkdir(exist_ok=True)
app=create_app();app.testing=True;server=make_server('127.0.0.1',0,app,threaded=True);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base='http://127.0.0.1:'+str(server.server_port);rows=[]
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch(headless=True)
  for attempt in [1,4]:
   app.config['RADIX_QA_ALLOCATOR']=None;context=browser.new_context();page=context.new_page();posts=[];errors=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script('let a;Object.defineProperty(window,"CountingRuntime",{configurable:true,get:()=>a,set:v=>{a={...v,createCompatiblePlayer:o=>{const p=v.createCompatiblePlayer(o);window.__radixPlayer=p;return p;}};}});')
   page.goto(base+'/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-manual-values').fill('-5,2')
   with page.expect_response('**/create-array'):page.click('#sorting-create-array')
   with page.expect_response('**/algorithm'):page.select_option('#sorting-algorithm','radixsort')
   with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
   accepted=got.value.json();assert accepted['success'];page.wait_for_function('window.__radixPlayer.hasTrace()')
   def allocator(name,capacity,index):
    if index==attempt:raise SimulatedRadixAllocationFailure('isolated UI QA; not real allocator exhaustion')
   app.config['RADIX_QA_ALLOCATOR']=allocator
   with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
   failure=got.value.json();assert not failure['success'];t=failure['execution_trace'];frames=t['steps'];count=len(posts);page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');captures=[]
   assert failure['history']==accepted['history'] and failure['main_c']==accepted['main_c'] and failure['visual_state']['items']==accepted['visual_state']['items']
   for direction,indices in [('forward',range(len(frames))),('reverse',range(len(frames)-1,-1,-1))]:
    for i in indices:
     page.evaluate('i=>window.__radixPlayer.seek(i)',i);shown=page.evaluate(r'''()=>({active:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>Number(e.dataset.line)),badge:document.querySelector('#sorting-counting-outcome').textContent,simulated:document.querySelector('#sorting-counting-outcome').dataset.simulated,main:document.querySelector('.didactic-history-main').textContent,array:Array.from(document.querySelectorAll('.sorting-item-label'),e=>Number(e.textContent.replace(/^\[\d+\]\s*/,'')))})''')
     assert shown['active']==([] if frames[i]['line_index'] is None else [frames[i]['line_index']]) and shown['simulated']=='true' and 'simulado'in shown['badge'] and shown['main']==accepted['main_c'] and shown['array']==frames[i]['state_after']['items'];captures.append(dict(cursor=i,direction=direction,shown=shown))
   assert len(posts)==count and not errors;page.reload(wait_until='networkidle');assert page.evaluate('window.__radixPlayer.hasTrace()') and len(posts)==count
   page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
   with page.expect_download() as got:page.click('#sorting-export-summary')
   path=E/('fault-'+str(attempt)+'-summary.json');got.value.save_as(str(path));summary=json.loads(path.read_text(encoding='utf-8'));assert summary['success'] is False and summary['main_c']==accepted['main_c'] and summary['accepted_state']['items']==accepted['visual_state']['items']
   page.screenshot(path=str(E/('fault-'+str(attempt)+'.png')),full_page=True)
   (E/('fault-'+str(attempt)+'-frames.json')).write_text(json.dumps(captures,ensure_ascii=False,indent=2),encoding='utf-8');rows.append(dict(attempt=attempt,simulated=True,real_C_allocator_exhaustion=False,frames=len(frames),restorations=len(captures),navigation_POSTs=0,accepted_history_main_preserved=True,reload_saved=True,export_accepted_attempt_separate=True,javascript_errors=errors));print('fault',attempt,len(captures),flush=True);context.close()
  browser.close()
finally:server.shutdown();server.server_close();thread.join(timeout=2)
(E/'report.json').write_text(json.dumps(dict(cases=rows,server='isolated TESTING app on ephemeral loopback; stopped after gate; preview5051 unchanged'),indent=2),encoding='utf-8')
