"""Actual unchanged UI/rejected Cima attempts and DOM/HTTP callers, no injected feature."""
from pathlib import Path
import json,re,sys,subprocess,shutil,os,hashlib
from playwright.sync_api import sync_playwright
R=Path.cwd();E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-cima-baseline-low';B=E/'browser';B.mkdir(exist_ok=True);report=[];CASES=[('empty',[]),('top',[9,17,3]),('bounds',[-2147483648,0,2147483647]),('minus1',[-1])]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name,values in CASES:
  context=browser.new_context();p=context.new_page();errors=[];posts=[];p.on('pageerror',lambda x:errors.append(str(x)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);p.goto('http://127.0.0.1:5051/sequential/stack')
  for v in reversed(values):assert p.request.post('http://127.0.0.1:5051/sequential/stack/operate',data={'operation':'apilar','payload':{'value':v}}).json()['success']
  p.reload();p.wait_for_function('()=>window.SEQ_VIEW_MODEL?.id==="stack"');before=p.evaluate('window.SEQ_VIEW_MODEL');options=p.locator('#operation-select option').evaluate_all('els=>els.map(e=>e.value)');views=[]
  for view in ['current','linked']:p.click('#stack-view-'+view);views.append({'view':view,'text':p.locator('#visual-state').inner_text()})
  rejected=[]
  for repeat in [1,2]:
   r=p.request.post('http://127.0.0.1:5051/sequential/stack/operate',data={'operation':'cima','payload':{}});data=r.json();assert r.status==400 and not data['success'] and data['visual_state']==before['visual_state'];rejected.append({'HTTP':r.status,'data':data})
  count=len(posts);p.reload();p.wait_for_function('()=>window.SEQ_VIEW_MODEL?.id==="stack"');after=p.evaluate('window.SEQ_VIEW_MODEL');afterviews=[]
  for view in ['current','linked']:p.click('#stack-view-'+view);afterviews.append({'view':view,'text':p.locator('#visual-state').inner_text()})
  assert before['visual_state']==after['visual_state'] and before['history']==after['history'];assert not any(x['operation']=='cima' for x in after['history'])
  mains=p.locator('pre.didactic-history-main').evaluate_all(r'els=>els.map(e=>Array.from(e.querySelectorAll(".code-line")).map(l=>l.textContent).join("\n")).filter(t=>t.includes("int main"))');r=p.request.get('http://127.0.0.1:5051/help/source/stack/main');assert r.status==200;body=r.body().decode('utf-8').replace('\r\n','\n');assert (len(mains)==1 and mains[0]==body) if values else len(mains)==0
  d=E/'actual-callers'/name;d.mkdir(parents=True,exist_ok=True);(d/'main.c').write_text(body,encoding='utf-8');(d/'DOM-body.txt').write_text(mains[0] if mains else '',encoding='utf-8');(d/'HTTP-main.c').write_bytes(r.body());out=B/name;out.mkdir(exist_ok=True);(out/'reload.html').write_text(p.content(),encoding='utf-8');p.screenshot(path=str(out/'reload.png'),full_page=True);headings=p.locator('.sequential-stage h3').evaluate_all('els=>els.map(e=>e.textContent.trim())')
  record={'case':name,'values_top_to_bottom':values,'before':before['visual_state'],'after':after['visual_state'],'rejected':rejected,'public_cima_not_registered':not any(x['name']=='cima' for x in after['operations']),'no_cima_selector':'cima' not in options,'history_unchanged':before['history']==after['history'],'views_before':views,'views_after':afterviews,'both_views_exactly_unchanged':views==afterviews,'five_sections':[x[0] for x in headings if re.match(r'^[1-5]\s',x)]==list('12345'),'extra_UI_POSTs':len(posts)-count,'JS_errors':errors,'HTTP_main_status':200,'DOM_HTTP_main_equal':bool(values),'DOM_main_present':bool(values),'actual_main_SHA':hashlib.sha256((d/'main.c').read_bytes()).hexdigest(),'standalone_queries_in_history':0,'integrated_setup_pila_cima_calls':body.count('pila_cima('),'limits':'No accepted/public Cima query or UI player; Cima references in real callers belong to setup push echoes, not rejected query records. Prepared push views are same sourceframe on both reloads; no push fidelity rerun.'};report.append(record);(B/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');context.close()
 browser.close()
N=E/'native';O=E/'caller-ownership';O.mkdir(exist_ok=True);old=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-apilar-instructions-medium/caller-ownership'
for f in ['ownership.c','ownership.h']:shutil.copyfile(old/f,O/f)
flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror'];cmd=flags+['-include',str(O/'ownership.h'),'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(N/'tad_pila.c'),'-o',str(O/'pila.o')];q=subprocess.run(cmd,capture_output=True,text=True);(O/'compile-source.log').write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0,q.stderr
callers=[]
for name,values in CASES:
 d=O/name;d.mkdir(exist_ok=True);main=E/'actual-callers'/name/'main.c';runs={}
 for owned in [False,True]:
  label='ownership' if owned else 'C17';exe=d/(label+'.exe');cmd=flags+['-I',str(N),str(main)]+([str(O/'pila.o'),str(O/'ownership.c')] if owned else [str(N/'tad_pila.c')])+['-o',str(exe)];q=subprocess.run(cmd,capture_output=True,text=True);(d/(label+'-compile.log')).write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0,q.stderr;q=subprocess.run([str(exe)],capture_output=True,text=True);(d/(label+'-run.log')).write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0
  expected=''.join('push:'+str(v)+'\n' for v in reversed(values))+'state:['+','.join(map(str,values))+']\n';assert q.stdout==expected,(q.stdout,expected)
  if owned and values:assert 'OWNERSHIP '+str(len(values))+' '+str(len(values))+' 0' in q.stderr
  runs[label]={'exit':q.returncode,'stdout':q.stdout,'stderr':q.stderr}
 faults=[]
 for point in range(1,len(values)+1):
  env=os.environ.copy();env['QA_NULL_POINT']=str(point);q=subprocess.run([str(d/'ownership.exe')],capture_output=True,text=True,env=env);(d/f'NULL-{point}.log').write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==1;assert f'OWNERSHIP {point-1} {point-1} 0' in q.stderr;faults.append({'point':point,'exit':q.returncode,'stderr':q.stderr})
 callers.append({'case':name,'SHA':hashlib.sha256(main.read_bytes()).hexdigest(),'runs':runs,'alloc':len(values),'free':len(values),'live':0,'faults':faults,'scope':'Actual DOM/HTTP main unchanged after rejected Cima queries. No standalone query record reproduced; integrated setup calls native computed.'})
from scripts.test_tool_paths import resolve_doxygen
D=E/'caller-doxygen';D.mkdir(exist_ok=True);inputs=[N/'tad_pila.c',N/'tad_pila.h']+[E/'actual-callers'/name/'main.c' for name,_ in CASES];config='PROJECT_NAME = CimaBaseline\nOUTPUT_DIRECTORY = "'+str(D/'output')+'"\nINPUT = '+' '.join('"'+str(p)+'"' for p in inputs)+'\nRECURSIVE = NO\nEXTRACT_ALL = NO\nWARN_IF_UNDOCUMENTED = YES\nWARN_IF_DOC_ERROR = YES\nGENERATE_HTML = NO\nGENERATE_LATEX = NO\nGENERATE_XML = YES\nQUIET = YES\nWARN_LOGFILE = "'+str(D/'warnings.log')+'"\n';(D/'Doxyfile').write_text(config,encoding='utf-8');q=subprocess.run([str(R/'../..') if False else resolve_doxygen(),str(D/'Doxyfile')],capture_output=True,text=True);(D/'run.log').write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0;warnings=(D/'warnings.log').read_text(encoding='utf-8');assert not warnings.strip(),warnings
import xml.etree.ElementTree as ET
xml=[]
for p in (D/'output/xml').glob('*main_8c.xml'):
 for symbol in ET.parse(p).findall('.//memberdef'):
  if symbol.findtext('name')=='main':xml.append({'file':p.name,'documented':bool(''.join(symbol.find('briefdescription').itertext()).strip())})
assert len(xml)==4 and all(x['documented'] for x in xml)
(E/'caller-report.json').write_text(json.dumps({'cases':callers,'Doxygen_warnings':0,'documented_mains':4,'inputs':6,'public_Cima_doc_verified':bool(list((D/'output/xml').glob('tad__pila_8*.xml'))),'limits':'7alloc/free setup/cleanup,7controlledNULL; no target Cima allocation, OOMreal/sanitizer/universal/leak guarantees. No accepted standalone query caller.'},indent=2)+'\n',encoding='utf-8');print('browser4contexts8rejectedqueries nofeature; actual3DOM+4HTTPmains C17 ownership7/7/0 NULL7 Doxygen0')
