"""Existing UI/read-only rejected methods and actual DOM callers; no query feature injection."""
from pathlib import Path
import sys,json,re,subprocess,shutil,os,hashlib
from playwright.sync_api import sync_playwright
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
from tests.test_graph_bfs_documentation import run_doxygen
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-queue-front-final-baseline-low';B=E/'browser';B.mkdir(exist_ok=True);CASES=[('empty',[]),('fifo',[17,9,3]),('bounds',[-2147483648,0,2147483647]),('minus1-front',[-1,17])];METHODS=['frente','final'];report=[]
with sync_playwright() as pw:
 browser=pw.chromium.launch(headless=True)
 for name,values in CASES:
  context=browser.new_context();p=context.new_page();errors=[];posts=[];p.on('pageerror',lambda x:errors.append(str(x)));p.on('request',lambda r:posts.append(r.url) if r.method=='POST' and '/operate' in r.url else None);p.goto('http://127.0.0.1:5051/sequential/queue')
  for value in values:assert p.request.post('http://127.0.0.1:5051/sequential/queue/operate',data={'operation':'encolar','payload':{'value':value}}).json()['success']
  p.reload();p.wait_for_function('()=>window.SEQ_VIEW_MODEL?.id==="queue"');before=p.evaluate('window.SEQ_VIEW_MODEL');options=p.locator('#operation-select option').evaluate_all('els=>els.map(x=>x.value)');views=[]
  for view in ['current','linked']:p.click('#stack-view-'+view);views.append({'view':view,'text':p.locator('#visual-state').inner_text()})
  rejected={}
  for method in METHODS:
   rejected[method]=[]
   for repeat in range(2):
    r=p.request.post('http://127.0.0.1:5051/sequential/queue/operate',data={'operation':method,'payload':{}});d=r.json();assert r.status==400 and not d['success'] and d['visual_state']==before['visual_state'];rejected[method].append({'HTTP':400,'data':d})
  count=len(posts);p.reload();p.wait_for_function('()=>window.SEQ_VIEW_MODEL?.id==="queue"');after=p.evaluate('window.SEQ_VIEW_MODEL');afterviews=[]
  for view in ['current','linked']:p.click('#stack-view-'+view);afterviews.append({'view':view,'text':p.locator('#visual-state').inner_text()})
  assert after['visual_state']==before['visual_state'] and after['history']==before['history'];assert not any(x['operation'] in METHODS for x in after['history']);mains=p.locator('pre.didactic-history-main').evaluate_all(r'els=>els.map(e=>Array.from(e.querySelectorAll(".code-line")).map(l=>l.textContent).join("\n")).filter(t=>t.includes("int main"))');r=p.request.get('http://127.0.0.1:5051/help/source/queue/main');assert r.status==404;assert (len(mains)==1) if values else (len(mains)==0)
  d=E/'actual-callers'/name;d.mkdir(parents=True,exist_ok=True);body=mains[0] if mains else '';(d/'DOM-body.txt').write_text(body,encoding='utf-8')
  if body:(d/'main.c').write_text('#include <stdio.h>\n#include "tad_cola.h"\n'+body+'\n',encoding='utf-8')
  directory=B/name;directory.mkdir(exist_ok=True);(directory/'reload.html').write_text(p.content(),encoding='utf-8');p.screenshot(path=str(directory/'reload.png'),full_page=True);headings=p.locator('.sequential-stage h3').evaluate_all('els=>els.map(e=>e.textContent.trim())')
  record={'case':name,'values_FIFO':values,'rejected_by_method':rejected,'no_new_selectors':all(method not in options for method in METHODS),'not_registered':all(x['name'] not in METHODS for x in after['operations']),'history_readonly':after['history']==before['history'],'visual_state_readonly':after['visual_state']==before['visual_state'],'views_before':views,'views_after':afterviews,'both_views_unchanged':views==afterviews,'five_sections':[x[0] for x in headings if re.match(r'^[1-5]\s',x)]==list('12345'),'extra_UI_POSTs':len(posts)-count,'JS_errors':errors,'main_HTTP_status':404,'DOM_main_present':bool(body),'caller_SHA':hashlib.sha256((d/'main.c').read_bytes()).hexdigest() if body else None,'standalone_query_records':0,'standalone_calls_by_method':{method:body.count('cola_'+method+'(') for method in METHODS},'limits':'Actual existing UI, two rejected requests per method. Empty no DOM/HTTP main;3 nonempty callers exactDOM withincludesonly. No queryselector/player/Next/reverse or record fabricated.'};report.append(record);(B/'report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');context.close()
 browser.close()
