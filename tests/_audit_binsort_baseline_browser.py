"""Actual Binsort UI generic-frame baseline and original caller downloads."""
from pathlib import Path
import json,sys
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from _audit_binsort_baseline_low import CASES
from _audit_sorting_main_native import audit_program
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-binsort-baseline-low'
PHASE=sys.argv[1];OUT=E/('browser-'+PHASE);OUT.mkdir(exist_ok=True);BASE='http://127.0.0.1:5051';rows=[]
def download(page,context,target,main):
 target.mkdir(exist_ok=True);page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
 for kind,name in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
  with page.expect_download() as got:page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]').click()
  got.value.save_as(str(target/name));actual=context.request.get(BASE+f'/help/source/sorting_array/{kind}')
  assert actual.status==200 and actual.body()==(target/name).read_bytes()
 assert (target/'main.c').read_text(encoding='utf-8')==main
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name in (['normal'] if PHASE=='before' else ['normal','negative_duplicates','outside_five']):
  values=CASES[name];context=browser.new_context();page=context.new_page();posts=[];errors=[]
  page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('let a;Object.defineProperty(window,"InterpreterRuntime",{configurable:true,get:()=>a,set:v=>{a={...v,createTracePlayer:o=>{const p=v.createTracePlayer(o);window.__auditPlayer=p;return p;}};}});')
  page.goto(BASE+'/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-manual-values').fill(','.join(map(str,values)))
  with page.expect_response('**/create-array'):page.click('#sorting-create-array')
  with page.expect_response('**/algorithm'):page.select_option('#sorting-algorithm','binsort')
  with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
  first=got.value.json();assert first['success'];frames=first['execution_trace']['steps'];count=len(posts)
  page.click('#sorting-sim-step');page.wait_for_timeout(100)
  restored=page.evaluate('window.__auditPlayer.hasTrace()');counter=page.locator('#sorting-sim-counter').text_content()
  row=dict(case=name,frames=len(frames),fast_to_step_trace_preserved=restored,counter_after_fast_step=counter,replay_extra_POSTs=len(posts)-count,errors=errors)
  captures=[]
  if PHASE=='after':
   assert restored and counter==f'Paso: 0/{len(frames)}'
   page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
   for direction,indices in [('forward',range(len(frames))),('reverse',range(len(frames)-1,-1,-1))]:
    for idx in indices:
     page.evaluate('index=>window.__auditPlayer.seek(index)',idx)
     shown=page.evaluate(r'''()=>({array:Array.from(document.querySelectorAll('.sorting-item-label'),e=>Number(e.textContent.replace(/^\[\d+\]\s*/,''))),stack:Array.from(document.querySelectorAll('#sorting-call-stack strong'),e=>e.textContent),active:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>Number(e.dataset.line)),console:document.querySelector('#sorting-printf-console').textContent})''')
     assert shown['array']==frames[idx]['state_after']['items']
     assert shown['active']==([] if frames[idx]['line_index'] is None else [frames[idx]['line_index']])
     captures.append(dict(direction=direction,cursor=idx,shown=shown))
   assert len(posts)==count
   page.click('#sorting-sim-next');page.wait_for_function('window.__auditPlayer.getCursor()===1');page.click('#sorting-sim-prev');assert page.evaluate('window.__auditPlayer.getCursor()')==0
   page.click('#sorting-sim-step')
   with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
   second=got.value.json();assert second['success'];count=len(posts);page.click('#sorting-sim-step')
   page.wait_for_function('(n)=>document.querySelector("#sorting-sim-counter").textContent==="Paso: 0/"+n',arg=len(second['execution_trace']['steps']))
   with page.expect_download() as got:page.click('#sorting-export-summary')
   got.value.save_as(str(OUT/(name+'-summary.json')));summary=json.loads((OUT/(name+'-summary.json')).read_text(encoding='utf-8'))
   assert summary['main_c']==second['main_c'] and summary['algorithm']=='binsort' and summary['total_steps']==len(frames)
   main=page.locator('.didactic-history-main').text_content();assert main==second['main_c'] and main.count('= ordenar_binsort(')==2
   page.reload(wait_until='networkidle');assert page.locator('.didactic-history-main').text_content()==main and len(posts)==count
   target=OUT/name;download(page,context,target,main);row['caller']=audit_program(target,[values,sorted(values),sorted(values)])
   assert row['caller']['successful_native_runs']==2 and row['caller']['allocations']==row['caller']['frees']==2 and row['caller']['live']==0
   assert context.request.get(BASE+'/api/ordenamiento/state').json()['history']==second['history']
   row.update(restorations=len(captures),helper_scope_visible=any('obtener_minimo_maximo' in c['shown']['stack'] for c in captures),console_has_printf=any('[printf]' in c['shown']['console'] for c in captures),five_sections=page.locator('.sorting-learning-stage').count(),replay_extra_POSTs=len(posts)-count)
   assert not errors and row['five_sections']==5 and row['replay_extra_POSTs']==0
  (OUT/(name+'.json')).write_text(json.dumps(dict(row=row,captures=captures,response=first),ensure_ascii=False,indent=2),encoding='utf-8');rows.append(row)
  page.screenshot(path=str(OUT/(name+'.png')),full_page=True);print(json.dumps(row),flush=True);context.close()
 if PHASE=='after':
  context=browser.new_context();page=context.new_page()
  context.request.post(BASE+'/api/ordenamiento/create-array',data={'values':[0,1000000]});context.request.post(BASE+'/api/ordenamiento/algorithm',data={'algorithm_id':'binsort'})
  before=context.request.get(BASE+'/api/ordenamiento/state').json();error=context.request.post(BASE+'/api/ordenamiento/run',data={'algorithm_id':'binsort','mode':'fast'})
  assert error.status==400 and error.json()['history']==before['history'];page.goto(BASE+'/sorting/visualizador',wait_until='networkidle')
  target=OUT/'range-error';download(page,context,target,error.json()['main_c']);failed=audit_program(target,[[0,1000000]])
  assert failed['successful_native_runs']==0 and failed['allocations']==failed['frees']==0
  (OUT/'range-error.json').write_text(json.dumps(dict(response=error.json(),caller=failed,ERROR_trace_present=bool(error.json().get('execution_trace'))),indent=2),encoding='utf-8');context.close()
 browser.close()
(OUT/'report.json').write_text(json.dumps(dict(rows=rows,scope='Actual generic Binsort frames, not proof of absent native instruction events.'),indent=2),encoding='utf-8')
