"""Actual RBT insertion histories: downloaded caller, reload and ownership baseline."""
from pathlib import Path
import json,subprocess,re,shutil
import pytest
from test_audit_avl_main_e2e import avl_server
from test_audit_rbt_queries_main_e2e import compile_main
pytestmark=pytest.mark.e2e

def observe_owner(target,expected_allocations,expected_stdout):
 code=r'''#include <stdio.h>
#include <stdlib.h>
static void *refs[128];static int live[128],count,releases;
void *audit_malloc(size_t n){void*p=malloc(n);if(p){refs[count]=p;live[count++]=1;}return p;}
void audit_free(void*p){int id=-1;for(int i=0;i<count;i++)if(live[i]&&refs[i]==p){id=i;break;}if(id<0)exit(71);live[id]=0;releases++;free(p);}
static void __attribute__((destructor)) audit_done(void){int alive=0;for(int i=0;i<count;i++)alive+=live[i];printf("AUDIT_OWNER %d %d %d\n",count,releases,alive);}
'''
 (target/'observer.c').write_text(code,encoding='utf-8');gcc=shutil.which('gcc');flags=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror']
 build=subprocess.run([gcc,*flags,'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(target/'tad_rojo_negro.c'),'-o',str(target/'raw-observed.o')],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 build=subprocess.run([gcc,*flags,str(target/'main.c'),str(target/'observer.c'),str(target/'raw-observed.o'),'-o',str(target/'observed.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0 and not build.stderr,build.stderr
 run=subprocess.run([str(target/'observed.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0 and run.stdout.startswith(expected_stdout),run.stdout
 tail=run.stdout[len(expected_stdout):];m=re.fullmatch(r'AUDIT_OWNER (\d+) (\d+) (\d+)\n',tail);assert m;allocated,freed,alive=map(int,m.groups());assert allocated==expected_allocations and allocated==freed+alive
 (target/'ownership-observer.log').write_text(run.stdout,encoding='utf-8');return {'allocated':allocated,'freed':freed,'live_at_exit':alive,'observer_variant':True,'executable_final_cleanup':alive==0}

@pytest.mark.parametrize('seed,value',[([30,20],10),([10,30],20),([0,-2147483648],2147483647),([20,10,30,5,15,25,35],1)])
def test_rbt_insert_actual_downloaded_main_duplicate_reload(avl_server,tmp_path,seed,value):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();errors=[];posts=[];page.on('pageerror',lambda e:errors.append(str(e)));page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None)
  for v in seed:assert context.request.post(avl_server+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
  page.goto(avl_server+'/hierarchical/red_black',wait_until='networkidle');page.select_option('#operation-select','insertar');page.locator('[name="value"]').fill(str(value))
  with page.expect_response(lambda resp:resp.url.endswith('/red_black/operate') and resp.request.method=='POST') as response:page.click('#hier-sim-play')
  success=response.value.json();assert success['success'];page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled")
  with page.expect_response(lambda resp:resp.url.endswith('/red_black/operate') and resp.request.method=='POST') as response:page.click('#hier-sim-play')
  failure=response.value.json();assert not failure['success'] and failure['history']==success['history'] and failure['visual_state']==success['visual_state'];page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled");assert len(posts)==2
  mains=[];programs=[]
  for label in ['before','after']:
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');mains.append(main)
   body=re.sub(r'/\*.*?\*/|//[^\n]*','',main.split('int main(void)',1)[1],flags=re.S);calls=re.findall(r'rbt_insertar\(&arbol,\s*(-?\d+)\);',body);assert list(map(int,calls))==seed+[value]
   target=tmp_path/label;result=compile_main(main,context,avl_server,target);expected='\tEl numero ha sido insertado\n'*(len(seed)+1);assert result['stdout']==expected
   # Ownership is measured, not inferred from successful compilation.
   result['owner']=observe_owner(target,len(seed)+1,expected);assert result['owner']['freed']==len(seed)+1 and result['owner']['live_at_exit']==0;assert 'rbt_liberar(arbol); arbol = NULL;' in body;programs.append(result)
   if label=='before':n=len(posts);page.reload(wait_until='networkidle');assert len(posts)==n
  assert mains[0]==mains[1] and not errors;context.close();browser.close()
 (tmp_path/'rbt-insert-main-review.json').write_text(json.dumps({'seed':seed,'value':value,'actual_programs':programs,'stable_reload':True,'no_replay_POST':True,'duplicate_excluded':True,'errors':errors,'instruction_UI_closed':False,'ownership_finding':programs[0]['owner']['live_at_exit']>0},indent=2),encoding='utf-8')
