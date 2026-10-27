from pathlib import Path
import json,sys
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'tests'))
from _audit_radix_baseline_low import CASES
from playwright.sync_api import sync_playwright
from _audit_sorting_main_native import audit_program
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-instructions/browser';E.mkdir(exist_ok=True)
L=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-radix-baseline-low/browser'
BASE='http://127.0.0.1:5051';rows=json.loads((E/'report.json').read_text(encoding='utf-8'))['cases'] if len(sys.argv)>1 and (E/'report.json').exists() else []
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name in (sys.argv[1:] or ['normal','negative_duplicates','int32_extremes','maximum']):
  values=CASES[name] if name!='maximum' else [-2147483648,2147483647]*40
  context=browser.new_context();page=context.new_page();posts=[];errors=[]
  page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  page.add_init_script('let a;Object.defineProperty(window,"CountingRuntime",{configurable:true,get:()=>a,set:v=>{a={...v,createCompatiblePlayer:o=>{const p=v.createCompatiblePlayer(o);window.__radixPlayer=p;return p;}};}});')
  page.goto(BASE+'/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-manual-values').fill(','.join(map(str,values)))
  with page.expect_response('**/create-array'):page.click('#sorting-create-array')
  with page.expect_response('**/algorithm'):page.select_option('#sorting-algorithm','radixsort')
  with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
  first=got.value.json();assert first['success'];count=len(posts);page.click('#sorting-sim-step');assert page.evaluate('window.__radixPlayer.hasTrace()') and len(posts)==count
  if name!='maximum':
   with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
   d=got.value.json()
  else:d=first
  trace=d['execution_trace'];total=trace.get('step_count',len(trace.get('steps',[])));count=len(posts)
  page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');captures=[]
  indices=list(range(total)) if name!='maximum' else [0,1,2,10,127,128,129,2047,2048,5704,11406,11407]
  for direction,targets in [('forward',indices),('reverse',list(reversed(indices)))]:
   for i in targets:
    page.evaluate('i=>window.__radixPlayer.seek(i)',i)
    frame=trace['steps'][i] if 'steps'in trace else context.request.get(BASE+trace['page_url']+'?start='+str(i)+'&limit=1').json()['steps'][0]
    shown=page.evaluate(r'''()=>({array:Array.from(document.querySelectorAll('.sorting-item-label'),e=>Number(e.textContent.replace(/^\[\d+\]\s*/,''))),stack:Array.from(document.querySelectorAll('#sorting-call-stack strong'),e=>e.textContent),active:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>Number(e.dataset.line)),console:document.querySelector('#sorting-printf-console').textContent,buffers:Array.from(document.querySelectorAll('[data-radix-buffer]'),e=>({name:e.dataset.radixBuffer,live:e.dataset.live,cells:Array.from(e.querySelectorAll('[data-radix-index]'),v=>({index:Number(v.dataset.radixIndex),initialized:v.dataset.initialized,text:v.textContent}))})),nodes:document.querySelectorAll('*').length})''')
    assert shown['array']==frame['state_after']['items'] and shown['active']==([] if frame['line_index'] is None else [frame['line_index']]),(name,i,shown['active'],frame['line_index'])
    for b in shown['buffers']:
     expected=frame['state_after']['radix_context']['buffers'][b['name']]
     assert b['live']==str(expected['live']).lower() and len(b['cells'])==(expected['capacity'] if expected['live'] else 0)
     for cell in b['cells']:assert cell['initialized']==str(expected['cells'][cell['index']] is not None).lower()
    captures.append(dict(cursor=i,direction=direction,shown=shown))
  assert len(posts)==count and not errors
  with page.expect_download() as got:page.click('#sorting-export-summary')
  got.value.save_as(str(E/(name+'-summary.json')));summary=json.loads((E/(name+'-summary.json')).read_text(encoding='utf-8'));assert summary['main_c']==d['main_c'] and summary['algorithm']=='radixsort'
  main=d['main_c'];assert page.locator('.didactic-history-main').text_content()==main
  page.reload(wait_until='networkidle');assert page.evaluate('window.__radixPlayer.hasTrace()') and len(posts)==count and page.locator('.didactic-history-main').text_content()==main
  target=E/name;target.mkdir(exist_ok=True)
  for kind,f in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
   (target/f).write_bytes(context.request.get(BASE+f'/help/source/sorting_array/{kind}').body())
  if name!='maximum':
   assert all((target/f).read_bytes()==(L/name/f).read_bytes() for f in ['main.c','tad_ordenamiento.c','tad_ordenamiento.h']);caller={'evidence_reused_from':str(L/name),'exact_bytes_unchanged':True,'native_not_rerun':True}
  else:caller=audit_program(target,[values,sorted(values)])
  page.screenshot(path=str(target/'terminal.png'),full_page=True)
  row=dict(case=name,logical_events=total,restorations=len(captures),fast_to_step_saved=True,reload_saved=True,extra_navigation_POSTs=0,helper_visible=any('counting_por_digito'in x['shown']['stack'] for x in captures),maximum_DOM_nodes=max(x['shown']['nodes'] for x in captures),five_sections=page.locator('.sorting-learning-stage').count(),javascript_errors=errors,caller=caller)
  (target/'frames.json').write_text(json.dumps(captures,ensure_ascii=False,indent=2),encoding='utf-8');rows.append(row);(E/'report.json').write_text(json.dumps(dict(cases=rows,browser=browser.version),indent=2),encoding='utf-8');print(name,total,len(captures),flush=True);context.close()
 browser.close()
