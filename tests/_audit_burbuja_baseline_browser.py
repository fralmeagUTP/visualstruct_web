"""Actual UI baseline: coarse insertion frames, shift/key gaps, existing real caller."""
from pathlib import Path
import sys,json,threading,re
sys.stdout.reconfigure(encoding='utf-8');sys.stderr.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from _audit_burbuja_baseline import UI_CASES as CASES
from _audit_sorting_main_native import audit_program
OUT=Path(sys.argv[1]).resolve();NATIVE=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True)
app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();rows=[]
CAPTURE=r'''() => ({array:Array.from(document.querySelectorAll('.sorting-item-label'),e=>Number(e.textContent.replace(/^\[\d+\]\s*/,''))),strategy:document.querySelector('#sorting-strategy-view').textContent,variables:Array.from(document.querySelectorAll('#sorting-variable-table tr'),r=>Array.from(r.querySelectorAll('td'),e=>e.textContent)),stack:Array.from(document.querySelectorAll('#sorting-call-stack strong'),e=>e.textContent),condition:document.querySelector('#sorting-condition-view').textContent,active:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>Number(e.dataset.line)),console:document.querySelector('#sorting-printf-console').textContent,cursor:window.__auditPlayer.getCursor()})'''
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  for name,values in CASES.items():
   context=browser.new_context();page=context.new_page();posts=[];errors=[]
   page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script('let auditRuntime;Object.defineProperty(window,"InterpreterRuntime",{configurable:true,get:()=>auditRuntime,set:v=>{auditRuntime={...v,createTracePlayer:o=>{const p=v.createTracePlayer(o);window.__auditPlayer=p;return p;}};}});')
   page.goto(f'http://127.0.0.1:{server.server_port}/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-manual-values').fill(','.join(map(str,values)))
   with page.expect_response(lambda r:r.url.endswith('/create-array')):page.click('#sorting-create-array')
   with page.expect_response(lambda r:r.url.endswith('/algorithm')):page.select_option('#sorting-algorithm','burbuja')
   page.click('#sorting-sim-step')
   with page.expect_response(lambda r:r.url.endswith('/run')) as response:page.click('#sorting-sim-play')
   d=response.value.json();assert d['success'];steps=d['execution_trace']['steps'];baseline=json.loads((NATIVE/(name+'.json')).read_text(encoding='utf-8'));assert len(steps)==len(baseline['projection'])
   page.wait_for_function('window.__auditPlayer && window.__auditPlayer.hasTrace()')
   count=len(posts);page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');captures=[];shift_key_gaps=[];hole_gaps=[];printf_frames=[]
   for direction,indices in [('forward',range(len(steps))),('reverse',range(len(steps)-1,-1,-1))]:
    for index in indices:
     page.evaluate('i=>window.__auditPlayer.seek(i)',index);shown=page.evaluate(CAPTURE);step=steps[index];projection=baseline['projection'][index];native=baseline['native'][projection['native_index']]
     assert shown['array']==native['array']==step['state_after']['items'],(name,index,shown)
     assert shown['active']==([] if step['line_index'] is None else [step['line_index']])
     assert shown['stack']==[call['function'] for call in step['pedagogy']['call_stack']]
     if '[printf]' in shown['console']:printf_frames.append({'direction':direction,'index':index})
     if projection['token']=='swap_assign_a' and name=='reverse' and direction=='forward':
      assert shown['array'][native['event']['a']]==shown['array'][native['event']['b']]
      page.screenshot(path=str(OUT/'reverse-partial-swap-baseline.png'),full_page=True)
     captures.append({'direction':direction,'index':index,'native_projection':projection,'shown':shown})
   assert len(posts)==count and not errors
   bubble_options=page.locator('#sorting-algorithm option').evaluate_all('(options)=>options.filter(o=>o.value.includes("burbuja")).map(o=>({id:o.value,label:o.textContent}))');assert len(bubble_options)==1 and bubble_options[0]['id']=='burbuja'
   page.click('#sorting-sim-next');page.wait_for_function('window.__auditPlayer.getCursor()===1');page.click('#sorting-sim-prev');assert page.evaluate(CAPTURE)['array']==values
   main=page.locator('.didactic-history-main').text_content();assert main==d['main_c'] and main.count('printf("Run ')==1
   page.reload(wait_until='networkidle');page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');assert page.locator('.didactic-history-main').text_content()==main and len(posts)==count
   target=OUT/name;target.mkdir()
   for kind,filename in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
    with page.expect_download() as got:page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]').click()
    got.value.save_as(str(target/filename));r=context.request.get(f'http://127.0.0.1:{server.server_port}/help/source/sorting_array/{kind}');assert r.status==200 and r.body()==(target/filename).read_bytes()
   assert (target/'main.c').read_text(encoding='utf-8')==main
   caller=audit_program(target,[values,sorted(values)])
   row={'case':name,'coarse_steps':len(steps),'coarse_restorations':len(captures),'replay_extra_POSTs':len(posts)-count,'page_errors':errors,'main_preserved_after_reload':True,'five_stages':page.locator('.sorting-learning-stage').count()==5,'DOM_bubble_variants':bubble_options,'projected_moves_match_C':all(p['moves_native']==p['moves_runtime'] for p in baseline['projection']),'printf_frames':printf_frames,'caller':caller,'instruction_fidelity':False};rows.append(row);(OUT/(name+'.json')).write_text(json.dumps({'row':row,'captures':captures,'response':d},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps({'case':name,'coarse_steps':len(steps),'DOM_bubble_variants':bubble_options},ensure_ascii=False),flush=True);context.close()
  context=browser.new_context();page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/sorting/visualizador',wait_until='networkidle')
  with page.expect_response(lambda r:r.url.endswith('/algorithm')):page.select_option('#sorting-algorithm','burbuja')
  with page.expect_response(lambda r:r.url.endswith('/run')) as response:page.click('#sorting-sim-play')
  empty=response.value.json();assert not empty['success'] and all(e['operation']!='run' for e in empty['history']);(OUT/'empty.json').write_text(json.dumps(empty,ensure_ascii=False,indent=2),encoding='utf-8')
  page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');target=OUT/'empty';target.mkdir()
  for kind,filename in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
   with page.expect_download() as got:page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]').click()
   got.value.save_as(str(target/filename))
  empty_caller=audit_program(target,[[]]);assert empty_caller['successful_native_runs']==0;context.close();browser.close()
finally:server.shutdown();thread.join(timeout=5)
(OUT/'report.json').write_text(json.dumps({'rows':rows,'empty_UI_rejected':True,'empty_caller':empty_caller,'scope':'Three actual improved-bubble histories and current coarse frames only; baseline is not instruction signoff'},ensure_ascii=False,indent=2),encoding='utf-8')
