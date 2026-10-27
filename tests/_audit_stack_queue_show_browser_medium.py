"""Actual existing UI rejection and callers; no Mostrar exposure."""
from pathlib import Path
import sys,json,re,hashlib
from playwright.sync_api import sync_playwright
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-queue-show-instructions-medium';sys.stdout.reconfigure(encoding='utf-8');records=[];reuse=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for sid in ['stack','queue']:
  cases=[('empty',[]),('top',[9,17,3]),('bounds',[-2147483648,0,2147483647]),('minus1',[-1])] if sid=='stack' else [('empty',[]),('fifo',[17,9,3]),('bounds',[-2147483648,0,2147483647]),('minus1-front',[-1,17])]
  previous=E.parent/('visible-stack-cima-instructions-medium' if sid=='stack' else 'visible-queue-front-final-instructions-medium')
  for name,values in cases:
   ctx=browser.new_context();p=ctx.new_page();errs=[];posts=[];p.on('pageerror',lambda e:errs.append(str(e)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);p.goto('http://127.0.0.1:5051/sequential/'+sid)
   for v in (list(reversed(values)) if sid=='stack' else values):assert p.request.post('http://127.0.0.1:5051/sequential/'+sid+'/operate',data={'operation':'apilar' if sid=='stack' else 'encolar','payload':{'value':v}}).json()['success']
   p.reload();p.wait_for_function('id=>window.SEQ_VIEW_MODEL?.id===id',arg=sid);before=p.evaluate('window.SEQ_VIEW_MODEL');options=p.locator('#operation-select option').evaluate_all('els=>els.map(e=>e.value)');views=[]
   for view in ['current','linked']:p.click('#stack-view-'+view);views.append(p.locator('#visual-state').inner_text())
   rejected=[]
   for _ in range(2):
    r=p.request.post('http://127.0.0.1:5051/sequential/'+sid+'/operate',data={'operation':'mostrar','payload':{}});d=r.json();assert r.status==400 and not d['success'] and d['visual_state']==before['visual_state'];assert d['execution_trace']['steps']==[] and d['execution_trace']['execution_started'] is False;rejected.append({'HTTP':400,'data':d})
   count=len(posts);p.reload();p.wait_for_function('id=>window.SEQ_VIEW_MODEL?.id===id',arg=sid);after=p.evaluate('window.SEQ_VIEW_MODEL');afterviews=[]
   for view in ['current','linked']:p.click('#stack-view-'+view);afterviews.append(p.locator('#visual-state').inner_text())
   assert before['visual_state']==after['visual_state'] and before['history']==after['history'] and views==afterviews;body=p.locator('pre.didactic-history-main').evaluate_all(r'els=>els.map(e=>Array.from(e.querySelectorAll(".code-line")).map(l=>l.textContent).join("\n")).filter(t=>t.includes("int main"))');http=p.request.get('http://127.0.0.1:5051/help/source/'+sid+'/main');directory=E/'actual-callers'/sid/name;directory.mkdir(parents=True,exist_ok=True);(directory/'DOM-body.txt').write_text(body[0] if body else '',encoding='utf-8');kind='HTTP' if sid=='stack' and not values else 'DOM';main=None
   if sid=='stack':
    assert http.status==200
    if values:assert len(body)==1
    else:assert not body
    main=http.body();(directory/'HTTP-main-download.c').write_bytes(main);(directory/'main.c').write_text(main.decode('utf-8'),encoding='utf-8');main=(directory/'main.c').read_bytes()
   else:
    assert http.status==404
    if values:assert len(body)==1;main=('#include <stdio.h>\n#include "tad_cola.h"\n'+body[0]+'\n').encode('utf-8');(directory/'main.c').write_text(main.decode('utf-8'),encoding='utf-8');main=(directory/'main.c').read_bytes()
    else:assert not body
   if main:
    old=previous/'actual-callers'/name/'main.c';assert main==old.read_bytes();reuse.append({'structure':sid,'case':name,'current':str((directory/'main.c').relative_to(R)),'baseline':str(old.relative_to(R)),'SHA256':hashlib.sha256(main).hexdigest()});assert b'_mostrar(' not in main
   headings=p.locator('.sequential-stage h3').evaluate_all('els=>els.map(e=>e.textContent.trim())');out=E/'browser'/sid/name;out.mkdir(parents=True,exist_ok=True);p.screenshot(path=str(out/'reload.png'),full_page=True);(out/'reload.html').write_text(p.content(),encoding='utf-8');records.append({'structure':sid,'case':name,'values_order':values,'rejected':rejected,'not_registered':all(o['name']!='mostrar' for o in after['operations']),'no_selector':'mostrar' not in options,'readonly':before['visual_state']==after['visual_state'] and before['history']==after['history'],'views_equal':views==afterviews,'five_sections':[x[0] for x in headings if re.match(r'^[1-5]\s',x)]==list('12345'),'extra_UI_POSTs':len(posts)-count,'JS_errors':errs,'main_HTTP':http.status,'DOM_main':bool(body),'main_input_kind':kind if main else 'absent','standalone_mostrar_calls':0,'query_records':0});ctx.close()
 browser.close()
for sid,stem in [('stack','pila'),('queue','cola')]:
 previous=E.parent/('visible-stack-cima-instructions-medium' if sid=='stack' else 'visible-queue-front-final-instructions-medium')
 for ext in ['c','h']:
  current=R/'docs/tads_C'/('tad_'+stem+'.'+ext);old=previous/'native'/current.name
  # Medium native may not copy source; canonical source exactly equals original LOW inputs.
  if not old.exists():old=E.parent/('visible-stack-cima-baseline-low' if sid=='stack' else 'visible-queue-front-final-baseline-low')/'native'/current.name
  assert current.read_bytes()==old.read_bytes();reuse.append({'structure':sid,'case':'C/H','current':str(current.relative_to(R)),'baseline':str(old.relative_to(R)),'SHA256':hashlib.sha256(current.read_bytes()).hexdigest()})
(E/'browser-report.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');(E/'caller-input-reuse.json').write_text(json.dumps({'inputs':reuse,'count':len(reuse),'limits':'Stack4 andqueue3 actualmains,includesonlyqueue; exact11inputsC/H+7mains. C17/ownership/Doxygen from priorfinite inputs reused,not rerun. Native prepared main copy uses platform CRLF as historical compiler input; raw HTTP download LF saved separately. Source statements unchanged,includesonlyqueue. No Mostrarcaller records/calls.'},indent=2)+'\n',encoding='utf-8');print('Browser8contexts16reject400 readonly;7actualmain+4C/H exact11inputs reused.')
