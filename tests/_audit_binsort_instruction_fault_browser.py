# Native-causal error UI QA. Simulation is TESTING fixture, never actual OOM.
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.domain.sorting.counting_sparse_instructions import SimulatedCountingAllocationFailure
from playwright.sync_api import sync_playwright
E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-sorting-binsort-instructions'
BASE='http://127.0.0.1:5051'
CAPTURE=r'''() => ({array:Array.from(document.querySelectorAll('.sorting-item-label'),e=>Number(e.textContent.replace(/^\[\d+\]\s*/,''))),variables:Array.from(document.querySelectorAll('#sorting-variable-table tr'),r=>Array.from(r.querySelectorAll('td'),e=>e.textContent)),stack:Array.from(document.querySelectorAll('#sorting-call-stack strong'),e=>e.textContent),conditionClass:document.querySelector('#sorting-condition-view').className,active:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>Number(e.dataset.line)),activeText:Array.from(document.querySelectorAll('.code-line.sim-active'),e=>e.textContent),strategy:document.querySelector('#sorting-strategy-view').textContent,accepted:window.SORTING_VIEW_MODEL.visual_state})'''
report={'cases':[],'scope':'Real loopback preview range errors. NULL allocation browser response is TESTING app fixture injected via Playwright route, explicitly simulated; no actual memory exhaustion.'}
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for case in ['range_eighty','null_two']:
  fixture=json.loads((E/'native-errors'/(case+'.json')).read_text(encoding='utf-8'));values=fixture['case']['input'];sim=fixture['case']['simulated_calloc']
  context=browser.new_context();page=context.new_page();posts=[];errors=[]
  page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  page.goto(BASE+'/sorting/visualizador',wait_until='networkidle');page.locator('#sorting-manual-values').fill(','.join(map(str,values)))
  with page.expect_response('**/create-array'):page.click('#sorting-create-array')
  with page.expect_response('**/algorithm'):page.select_option('#sorting-algorithm','binsort')
  before=context.request.get(BASE+'/api/ordenamiento/state').json();main=before['main_c'];page.click('#sorting-sim-step')
  if sim:
   app=create_app();app.testing=True
   def fail(_length):raise SimulatedCountingAllocationFailure('isolated browser fixture')
   app.config['COUNTING_QA_ALLOCATOR']=fail;c=app.test_client();c.post('/api/ordenamiento/create-array',json={'values':values});c.post('/api/ordenamiento/algorithm',json={'algorithm_id':'binsort'})
   result=c.post('/api/ordenamiento/run',json={'algorithm_id':'binsort','mode':'step_by_step'});isolated=result.get_json();isolated_trace=isolated['execution_trace'];export=c.get(isolated_trace['export_url']).get_json()
   page.route('**/api/ordenamiento/run',lambda route:route.fulfill(status=400,content_type='application/json',body=json.dumps(isolated)))
   page.route('**'+isolated_trace['export_url'],lambda route:route.fulfill(status=200,content_type='application/json',body=json.dumps(export)))
   (E/'simulated-browser-response.json').write_text(json.dumps(isolated,ensure_ascii=False),encoding='utf-8')
  with page.expect_response('**/run') as got:page.click('#sorting-sim-play')
  response=got.value;assert response.status==400;d=response.json();t=d['execution_trace'];total=t.get('step_count',len(t.get('steps',[])))
  page.wait_for_function('(n)=>document.querySelector("#sorting-sim-counter").textContent===`Paso: 0/${n}`',arg=total)
  assert page.locator('#sorting-counting-outcome').is_visible() and page.locator('#sorting-counting-outcome').get_attribute('data-simulated')==str(sim).lower()
  if sim:assert 'Fallo simulado' in page.locator('#sorting-counting-outcome').text_content()
  count=len(posts);page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)')
  def jump(index):
   page.locator('#sorting-counting-jump').fill(str(index+1));page.click('#sorting-counting-go')
   page.wait_for_function('(args)=>document.querySelector("#sorting-sim-counter").textContent===`Paso: ${args[0]+1}/${args[1]}`',arg=[index,total])
  captures=[];indices=list(range(total)) if total<100 else sorted({0,1,2,11,12,15,total//2,total-5,total-4,total-3,total-2,total-1})
  for direction,chosen in [('forward',indices),('reverse',list(reversed(indices)))]:
   for idx in chosen:
    jump(idx);shown=page.evaluate(CAPTURE);raw=fixture['native'][idx]
    frame=t['steps'][idx] if 'steps' in t else context.request.get(BASE+t['page_url'],params={'start':idx,'limit':1}).json()['steps'][0]
    p=frame['pedagogy'];assert shown['array']==raw['array'] and shown['accepted']==d['visual_state']
    assert shown['active']==([] if frame['line_index'] is None else [frame['line_index']])
    assert shown['stack']==[x['function'] for x in p['call_stack']]
    if p['variables']:
     assert len(shown['variables'])==len(p['variables'])
     for cells,v in zip(shown['variables'],p['variables']):assert cells[:3]==[v['name'],v['type'],str(v['value']) if v['initialized'] else 'sin inicializar'] and v['scope'] in cells[3]
    else:assert not any(len(cells)==4 for cells in shown['variables']), (case,idx,shown['variables'])
    if raw['condition'] is not None:assert ('is-true' if raw['condition'] else 'is-false') in shown['conditionClass']
    assert frame['state_after']['trace_action'] in shown['strategy']
    if raw['token']=='error_return':assert 'return ORDENAMIENTO_ERROR' in shown['activeText'][0] and shown['stack']==['ordenar_binsort']
    if raw['token']=='binsort_return':assert 'return ordenar_counting_sort' in shown['activeText'][0] and not shown['stack'] and 'fuera de alcance' in shown['strategy']
    captures.append(dict(direction=direction,cursor=idx,shown=shown))
  jump(total-2);page.screenshot(path=str(E/(case+'-guard.png')),full_page=True)
  page.click('#sorting-sim-next');page.wait_for_function('(n)=>document.querySelector("#sorting-sim-counter").textContent===`Paso: ${n}/${n}`',arg=total)
  page.click('#sorting-sim-prev');page.wait_for_function('(n)=>document.querySelector("#sorting-sim-counter").textContent===`Paso: ${n-1}/${n}`',arg=total)
  page.click('#sorting-sim-step');page.click('#sorting-sim-step');jump(total-1)
  page.screenshot(path=str(E/(case+'-return.png')),full_page=True)
  with page.expect_download() as got:page.click('#sorting-export-summary')
  got.value.save_as(str(E/(case+'-summary.json')));summary=json.loads((E/(case+'-summary.json')).read_text(encoding='utf-8'))
  assert summary['state']==summary['accepted_state']==d['visual_state'] and summary['attempt_state']['trace_token']=='binsort_return' and summary['native_status']==0 and not summary['success'] and not summary['counting_trace']['success'] and summary['main_c']==main
  assert len(posts)==count and not errors and page.locator('.sorting-learning-stage').count()==5
  state=context.request.get(BASE+'/api/ordenamiento/state').json();assert state['history']==before['history'] and state['main_c']==main and state['visual_state']==before['visual_state']
  if not sim:
   page.reload(wait_until='networkidle');page.wait_for_function('(n)=>document.querySelector("#sorting-sim-counter").textContent===`Paso: ${n}/${n}`',arg=total)
   assert page.locator('#sorting-counting-outcome').is_visible() and page.evaluate('window.SORTING_VIEW_MODEL.visual_state')==before['visual_state'] and len(posts)==count
   page.locator('#sorting-manual-values').fill('5,0')
   with page.expect_response('**/create-array'):page.click('#sorting-create-array')
   with page.expect_response('**/run') as normal:page.click('#sorting-sim-play')
   assert normal.value.json()['success'];page.wait_for_function('document.querySelector("#sorting-counting-outcome").hidden')
  row=dict(case=case,simulated=sim,transport='isolated TESTING fixture' if sim else 'actual preview HTTP400',logical_events=total,restorations=len(captures),replay_extra_POSTs=0,scope_retirement_visible=True,accepted_history_main_unchanged=True,export_accepted_and_attempt_distinct=True,reload_verified=not sim,five_sections=True,errors=errors)
  report['cases'].append(row);(E/(case+'-browser.json')).write_text(json.dumps(dict(row=row,captures=captures),ensure_ascii=False,indent=2),encoding='utf-8');print(json.dumps(row),flush=True);context.close()
 browser.close()
(E/'browser-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
