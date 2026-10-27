"""Download the actual main/C/H from eleven real UI histories, compile and observe ownership."""
from pathlib import Path
import sys,json,threading,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from app.domain.sorting import SORTING_ALGORITHMS
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
from _audit_sorting_main_native import audit_program
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();rows=[];empty=None;empty_reset_verified=False;selected=sys.argv[2] if len(sys.argv)>2 else None
assert selected is None or selected in {a["id"] for a in SORTING_ALGORITHMS}|{"empty"}
PRIMARY_BUTTONS={"sorting-create-array","sorting-random-array","sorting-sim-play","sorting-sim-step","sorting-sim-prev","sorting-sim-next","sorting-reset"}
COUNTING_BUTTONS={"sorting-counting-go","sorting-counting-replay","sorting-counting-pause"}
CONTROL_SELECTOR='#sorting-controls button, .sorting-execution-controls button'
try:
 with sync_playwright() as pw:
  browser=pw.chromium.launch()
  for alg in SORTING_ALGORITHMS:
   if selected is not None and alg["id"]!=selected:continue
   name=alg['id'];target=OUT/name;target.mkdir(exist_ok=True);context=browser.new_context(accept_downloads=True);page=context.new_page();posts=[];errors=[];expected=[];downloads=[]
   page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   page.goto(f'http://127.0.0.1:{server.server_port}/sorting/visualizador',wait_until='networkidle');page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');button_ids=set(page.locator(CONTROL_SELECTOR).evaluate_all('(buttons)=>buttons.map(b=>b.id)'));assert button_ids==PRIMARY_BUTTONS|COUNTING_BUTTONS,page.locator(CONTROL_SELECTOR).evaluate_all('(buttons)=>buttons.map(b=>({id:b.id,text:b.textContent.trim(),type:b.type}))');button_count=len(button_ids)
   def action(selector,route,accepted=True,duplicate=False):
    with page.expect_response(lambda r:r.url.endswith('/'+route)) as resp:
     if duplicate:page.evaluate('selector=>{const e=document.querySelector(selector);e.click();e.click();}',selector)
     else:page.click(selector)
    d=resp.value.json();assert d['success']==accepted,d
    if accepted and route in ['create-array','random-array','run']:expected.append(d['visual_state']['items'])
    if accepted:page.wait_for_function('code=>document.querySelector(".didactic-history-main").textContent===code',arg=d['main_c'])
    return d
   def create(values):
    page.locator('#sorting-manual-values').fill(','.join(map(str,values)));return action('#sorting-create-array','create-array')
   create([3,1,3,-2,0]);page.select_option('#sorting-algorithm',name);page.wait_for_function('name=>document.querySelector(".didactic-history-main").textContent.includes("Metodo preparado: ordenar_"+name)',arg=name)
   first=action('#sorting-sim-play','run',duplicate=True);assert sum(p.endswith('/run') for p in posts)==1
   second=action('#sorting-sim-play','run');before=page.locator('.didactic-history-main').text_content();assert before.count('printf("Run ')==2;(target/'main-before-reload.c').write_text(before,encoding='utf-8');count=len(posts)
   page.reload(wait_until='networkidle');page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');after=page.locator('.didactic-history-main').text_content();(target/'main-after-reload.c').write_text(after,encoding='utf-8');assert after==before and len(posts)==count,{'before':before,'after':after,'posts':posts,'before_count':count}
   page.locator('#sorting-random-size').fill('4');page.locator('#sorting-random-min').fill('-5');page.locator('#sorting-random-max').fill('5');random=action('#sorting-random-array','random-array');assert random['history'][-1]['materialized_values']==random['visual_state']['items'];action('#sorting-sim-play','run')
   # Recreate at int32 extremes. Counting/Bin range is rejected, not forged into main.
   create([2147483647,-2147483648,0]);last=action('#sorting-sim-play','run',accepted=name not in ['counting_sort','binsort'])
   if name=='burbuja':
    create(list(range(-40,40)));last=action('#sorting-sim-play','run');stable=page.locator('.didactic-history-main').text_content()
    for values in ['1.5','2147483648','',','.join(['1']*81)]:
     page.locator('#sorting-manual-values').fill(values);action('#sorting-create-array','create-array',accepted=False);assert page.locator('.didactic-history-main').text_content()==stable
   main=page.locator('.didactic-history-main').text_content();count=len(posts)
   page.click('#sorting-sim-step');page.click('#sorting-sim-step');assert len(posts)==count and page.locator('.didactic-history-main').text_content()==main
   page.reload(wait_until='networkidle');page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');assert page.locator('.didactic-history-main').text_content()==main and len(posts)==count
   page.get_by_role('tab',name='main.c del historial',exact=True).click()
   assert page.locator('#sorting-action-history').is_visible()
   for kind,filename in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
    link=page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]')
    with page.expect_download() as got:link.click()
    download=got.value;assert download.suggested_filename==filename;download.save_as(str(target/filename));response=context.request.get(f'http://127.0.0.1:{server.server_port}/help/source/sorting_array/{kind}');assert response.status==200 and response.body()==(target/filename).read_bytes();downloads.append({'kind':kind,'name':filename,'status':response.status,'content_type':response.headers['content-type'],'content_disposition':response.headers['content-disposition'],'sha256':hashlib.sha256(response.body()).hexdigest()})
   assert (target/'main.c').read_text(encoding='utf-8')==main
   with page.expect_download() as got:page.click('#sorting-export-summary')
   got.value.save_as(str(target/'summary-export.json'));assert json.loads((target/'summary-export.json').read_text(encoding='utf-8'))['main_c']==main
   state=context.request.get(f'http://127.0.0.1:{server.server_port}/api/ordenamiento/state').json();assert state['main_c']==main and state['visual_state']['items']==expected[-1]
   assert set(page.locator(CONTROL_SELECTOR).evaluate_all('(buttons)=>buttons.map(b=>b.id)'))==button_ids;assert button_count==10;assert page.locator('.sorting-learning-stage').count()==5;assert not errors
   native=audit_program(target,expected);row={'algorithm':name,'original_data':[3,1,3,-2,0],'random_values':random['visual_state']['items'],'runs':sum(e['operation']=='run' for e in state['history']),'duplicate_pending_extra_run_POSTs':0,'reload_replay_extra_POSTs':len(posts)-count,'same_main_after_reload':True,'control_button_elements':button_count,'primary_execution_control_elements':len(PRIMARY_BUTTONS),'counting_navigation_control_elements':len(COUNTING_BUTTONS),'new_execution_buttons':0,'five_stages':True,'page_errors':errors,'downloads':downloads,'native':native};rows.append(row);(target/'browser-report.json').write_text(json.dumps(row,ensure_ascii=False,indent=2),encoding='utf-8');(target/'history.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),encoding='utf-8');page.screenshot(path=str(target/'final.png'),full_page=True);print(json.dumps({'algorithm':name,'runs':row['runs'],'allocations':native['allocations'],'frees':native['frees'],'strictC17':True}),flush=True);context.close()
  if selected is None or selected=="empty":
   # Download the actual initial/reset empty main with no invented sorting call.
   context=browser.new_context(accept_downloads=True);page=context.new_page();page.goto(f'http://127.0.0.1:{server.server_port}/sorting/visualizador',wait_until='networkidle');page.locator('#didactic-mode-switch').check();page.evaluate('document.querySelectorAll("details").forEach(e=>e.open=true)');target=OUT/'empty';target.mkdir(exist_ok=True)
   page.get_by_role('tab',name='main.c del historial',exact=True).click()
   assert page.locator('#sorting-action-history').is_visible()
   for kind,filename in [('main','main.c'),('source','tad_ordenamiento.c'),('header','tad_ordenamiento.h')]:
    with page.expect_download() as got:page.locator(f'#sorting-action-history a[href="/help/source/sorting_array/{kind}"]').click()
    got.value.save_as(str(target/filename))
   empty=audit_program(target,[[]]);assert empty['successful_native_runs']==0
   initial=(target/'main.c').read_text(encoding='utf-8');page.locator('#sorting-manual-values').fill('1')
   with page.expect_response(lambda r:r.url.endswith('/create-array')):page.click('#sorting-create-array')
   with page.expect_response(lambda r:r.url.endswith('/run')):page.click('#sorting-sim-play')
   page.once('dialog',lambda dialog:dialog.accept())
   with page.expect_response(lambda r:r.url.endswith('/reset')) as reset:page.click('#sorting-reset')
   assert reset.value.json()['main_c']==initial;page.wait_for_function('s=>document.querySelector(".didactic-history-main").textContent===s',arg=initial)
   page.reload(wait_until='networkidle');assert page.locator('.didactic-history-main').text_content()==initial
   (target/'reset-response.json').write_text(json.dumps(reset.value.json(),ensure_ascii=False,indent=2),encoding='utf-8');context.close();empty_reset_verified=True
  browser.close()
finally:server.shutdown();thread.join(timeout=5)
(OUT/'report.json').write_text(json.dumps({'rows':rows,'empty':empty,'unique_method_histories':len(rows),'actual_downloaded_programs':len(rows)+(empty is not None),'empty_reset_verified':empty_reset_verified,'selected_case':selected,'successful_native_calls':sum(r['native']['successful_native_runs'] for r in rows),'allocations':sum(r['native']['allocations'] for r in rows),'frees':sum(r['native']['frees'] for r in rows),'scope':'real UI callers/downloads; no new algorithm or instruction signoff'},ensure_ascii=False,indent=2),encoding='utf-8')
