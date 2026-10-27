"""Actual Prim browser caller baseline; retains failing original strict build."""
from pathlib import Path
import sys,json,threading,subprocess,shutil,re,hashlib
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from app import create_app
from werkzeug.serving import make_server
from playwright.sync_api import sync_playwright
OUT=Path(sys.argv[1]).resolve();OUT.mkdir(parents=True,exist_ok=True)
CASES=[dict(name='single_vertex',v=[-1],e=[],start=-1),dict(name='connected',v=[1,2,3],e=[(1,2,4),(1,3,1),(3,2,2)],start=1),dict(name='disconnected',v=[1,2,3,4],e=[(1,2,2),(3,4,3)],start=1)]
app=create_app();server=make_server('127.0.0.1',0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}';rows=[];compiler=shutil.which('gcc');assert compiler
try:
 with sync_playwright() as p:
  browser=p.chromium.launch()
  for c in CASES:
   out=OUT/c['name'];out.mkdir();context=browser.new_context();page=context.new_page();posts=[];errors=[];page.on('request',lambda r:posts.append(r.url) if r.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
   for op,payload in [('create_graph',{'directed':False}),*[('insert_vertex',{'vertex':v}) for v in c['v']],*[('insert_edge',{'origin':a,'target':b,'weight':w}) for a,b,w in c['e']]]:
    response=context.request.post(base+'/graph/graph/operate',data={'operation':op,'payload':payload});assert response.json()['success']
   page.add_init_script("document.addEventListener('DOMContentLoaded',()=>{const old=window.InterpreterRuntime.createTracePlayer;window.InterpreterRuntime.createTracePlayer=function(options){const player=old(options);window.primPlayer=player;return player;};});")
   page.goto(base+'/graph/graph/expansion-minima',wait_until='networkidle');page.select_option('#graph-algorithm-select','run_prim');page.locator('#g-alg-field-start').fill(str(c['start']));results=[]
   for _ in range(2):
    with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-sim-play')
    data=response.value.json();assert data['success'];results.append(data['result'])
   main='\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');(out/'main.c').write_text(main,encoding='utf-8')
   count=len(posts)
   page.evaluate("async()=>{const toggle=document.querySelector('#graph-step-toggle');toggle.checked=true;toggle.dispatchEvent(new Event('change'));window.primPlayer.pause();window.primPlayer.reset();await window.primPlayer.step();window.primPlayer.prev();window.primPlayer.seek(window.primPlayer.getTotalSteps()-1);toggle.checked=false;toggle.dispatchEvent(new Event('change'));}")
   assert len(posts)==count
   for _ in range(2):page.reload(wait_until='networkidle')
   reloaded='\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');(out/'reloaded-main.c').write_text(reloaded,encoding='utf-8');assert len(posts)==count==2;assert not errors
   assert main.count('= grafo_prim(')==2 and reloaded.count('= grafo_prim(')==2
   # Replay the already executed query without executing a new POST.
   page.select_option('#graph-algorithm-select','run_prim');page.locator('#g-alg-field-start').fill(str(c['start']))
   # A missing start is rejected; its invocation must never enter main/history.
   page.locator('#g-alg-field-start').fill('999')
   with page.expect_response(lambda r:r.url.endswith('/graph/graph/operate') and r.request.method=='POST') as response:page.click('#graph-sim-play')
   rejected=response.value.json();assert not rejected['success']
   after_failure='\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');assert after_failure==reloaded
   before_failed_reload=len(posts);page.reload(wait_until='networkidle');assert len(posts)==before_failed_reload==3
   assert '\n'.join(page.locator('.didactic-history-main .code-line').all_text_contents()).replace('\u00a0','')==reloaded

   for tad,stem in [('graph','tad_grafo'),('queue','tad_cola')]:
    for part,ext in [('source','c'),('header','h')]:
     response=context.request.get(base+'/help/source/'+tad+'/'+part);assert response.status==200;(out/(stem+'.'+ext)).write_bytes(response.body())
   build=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'main.c'),str(out/'tad_grafo.c'),str(out/'tad_cola.c'),'-o',str(out/'original.exe')],capture_output=True,text=True,timeout=30);(out/'original-strict-compile.log').write_text(build.stdout+build.stderr)
   original_stdout=None;original_returncode=None
   if build.returncode==0:
    original=subprocess.run([str(out/'original.exe')],capture_output=True,text=True,timeout=10);original_stdout=original.stdout;original_returncode=original.returncode;(out/'original.stdout.log').write_text(original.stdout+original.stderr)

   # Observation only: record returned pointer uses, not new frees or algorithm
   # changes. Original compile result is reported separately and never replaced.
   header='#include <stddef.h>\nvoid *owned_malloc(size_t);\nvoid *owned_calloc(size_t,size_t);\nvoid owned_free(void*);\n';(out/'ownership.h').write_text(header)
   observer=r"""
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
static void *ptrs[4096];static int live[4096],total,allocations,frees,observed_results;
static void *track(void *p){if(p){assert(total<4096);ptrs[total]=p;live[total++]=1;allocations++;}return p;}
void *owned_malloc(size_t n){return track(malloc(n));}
void *owned_calloc(size_t n,size_t z){return track(calloc(n,z));}
void owned_free(void *p){if(p){int found=0;for(int i=0;i<total;i++){if(live[i]&&ptrs[i]==p){live[i]=0;found=1;break;}}assert(found);frees++;}free(p);}
void observe_result(void *p){if(p)observed_results++;}
static void ownership_done(void){int remaining=0;for(int i=0;i<total;i++)remaining+=live[i];printf("OWNERSHIP %d %d %d %d\n",allocations,frees,remaining,observed_results);}
#define free owned_free
"""
   observed=re.sub(r'(ListaArco (mst_\d+) = grafo_prim\([^;]+;)',r'\1 observe_result(\2);',main);observed=observer+observed.replace('    return 0;','    ownership_done();\n    return 0;');(out/'observed-main.c').write_text(observed,encoding='utf-8');objects=[]
   for stem in ['tad_grafo','tad_cola']:
    obj=out/(stem+'.o');r=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-include',str(out/'ownership.h'),'-Dmalloc=owned_malloc','-Dcalloc=owned_calloc','-Dfree=owned_free','-c',str(out/(stem+'.c')),'-o',str(obj)],capture_output=True,text=True,timeout=30);assert r.returncode==0 and not r.stderr,r.stderr;objects.append(obj)
   r=subprocess.run([compiler,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'observed-main.c'),*map(str,objects),'-o',str(out/'observed.exe')],capture_output=True,text=True,timeout=30);assert r.returncode==0 and not r.stderr,r.stderr;run=subprocess.run([str(out/'observed.exe')],capture_output=True,text=True,timeout=10);assert run.returncode==0; (out/'observed.stdout.log').write_text(run.stdout);m=re.search(r'^OWNERSHIP (\d+) (\d+) (\d+) (\d+)$',run.stdout,re.M);assert m
   row={'case':c['name'],'actual_calls':2,'before_reload_calls':main.count('= grafo_prim('),'after_reload_calls':reloaded.count('= grafo_prim('),'extra_reload_POSTs':len(posts)-before_failed_reload,'replay_extra_POSTs':0,'failed_query_omitted':True,'original_stdout':original_stdout,'original_returncode':original_returncode,'page_errors':errors,'result':results,'original_strict_c17_pass':build.returncode==0,'original_compile_returncode':build.returncode,'caller_output_is_precomputed':bool(re.search(r'printf\("Prim desde',main)),'actual_main_sha256':hashlib.sha256((out/'main.c').read_bytes()).hexdigest(),'observational_variant_only':True,'ownership':{'allocations':int(m[1]),'frees':int(m[2]),'live':int(m[3]),'non_null_results':int(m[4])}};rows.append(row);(out/'browser-report.json').write_text(json.dumps(row,ensure_ascii=False,indent=2));print(json.dumps(row),flush=True);context.close()
  browser.close()
finally:server.shutdown();thread.join(timeout=5)
(OUT/'report.json').write_text(json.dumps({'scope':'actual caller/reload baseline, not instruction verification','rows':rows},ensure_ascii=False,indent=2),encoding='utf-8')
