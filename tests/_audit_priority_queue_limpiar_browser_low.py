"""Finite UI baseline for limpiar only; both views/replay/reload observations."""
from pathlib import Path
import json,re
from playwright.sync_api import sync_playwright
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-priority-queue-limpiar-baseline-completion-low';B=E/'browser';B.mkdir(exist_ok=True)
s=(R/'tests/_audit_hash_query_medium_browser.py').read_text(encoding='utf-8-sig');INJECT=s.split('INJECT="""')[1].split('"""')[0].replace('__hash','__priority')
SNAP='''() => ({state:window.__priorityRendered,cursor:window.__priorityPlayer.getCursor(),active:Array.from(document.querySelectorAll('#op-pseudocode .sim-active')).map(x=>Number(x.dataset.line)),done:Array.from(document.querySelectorAll('#op-pseudocode .sim-done')).map(x=>Number(x.dataset.line)),visual:document.querySelector('#visual-state').textContent,pointers:document.querySelector('#seq-pointer-view')?.textContent,heap:document.querySelector('#seq-heap-view')?.textContent,call:document.querySelector('#seq-call-view')?.textContent,console:document.querySelector('#seq-printf-console')?.textContent})'''
report=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name,values in [('empty',[]),('single',[(-1,2)]),('multi',[(7,3),(-2,1),(7,1)]),('reinsert',[(7,3),(-2,1),(7,1)])]:
  context=browser.new_context();p=context.new_page();p.add_init_script(INJECT);p.on('dialog',lambda dialog:dialog.accept());errors=[];posts=[];p.on('pageerror',lambda e:errors.append(str(e)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);p.goto('http://127.0.0.1:5051/sequential/priority_queue')
  for v,priority in values:p.request.post('http://127.0.0.1:5051/sequential/priority_queue/operate',data={'operation':'encolar','payload':{'value':v,'priority':priority}})
  p.reload();forward=back=0;observations=[]
  for repeat in [1,2]:
   if name=='reinsert' and repeat==2:p.request.post('http://127.0.0.1:5051/sequential/priority_queue/operate',data={'operation':'encolar','payload':{'value':8,'priority':-1}});p.reload()
   p.select_option('#operation-select','limpiar')
   if not p.locator('#seq-step-toggle').is_checked():p.click('#seq-step-mode')
   with p.expect_response(lambda r:'/sequential/priority_queue/operate' in r.url and r.request.method=='POST') as response:p.click('#seq-sim-execute')
   d=response.value.json();assert d['success'] and not d['visual_state']['items'];trace=d['execution_trace'];p.wait_for_function('()=>window.__priorityTrace?.operation_name==="limpiar"');count=len(posts);eventshots=[]
   for view in ['current','linked']:
    p.click('#stack-view-'+view);p.evaluate('window.__priorityPlayer.seek(-1)');shots=[]
    for i,f in enumerate(trace['steps']):
     p.evaluate('(i)=>window.__priorityPlayer.seek(i)',i);shot=p.evaluate(SNAP);assert shot['state']==f['state_after'] and shot['cursor']==i
     assert f['line_index'] in shot['active'] or (i==len(trace['steps'])-1 and f['line_index'] in shot['done']);shots.append(shot);forward+=1
     if any(t in f['line_text'] for t in ['next = aux->sgte;', 'cola->delante = next;', 'free(aux);', 'cola->atras = NULL;', 'cola->cantidad--;']):eventshots.append({'view':view,'line':f['line_text'],'snapshot':shot})
    for i in range(len(shots)-2,-1,-1):p.click('#seq-sim-prev');assert p.evaluate(SNAP)==shots[i];back+=1
    assert len(posts)==count
   p.evaluate('window.__priorityPlayer.seek(0)');assert len(posts)==count;observations.append({'repeat':repeat,'frames':len(trace['steps']),'eventshots':eventshots,'trace':trace})
  last=p.evaluate('window.__priorityTrace');last_history=d['history'];count=len(posts);before_counter=p.locator('#seq-sim-counter').inner_text();p.reload();reload_equal=p.evaluate('window.__priorityTrace')==last;assert len(posts)==count and not errors
  headings=p.locator('main h3,main summary').evaluate_all('els=>els.map(e=>e.textContent)');numbered=[re.sub(r'\s+',' ',h).strip().replace('Mostrar','').replace('Ocultar','').strip() for h in headings if re.match(r'\s*[1-5]\s',h)];expected=['1 Preparar y controlar ejecución','2 Visualizar y ejecutar','3 Relacionar con código','4 Comprender','5 Resultados de ejecución'];heading_match=numbered==expected
  for kind,ext in [('source','c'),('header','h')]:assert p.request.get('http://127.0.0.1:5051/help/source/priority_queue/'+kind).body()==(E.parent/'visible-priority-queue-limpiar-baseline-low/native'/('tad_cola_prioridad.'+ext)).read_bytes()
  directory=B/name;directory.mkdir(exist_ok=True);(directory/'reload.html').write_text(p.content(),encoding='utf-8');actual_main_fragments=p.locator('pre.didactic-history-main').evaluate_all(r'els=>els.map(e=>Array.from(e.querySelectorAll(".code-line")).map(l=>l.textContent).join("\n")).filter(t=>t.includes("int main"))');mainbody=actual_main_fragments[0] if actual_main_fragments else '';caller_dir=E/'actual-callers'/name;caller_dir.mkdir(parents=True,exist_ok=True);(caller_dir/'main.c').write_text('#include <stdio.h>\n#include \"tad_cola_prioridad.h\"\n'+mainbody+'\n',encoding='utf-8');(caller_dir/'DOM-body.txt').write_text(mainbody,encoding='utf-8');main_response=p.request.get('http://127.0.0.1:5051/help/source/priority_queue/main');links=p.locator('a').evaluate_all('els=>els.map(e=>({text:e.textContent,href:e.getAttribute("href")}))');p.screenshot(path=str(directory/'final.png'),full_page=True);report.append({'case':name,'actions':2,'forward_same_trace_two_views':forward,'back_same_trace_two_views':back,'numbered_headings':numbered,'five_numbered_sections_match':heading_match,'actual_main_fragments':actual_main_fragments,'main_HTTP_status':main_response.status,'links':links,'history_after_reload':p.evaluate('window.SEQ_VIEW_MODEL.history'),'history_before_reload':last_history,'history_reload_equal':p.evaluate('window.SEQ_VIEW_MODEL.history')==last_history,'counter_before_reload':before_counter,'counter_after_reload':p.locator('#seq-sim-counter').inner_text(),'auxiliary_regions':p.locator('.sequential-stage').count()-5,'JS_errors':errors,'extra_POSTs':0,'reload_trace_equal':reload_equal,'observations':observations});context.close()
 browser.close()
(B/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps([{k:v for k,v in r.items() if k!='observations'} for r in report]))