N=E/'native';O=E/'caller-ownership';O.mkdir(exist_ok=True);old=E.parent/'visible-queue-encolar-baseline-low/caller-ownership'
for f in ['ownership.c','ownership.h']:shutil.copyfile(old/f,O/f)
flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror'];cmd=flags+['-include',str(O/'ownership.h'),'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(N/'tad_cola.c'),'-o',str(O/'cola.o')];q=subprocess.run(cmd,capture_output=True,text=True);(O/'compile-source.log').write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0,q.stderr;callers=[]
for name,values in CASES:
 if not values:continue
 d=O/name;d.mkdir(exist_ok=True);main=E/'actual-callers'/name/'main.c';runs={}
 for owned in [False,True]:
  label='ownership' if owned else 'C17';exe=d/(label+'.exe');cmd=flags+['-I',str(N),str(main)]+([str(O/'cola.o'),str(O/'ownership.c')] if owned else [str(N/'tad_cola.c')])+['-o',str(exe)];q=subprocess.run(cmd,capture_output=True,text=True);(d/(label+'-compile.log')).write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0,q.stderr;q=subprocess.run([str(exe)],capture_output=True,text=True);(d/(label+'-run.log')).write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==0;expected='Operacion aplicada.\n'*len(values);assert q.stdout==expected,(q.stdout,expected)
  if owned:assert f'OWNERSHIP {len(values)} {len(values)} 0' in q.stderr
  runs[label]={'exit':q.returncode,'stdout':q.stdout,'stderr':q.stderr}
 faults=[]
 for point in range(1,len(values)+1):
  env=os.environ.copy();env['QA_NULL_POINT']=str(point);q=subprocess.run([str(d/'ownership.exe')],capture_output=True,text=True,env=env);(d/f'NULL-{point}.log').write_text(q.stdout+q.stderr,encoding='utf-8');assert q.returncode==1 and f'OWNERSHIP {point-1} {point-1} 0' in q.stderr;faults.append({'point':point,'exit':q.returncode,'stdout':q.stdout,'stderr':q.stderr})
 callers.append({'case':name,'SHA':hashlib.sha256(main.read_bytes()).hexdigest(),'runs':runs,'alloc':len(values),'free':len(values),'live':0,'controlled_NULL':faults,'standalone_query_calls':{method:main.read_text(encoding='utf-8').count('cola_'+method+'(') for method in METHODS},'query_records':0})
(E/'caller-report-before-Doxygen.json').write_text(json.dumps({'cases':callers,'scope':'Three actual nonemptyDOMcallers;empty absent noHTTPmain404; no accepted independentqueries'},indent=2)+'\n',encoding='utf-8')
D=E/'caller-doxygen';D.mkdir(exist_ok=True);inputs=[N/'tad_cola.c',N/'tad_cola.h']+[E/'actual-callers'/name/'main.c' for name,values in CASES if values];run_doxygen(D,inputs)
import xml.etree.ElementTree as ET
symbols=[]
for p in (D/'doxygen/xml').glob('*.xml'):
 for symbol in ET.parse(p).findall('.//memberdef'):
  if symbol.findtext('name') in ['main','cola_frente','cola_final']:symbols.append({'file':p.name,'name':symbol.findtext('name'),'documented':bool(''.join(symbol.find('briefdescription').itertext()).strip())})
assert len([x for x in symbols if x['name']=='main'])==3 and all(x['documented'] for x in symbols)
(E/'caller-report.json').write_text(json.dumps({'cases':callers,'Doxygen_inputs':5,'Doxygen_warnings':0,'documented_mains':3,'documented_symbols':symbols,'empty_caller_absent':True,'main_HTTP':404,'limits':'3actualDOMmainincludesonly,8setupalloc/free0live8controlledNULL; querykernel0allocation. No queryrecords/currentpublicquerycaller,OOMreal/sanitizers/universalguarantee.'},indent=2)+'\n',encoding='utf-8');print('Browser4contexts16reject queries (8each),noexposure/read-only;3actualDOMmainsC17/8allocfree0live8NULL/Doxygen5inputs3main0warnings;empty noDOM/HTTPmain404')
