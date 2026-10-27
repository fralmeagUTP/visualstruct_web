"""Actual Chromium UI restoration against independently observed native events."""
from pathlib import Path
import sys,json,threading
sys.stdout.reconfigure(encoding="utf-8");sys.stderr.reconfigure(encoding="utf-8")
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from _audit_seleccion_instructions import CASES
from _audit_sorting_main_native import audit_program
OUT=Path(sys.argv[1]).resolve();NATIVE=Path(sys.argv[2]).resolve();OUT.mkdir(parents=True,exist_ok=True)
app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();rows=[]
CAPTURE='''() => ({array:Array.from(document.querySelectorAll('.sorting-item-label'),e=>Number(e.textContent.replace(/^\\[\\d+\\]\\s*/,''))),strategy:document.querySelector('#sorting-strategy-view').textContent,variables:Array.from(document.querySelectorAll('#sorting-variable-table tr'),r=>Array.from(r.querySelectorAll('td'),e=>e.textContent)),stack:Array.from(document.querySelectorAll('#sorting-call-stack strong'),e=>e.textContent),pointers:document.querySelector('#sorting-pointer-view').textContent,condition:document.querySelector('#sorting-condition-view').textContent,conditionClass:document.querySelector('#sorting-condition-view').className,loop:document.querySelector('#sorting-loop-view').textContent,active:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>Number(e.dataset.line)),console:document.querySelector('#sorting-printf-console').textContent,progress:window.__auditPlayer.getCursor()+1})'''
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  for name,values in CASES.items():
   context=browser.new_context();page=context.new_page();posts=[];errors=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   page.add_init_script('let auditRuntime;Object.defineProperty(window,"InterpreterRuntime",{configurable:true,get:()=>auditRuntime,set:v=>{auditRuntime={...v,createTracePlayer:o=>{const p=v.createTracePlayer(o);window.__auditPlayer=p;return p;}};}});');page.goto(f'http://127.0.0.1:{server.server_port}/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-manual-values').fill(','.join(map(str,values)))
   with page.expect_response(lambda r:r.url.endswith('/create-array')):page.click('#sorting-create-array')
   with page.expect_response(lambda r:r.url.endswith('/algorithm')):page.select_option('#sorting-algorithm','seleccion')
   with page.expect_response(lambda r:r.url.endswith('/run')) as resp:page.click('#sorting-sim-play')
   d=resp.value.json();assert d['success'];steps=d['execution_trace']['steps'];native=json.loads((NATIVE/(name+'.json')).read_text(encoding='utf-8'))['native'];assert len(native)==len(steps)
   page.wait_for_function('window.__auditPlayer && window.__auditPlayer.hasTrace() && window.__auditPlayer.isAtEnd()')
   count=len(posts);page.click('#sorting-sim-step');assert len(posts)==count
   page.locator('#didactic-mode-switch').check()
   page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
   assert page.locator('#sorting-variable-table').is_visible() and page.locator('#sorting-call-stack').is_visible() and page.locator('#sorting-pointer-view').is_visible()
   captures=[]
   for direction,indices in [('forward',range(len(steps))),('reverse',range(len(steps)-1,-1,-1))]:
    for idx in indices:
     page.evaluate('index=>window.__auditPlayer.seek(index)',idx)
     shown=page.evaluate(CAPTURE);step=steps[idx];frame=step['pedagogy'];event=native[idx]['event']
     assert shown['array']==native[idx]['array'],(name,direction,idx,shown)
     assert shown['active']==([] if step['line_index'] is None else [step['line_index']]),(name,direction,idx,shown['active'],step['line_index'])
     assert shown['stack']==[call['function'] for call in frame['call_stack']],(name,direction,idx)
     assert step['state_after']['trace_action'] in shown['strategy']
     candidate=step['state_after']['selection_context']['indice_menor']
     import re
     candidate_text=re.split(r'M.nimo provisional:',shown['strategy'])[-1].strip()
     assert candidate_text==(f'[{candidate}] = {native[idx]["array"][candidate]}' if candidate is not None else '\u2014'),(name,idx,candidate_text,candidate)

     if frame['loop']:assert frame['loop']['kind'] in shown['loop']
     if frame['variables']:
      assert len(shown['variables'])==len(frame['variables'])
      for cells,var in zip(shown['variables'],frame['variables']):
       assert cells[:3]==[var['name'],var['type'],str(var['value']) if var['initialized'] else 'sin inicializar'],(name,idx,cells,var)
     if native[idx]['condition'] is not None:
      assert ('is-true' if native[idx]['condition'] else 'is-false') in shown['conditionClass']
     for alias in ['a','b']:
      if event[alias] is not None:assert f'arreglo[{event[alias]}] = {native[idx]["array"][event[alias]]}' in shown['pointers']
     assert '[printf]' not in shown['console']
     if name=='reverse' and direction=='forward' and event['token']=='swap_assign_a':page.screenshot(path=str(OUT/'reverse-partial-write.png'),full_page=True)
     captures.append({'direction':direction,'cursor':idx,'shown':shown})
   # Product buttons exercise next/prev on the same trace in addition to runtime seek (the actual UI has no slider).
   page.click('#sorting-sim-next');page.wait_for_function('window.__auditPlayer.getCursor()===1');page.click('#sorting-sim-prev');assert page.evaluate(CAPTURE)['array']==native[0]['array']
   page.click('#sorting-sim-step');page.click('#sorting-sim-step');assert len(posts)==count;assert not errors
   page.screenshot(path=str(OUT/(name+'.png')),full_page=True)
   # Same saved caller survives reload; use the product's three real download links.
   main=page.locator('.didactic-history-main').text_content()
   assert main==d['main_c'] and main.count('printf("Run ')==1
   page.reload(wait_until='networkidle');page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
   assert page.locator('.didactic-history-main').text_content()==main and len(posts)==count
   target=OUT/name;target.mkdir()
   for kind,filename in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
    with page.expect_download() as got:page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]').click()
    got.value.save_as(str(target/filename))
    downloaded=context.request.get(f'http://127.0.0.1:{server.server_port}/help/source/sorting_array/{kind}')
    assert downloaded.status==200 and downloaded.body()==(target/filename).read_bytes()
   assert (target/'main.c').read_text(encoding='utf-8')==main
   caller=audit_program(target,[values,sorted(values)])
   assert page.locator('.sorting-learning-stage').count()==5
   row={'case':name,'instructions':len(steps),'forward_reverse_restorations':len(captures),'replay_extra_POSTs':len(posts)-count,'page_errors':errors,'fast_to_step_preserved':True,'technical_views_visible':True,'actual_main_elements':page.locator('.didactic-history-main').count(),'caller':caller,'reload_main_preserved':True,'five_stages':True};rows.append(row);(OUT/(name+'.json')).write_text(json.dumps({'row':row,'captures':captures,'response':d},ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(row),flush=True);context.close()
  # Empty array rejected through the actual UI with no successful run entry.
  context=browser.new_context();page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/sorting/visualizador',wait_until='networkidle')
  with page.expect_response(lambda r:r.url.endswith('/algorithm')):page.select_option('#sorting-algorithm','seleccion')
  with page.expect_response(lambda r:r.url.endswith('/run')) as resp:page.click('#sorting-sim-play')
  empty=resp.value.json();assert not empty['success'];assert all(e['operation']!='run' for e in empty['history']);(OUT/'empty.json').write_text(json.dumps(empty,ensure_ascii=False,indent=2),encoding='utf-8')
  target=OUT/'empty';target.mkdir();page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
  for kind,filename in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
   with page.expect_download() as got:page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]').click()
   got.value.save_as(str(target/filename))
  empty_caller=audit_program(target,[[]]);assert empty_caller['successful_native_runs']==0
  context.close();browser.close()
finally:server.shutdown();thread.join(timeout=5)
(OUT/'report.json').write_text(json.dumps({'rows':rows,'empty_UI_rejected':True,'empty_caller':empty_caller,'scope':'actual array/strategy, variables, stack, pointers, condition, C highlight; six finite entries, replay states not new cases'},ensure_ascii=False,indent=2),encoding='utf-8')
