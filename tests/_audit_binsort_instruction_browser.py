"""Actual canonical Binsort UI instruction replay and bounded large-domain evidence."""
from pathlib import Path
import sys,json,time,hashlib
from playwright.sync_api import sync_playwright
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'tests'))
from _audit_sorting_main_native import audit_program
C=ROOT/'openspec/changes/audit-local-quality-and-unified-controls';E=C/'evidence/visible-sorting-binsort-instructions/browser';E.mkdir(exist_ok=True)
L=C/'evidence/visible-sorting-binsort-baseline-low/browser-after';BASE='http://127.0.0.1:5051'
rows=[]
INIT='let a;Object.defineProperty(window,"CountingRuntime",{configurable:true,get:()=>a,set:v=>{a={...v,createCompatiblePlayer:o=>{const p=v.createCompatiblePlayer(o);const load=p.loadTrace;p.loadTrace=t=>{window.__binTrace=t;return load(t);};window.__binPlayer=p;return p;}};}});'
def snapshot(page):
 return page.evaluate(r'''()=>({array:Array.from(document.querySelectorAll('.sorting-item-label'),e=>Number(e.textContent.replace(/^\[\d+\]\s*/,''))),stack:Array.from(document.querySelectorAll('#sorting-call-stack strong'),e=>e.textContent),active:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>Number(e.dataset.line)),console:document.querySelector('#sorting-printf-console').textContent,buckets:document.querySelectorAll('[data-count-index]').length,live:document.querySelector('[data-count-live]')?.dataset.countLive})''')
