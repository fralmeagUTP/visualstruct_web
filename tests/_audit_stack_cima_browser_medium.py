"""Actual unchanged UI/rejected Cima attempts and DOM/HTTP callers, no injected feature."""
from pathlib import Path
import json,re,sys,subprocess,shutil,os,hashlib
from playwright.sync_api import sync_playwright
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-cima-instructions-medium';B=E/'browser';B.mkdir(exist_ok=True);report=[];CASES=[('empty',[]),('top',[9,17,3]),('bounds',[-2147483648,0,2147483647]),('minus1',[-1])]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name,values in CASES:
  context=browser.new_context();p=context.new_page();errors=[];posts=[];p.on('pageerror',lambda x:errors.append(str(x)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);p.goto('http://127.0.0.1:5051/sequential/stack')
  for v in reversed(values):assert p.request.post('http://127.0.0.1:5051/sequential/stack/operate',data={'operation':'apilar','payload':{'value':v}}).json()['success']
  p.reload();p.wait_for_function('()=>window.SEQ_VIEW_MODEL?.id==="stack"');before=p.evaluate('window.SEQ_VIEW_MODEL');options=p.locator('#operation-select option').evaluate_all('els=>els.map(e=>e.value)');views=[]
  for view in ['current','linked']:p.click('#stack-view-'+view);views.append({'view':view,'text':p.locator('#visual-state').inner_text()})
  rejected=[]
  for repeat in [1,2]:
   r=p.request.post('http://127.0.0.1:5051/sequential/stack/operate',data={'operation':'cima','payload':{}});data=r.json();assert r.status==400 and not data['success'] and data['visual_state']==before['visual_state'];assert data['execution_trace']['steps']==[] and data['execution_trace']['execution_started'] is False;rejected.append({'HTTP':r.status,'data':data})
  count=len(posts);p.reload();p.wait_for_function('()=>window.SEQ_VIEW_MODEL?.id==="stack"');after=p.evaluate('window.SEQ_VIEW_MODEL');afterviews=[]
  for view in ['current','linked']:p.click('#stack-view-'+view);afterviews.append({'view':view,'text':p.locator('#visual-state').inner_text()})
  assert before['visual_state']==after['visual_state'] and before['history']==after['history'];assert not any(x['operation']=='cima' for x in after['history'])
  mains=p.locator('pre.didactic-history-main').evaluate_all(r'els=>els.map(e=>Array.from(e.querySelectorAll(".code-line")).map(l=>l.textContent).join("\n")).filter(t=>t.includes("int main"))');r=p.request.get('http://127.0.0.1:5051/help/source/stack/main');assert r.status==200;body=r.body().decode('utf-8').replace('\r\n','\n');assert (len(mains)==1 and mains[0]==body) if values else len(mains)==0
  d=E/'actual-callers'/name;d.mkdir(parents=True,exist_ok=True);(d/'main.c').write_text(body,encoding='utf-8');(d/'DOM-body.txt').write_text(mains[0] if mains else '',encoding='utf-8');(d/'HTTP-main.c').write_bytes(r.body());out=B/name;out.mkdir(exist_ok=True);(out/'reload.html').write_text(p.content(),encoding='utf-8');p.screenshot(path=str(out/'reload.png'),full_page=True);headings=p.locator('.sequential-stage h3').evaluate_all('els=>els.map(e=>e.textContent.trim())')
  record={'case':name,'values_top_to_bottom':values,'before':before['visual_state'],'after':after['visual_state'],'rejected':rejected,'public_cima_not_registered':not any(x['name']=='cima' for x in after['operations']),'no_cima_selector':'cima' not in options,'history_unchanged':before['history']==after['history'],'views_before':views,'views_after':afterviews,'both_views_exactly_unchanged':views==afterviews,'five_sections':[x[0] for x in headings if re.match(r'^[1-5]\s',x)]==list('12345'),'extra_UI_POSTs':len(posts)-count,'JS_errors':errors,'HTTP_main_status':200,'DOM_HTTP_main_equal':bool(values),'DOM_main_present':bool(values),'actual_main_SHA':hashlib.sha256((d/'main.c').read_bytes()).hexdigest(),'standalone_queries_in_history':0,'integrated_setup_pila_cima_calls':body.count('pila_cima('),'limits':'No accepted/public Cima query or UI player; Cima references in real callers belong to setup push echoes, not rejected query records. Prepared push views are same sourceframe on both reloads; no push fidelity rerun.'};report.append(record);(B/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');context.close()
 browser.close()

print("Current browser4contexts8rejects validation0steps; nofeature;3DOM+4HTTPcaller unchangedprotocol")
