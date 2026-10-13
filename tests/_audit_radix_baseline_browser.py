from pathlib import Path
import json,sys
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'tests'))
from _audit_radix_baseline_low import CASES
from playwright.sync_api import sync_playwright
from _audit_sorting_main_native import audit_program
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-baseline-low/browser';E.mkdir(exist_ok=True)
BASE='http://127.0.0.1:5051';rows=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name in ['normal','negative_duplicates','int32_extremes']:
  values=CASES[name];context=browser.new_context();page=context.new_page();posts=[];errors=[]
  page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('let a;Object.defineProperty(window,"InterpreterRuntime",{configurable:true,get:()=>a,set:v=>{a={...v,createTracePlayer:o=>{const p=v.createTracePlayer(o);window.__radixPlayer=p;return p;}};}});')
  page.goto(BASE+'/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-manual-values').fill(','.join(map(str,values)))
  with page.expect_response('**/create-array'):page.click('#sorting-create-array')
  with page.expect_response('**/algorithm'):page.select_option('#sorting-algorithm','radixsort')
  with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
  first=got.value.json();assert first['success'];total=len(first['execution_trace']['steps']);count=len(posts)
  page.click('#sorting-sim-step');fast_restored=page.evaluate('window.__radixPlayer.hasTrace()');fast_counter=page.locator('#sorting-sim-counter').text_content();assert len(posts)==count
  with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
  second=got.value.json();assert second['success'];frames=second['execution_trace']['steps'];count=len(posts);page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');captures=[]
  for direction,indices in [('forward',range(len(frames))),('reverse',range(len(frames)-1,-1,-1))]:
   for i in indices:
    page.evaluate('i=>window.__radixPlayer.seek(i)',i)
    shown=page.evaluate(r'''()=>({array:Array.from(document.querySelectorAll('.sorting-item-label'),e=>Number(e.textContent.replace(/^\[\d+\]\s*/,''))),stack:Array.from(document.querySelectorAll('#sorting-call-stack strong'),e=>e.textContent),active:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>Number(e.dataset.line)),console:document.querySelector('#sorting-printf-console').textContent})''')
    assert shown['array']==frames[i]['state_after']['items'] and shown['active']==([] if frames[i]['line_index'] is None else [frames[i]['line_index']])
    captures.append(dict(cursor=i,direction=direction,shown=shown))
  assert len(posts)==count and not errors
  with page.expect_download() as got:page.click('#sorting-export-summary')
  got.value.save_as(str(E/(name+'-summary.json')));summary=json.loads((E/(name+'-summary.json')).read_text(encoding='utf-8'));assert summary['main_c']==second['main_c'] and summary['algorithm']=='radixsort'
  main=second['main_c'];assert page.locator('.didactic-history-main').text_content()==main and main.count('= ordenar_radixsort(')==2
  page.reload(wait_until='networkidle');assert page.locator('.didactic-history-main').text_content()==main and len(posts)==count
  reloaded=page.evaluate('window.__radixPlayer.hasTrace()');target=E/name;target.mkdir(exist_ok=True);page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
  for kind,f in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
   with page.expect_download() as got:page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]').click()
   got.value.save_as(str(target/f));assert context.request.get(BASE+f'/help/source/sorting_array/{kind}').body()==(target/f).read_bytes()
  caller=audit_program(target,[values,sorted(values),sorted(values)]);assert caller['successful_native_runs']==2
  row=dict(case=name,original_fast_trace_frames=total,fast_to_step_trace_restored=fast_restored,fast_counter=fast_counter,fast_step_extra_POSTs=0,restorations=len(captures),replay_extra_POSTs=0,helper_scope_visible=any('counting_por_digito'in x['shown']['stack'] for x in captures),reload_trace_restored=reloaded,history_main_preserved=True,five_sections=page.locator('.sorting-learning-stage').count(),UI_fictional_printf=any('[printf]'in x['shown']['console'] for x in captures),JS_errors=errors,caller=caller)
  (E/(name+'.json')).write_text(json.dumps(dict(row=row,captures=captures),ensure_ascii=False,indent=2),encoding='utf-8');rows.append(row);page.screenshot(path=str(E/(name+'.png')),full_page=True);print(json.dumps(row),flush=True);context.close()
 browser.close()
(E/'report.json').write_text(json.dumps(dict(rows=rows,scope='Actual original Radix aggregate frames/callers; this is not native instruction fidelity. Fast-step and reload trace gaps preserved.'),indent=2),encoding='utf-8')
