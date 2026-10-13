"""Finite UI baseline for limpiar only; both views/replay/reload observations."""
from pathlib import Path
import json,re
from playwright.sync_api import sync_playwright
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-limpiar-baseline-low';B=E/'browser';B.mkdir(exist_ok=True)
s=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig');INJECT=s.split('INJECT="""')[1].split('"""')[0].replace('__hash','__stack')
SNAP='''() => ({state:window.__stackRendered,cursor:window.__stackPlayer.getCursor(),active:Array.from(document.querySelectorAll('#op-pseudocode .sim-active')).map(x=>Number(x.dataset.line)),done:Array.from(document.querySelectorAll('#op-pseudocode .sim-done')).map(x=>Number(x.dataset.line)),visual:document.querySelector('#visual-state').textContent,pointers:document.querySelector('#seq-pointers-view')?.textContent,heap:document.querySelector('#seq-heap-view')?.textContent,call:document.querySelector('#seq-call-view')?.textContent,console:document.querySelector('#seq-printf-console')?.textContent})'''
report=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name,values in [('empty',[]),('single',[-1]),('multi',[7,-2,7]),('reinsert',[7,-2,7])]:
  context=browser.new_context();p=context.new_page();p.add_init_script(INJECT);p.on('dialog',lambda dialog:dialog.accept());errors=[];posts=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);p.goto('http://127.0.0.1:5051/sequential/stack')
  for v in values:p.request.post('http://127.0.0.1:5051/sequential/stack/operate',data={'operation':'apilar','payload':{'value':v}})
  p.reload();forward=back=0;observations=[]
  for repeat in [1,2]:
   if name=='reinsert' and repeat==2:p.request.post('http://127.0.0.1:5051/sequential/stack/operate',data={'operation':'apilar','payload':{'value':8}});p.reload()
   p.select_option('#operation-select','limpiar')
   if not p.locator('#seq-step-toggle').is_checked():p.click('#seq-step-mode')
   with p.expect_response(lambda r:'/sequential/stack/operate' in r.url and r.request.method=='POST') as response:p.click('#seq-sim-execute')
   d=response.value.json();assert d['success'] and not d['visual_state']['items'];trace=d['execution_trace'];p.wait_for_function('()=>window.__stackTrace?.operation_name==="limpiar"');count=len(posts);eventshots=[]
   for view in ['current','linked']:
    p.click('#stack-view-'+view);p.evaluate('window.__stackPlayer.seek(-1)');shots=[]
    for i,f in enumerate(trace['steps']):
     p.evaluate('(i)=>window.__stackPlayer.seek(i)',i);shot=p.evaluate(SNAP);assert shot['state']==f['state_after'] and shot['cursor']==i
     assert f['line_index'] in shot['active'] or (i==len(trace['steps'])-1 and f['line_index'] in shot['done']);shots.append(shot);forward+=1
     if '*p = aux->sgte;' in f['line_text']:eventshots.append({'view':view,'line':f['line_text'],'snapshot':shot})
    for i in range(len(shots)-2,-1,-1):p.click('#seq-sim-prev');assert p.evaluate(SNAP)==shots[i];back+=1
    assert len(posts)==count
   p.evaluate('window.__stackPlayer.seek(0)');assert len(posts)==count;observations.append({'repeat':repeat,'frames':len(trace['steps']),'eventshots':eventshots,'trace':trace})
  last=p.evaluate('window.__stackTrace');count=len(posts);p.reload();reload_equal=p.evaluate('window.__stackTrace')==last;assert len(posts)==count and not errors
  headings=p.locator('main h3,main summary').evaluate_all('els=>els.map(e=>e.textContent)');numbered=[re.sub(r'\s+',' ',h).strip().replace('Mostrar','').replace('Ocultar','').strip() for h in headings if re.match(r'\s*[1-5]\s',h)];expected=['1 Preparar y controlar ejecución','2 Visualizar y ejecutar','3 Relacionar con código','4 Comprender','5 Resultados de ejecución'];assert numbered==expected,numbered
  for kind,ext in [('source','c'),('header','h')]:assert p.request.get('http://127.0.0.1:5051/help/source/stack/'+kind).body()==(E/'native'/('tad_pila.'+ext)).read_bytes()
  directory=B/name;directory.mkdir(exist_ok=True);p.screenshot(path=str(directory/'final.png'),full_page=True);report.append({'case':name,'actions':2,'forward_same_trace_two_views':forward,'back_same_trace_two_views':back,'five_numbered_sections':numbered,'auxiliary_regions':p.locator('.sequential-stage').count()-5,'JS_errors':errors,'extra_POSTs':0,'reload_trace_equal':reload_equal,'observations':observations});context.close()
 browser.close()
(B/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps([{k:v for k,v in r.items() if k!='observations'} for r in report]))