def download(page,context,target):
 target.mkdir(exist_ok=True);page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
 for kind,name in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
  with page.expect_download() as got:page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]').click()
  got.value.save_as(str(target/name));actual=context.request.get(BASE+f'/help/source/sorting_array/{kind}')
  assert actual.status==200 and actual.body()==(target/name).read_bytes()
 return target
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name,values in [('normal',[3,1,2]),('negative_duplicates',[-3,-5,-3,-4]),('outside_five',[5,4,3,2,1]),('wide_eighty',[int(i*999999/79) for i in range(80)]),('range-error',[0,1000000])]:
  context=browser.new_context();page=context.new_page();posts=[];errors=[];captures=[]
  page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script(INIT);page.goto(BASE+'/sorting/visualizador',wait_until='networkidle')
  page.locator('#sorting-manual-values').fill(','.join(map(str,values)))
  with page.expect_response('**/create-array'):page.click('#sorting-create-array')
  with page.expect_response('**/algorithm'):page.select_option('#sorting-algorithm','binsort')
  before=context.request.get(BASE+'/api/ordenamiento/state').json()
  start=time.perf_counter()
  with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
  r=got.value;data=r.json();trace=data['execution_trace'];total=trace.get('step_count',len(trace.get('steps',[])));assert r.status==(400 if name=='range-error' else 200)
  page.wait_for_function('(n)=>window.__binPlayer?.getTotalSteps()===n',arg=total)
  page.click('#sorting-sim-step');page.wait_for_function('(n)=>window.__binPlayer?.getTotalSteps()===n',arg=total)
  page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');count=len(posts)
  if name=='wide_eighty':
   assert trace['schema']=='counting-paged-trace/v1' and total==3000912
   compact=context.request.get(BASE+trace['export_url']).json()['compact_trace'];ends=compact['ends'];begins=[0]+ends[:-1]
   indices=sorted(set([0,1,2,3,total//2,total-3,total-2,total-1]+[j for begin,end,record in zip(begins,ends,compact['records']) if record['kind']=='zero_span' for j in [begin,begin+1,begin+2,end-3,end-2,end-1]]))
  else:indices=list(range(total))
  for direction,order in [('forward',indices),('reverse',list(reversed(indices)))]:
   for idx in order:
    assert page.evaluate('index=>window.__binPlayer.seek(index)',idx) is not False
    expected=page.evaluate('index=>window.__binPlayer.getStep(index)',idx);shown=snapshot(page)
    assert shown['array']==expected['state_after']['items']
    assert shown['active']==([] if expected['line_index'] is None else [expected['line_index']])
    assert shown['stack']==[x['function'] for x in expected['pedagogy']['call_stack']]
    assert '[printf]' not in shown['console'] and shown['buckets']<=64
    captures.append(dict(direction=direction,cursor=idx,token=expected['debug']['instruction_event']['token'],shown=shown))
  assert len(posts)==count and not errors
  if name=='wide_eighty':
   assert page.evaluate('window.CountingRuntime.cachePages(window.__binTrace)')<=4
   page.locator('#sorting-counting-jump').fill(str(total));page.locator('#sorting-counting-jump-go').click() if page.locator('#sorting-counting-jump-go').count() else page.evaluate('n=>window.__binPlayer.seek(n-1)',total)
   page.wait_for_function('(n)=>window.__binPlayer.getCursor()===n-1',arg=total)
  if name=='range-error':
   assert data['history']==before['history'] and data['main_c']==before['main_c']
   assert page.locator('#sorting-counting-outcome').is_visible() and 'ORDENAMIENTO_ERROR (0)' in page.locator('#sorting-counting-outcome').text_content()
   assert context.request.get(BASE+'/api/ordenamiento/state').json()==before
  elif name!='wide_eighty':
   page.click('#sorting-sim-step')
   with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
   data=got.value.json();assert data['success'];count=len(posts);page.click('#sorting-sim-step')
  with page.expect_download() as got:page.click('#sorting-export-summary')
  got.value.save_as(str(E/(name+'-summary.json')));summary=json.loads((E/(name+'-summary.json')).read_text(encoding='utf-8'))
  assert summary['main_c']==data['main_c'] and summary['algorithm']=='binsort' and summary['total_steps']==data['execution_trace'].get('step_count',len(data['execution_trace'].get('steps',[])))
  if name in ('wide_eighty','range-error'):assert summary['counting_trace']['operation_name']=='binsort'
  main=data['main_c'];page.reload(wait_until='networkidle');assert page.locator('.didactic-history-main').text_content()==main and len(posts)==count
  target=download(page,context,E/name)
  if name!='wide_eighty':
   for f in ['main.c','tad_ordenamiento.c','tad_ordenamiento.h']:assert (target/f).read_bytes()==(L/name/f).read_bytes()
   caller=dict(reused_exact_original_program=True,source=str(L/name),new_native_execution=False)
  else:caller=audit_program(target,[values,sorted(values)])
  assert page.locator('.sorting-learning-stage').count()==5 and not errors
  row=dict(case=name,logical_events=total,restorations=len(captures),range=1000000 if name=='wide_eighty' else None,run_and_replay_seconds=time.perf_counter()-start,POSTs_during_replay=0,JS_errors=errors,five_sections=5,helper_scope_visible=any('obtener_minimo_maximo' in x['shown']['stack'] for x in captures),max_bucket_DOM=max(x['shown']['buckets'] for x in captures),caller=caller)
  if name=='wide_eighty':row.update(stored_records=trace['manifest']['stored_records'],retained_bytes=trace['manifest']['retained_bytes'],initial_response_bytes=len(r.body()))
  (E/(name+'.json')).write_text(json.dumps(dict(row=row,captures=captures,trace_id=trace['trace_id']),ensure_ascii=False,indent=2),encoding='utf-8');rows.append(row)
  page.screenshot(path=str(E/(name+'.png')),full_page=True);print(json.dumps(row),flush=True);context.close()
 browser.close()
(E/'report.json').write_text(json.dumps(dict(rows=rows,limits='Small native cases replayed completely; large case samples zero-span boundaries, scalar/body Counting oracles reused. Not exhaustive paths or real allocator exhaustion.'),indent=2),encoding='utf-8')
