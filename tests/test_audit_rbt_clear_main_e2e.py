"""Actual downloaded clear history, repeated invocations and allocation/free observer variants."""
from pathlib import Path
import json,re,subprocess,shutil
import pytest
from test_audit_avl_main_e2e import avl_server
from test_audit_rbt_queries_main_e2e import compile_main
pytestmark=pytest.mark.e2e

def observe_program_memory(target,expected_allocations,expected_stdout):
 gcc=shutil.which('gcc');code=r'''#include <stdio.h>
#include <stdlib.h>
static void *refs[128];static int live[128],count,releases;
void *audit_malloc(size_t n){void*p=malloc(n);if(p){refs[count]=p;live[count++]=1;}return p;}
void audit_free(void *p){int id=-1;for(int i=0;i<count;i++)if(live[i]&&refs[i]==p){id=i;break;}if(id<0)exit(71);live[id]=0;releases++;free(p);}
static void __attribute__((destructor)) audit_done(void){for(int i=0;i<count;i++)if(live[i]){puts("AUDIT_LEAK");return;}printf("AUDIT_MEMORY %d %d\n",count,releases);}
'''
 (target/'observer.c').write_text(code,encoding='utf-8');obj=target/'instrumented-tad.o';args=['-std=c17','-Wall','-Wextra','-Wpedantic','-Werror']
 build=subprocess.run([gcc,*args,'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(target/'tad_rojo_negro.c'),'-o',str(obj)],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 build=subprocess.run([gcc,*args,str(target/'main.c'),str(target/'observer.c'),str(obj),'-o',str(target/'observer.exe')],capture_output=True,text=True,timeout=30);assert build.returncode==0,build.stderr
 run=subprocess.run([str(target/'observer.exe')],capture_output=True,text=True,timeout=5);assert run.returncode==0 and run.stdout==expected_stdout+f'AUDIT_MEMORY {expected_allocations} {expected_allocations}\n',run.stdout;(target/'memory-stdout.log').write_text(run.stdout);return {'allocations':expected_allocations,'frees':expected_allocations,'observer_variant':True,'no_live_reservations_at_exit':True}
@pytest.mark.parametrize('seed',[[],[7],[10,5,15,3,7,12,18],[-2147483648,0,2147483647]])
def test_rbt_clear_downloaded_main_empty_populated_repeat_reload(avl_server,tmp_path,seed):
 with pytest.importorskip('playwright.sync_api').sync_playwright() as p:
  browser=p.chromium.launch();context=browser.new_context();page=context.new_page();posts=[];errors=[];page.on('request',lambda req:posts.append(req.url) if req.method=='POST' else None);page.on('pageerror',lambda e:errors.append(str(e)))
  for v in seed:assert context.request.post(avl_server+'/hierarchical/red_black/operate',data={'operation':'insertar','payload':{'value':v}}).json()['success']
  page.goto(avl_server+'/hierarchical/red_black',wait_until='networkidle');page.select_option('#operation-select','limpiar')
  def clear():
   with page.expect_response(lambda resp:resp.url.endswith('/red_black/operate') and resp.request.method=='POST') as response:page.click('#hier-sim-play')
   data=response.value.json();assert data['success'] and data['visual_state']['root'] is None and data['visual_state']['size']==0;page.wait_for_function("()=>!document.querySelector('#hier-sim-play').disabled")
  clear();clear();assert len(posts)==2;mains=[];programs=[];variants=[]
  for label,operations in [('before',2),('after',2),('repeat',3)]:
   if label=='after':n=len(posts);page.reload(wait_until='networkidle');assert len(posts)==n
   if label=='repeat':page.select_option('#operation-select','limpiar');clear()
   main='\n'.join(page.locator('#action-history .didactic-history-main .code-line').all_text_contents()).replace('\u00a0','');mains.append(main);body=re.sub(r'/\*.*?\*/|//[^\n]*','',main.split('int main(void)',1)[1],flags=re.S)
   # History keeps each requested cleanup; a separate final caller cleanup adds no operation/output.
   assert body.count('rbt_liberar(arbol);')==operations+1 and body.count('arbol = NULL;')==operations+2
   assert main.count('// Limpieza final del caller; no es otra operacion del historial.')==1
   assert body.rsplit('rbt_liberar(arbol); arbol = NULL;',1)[1].strip()=='return 0;\n}'
   target=tmp_path/label;program=compile_main(main,context,avl_server,target);expected='\tEl numero ha sido insertado\n'*len(seed)+'LIMPIAR\n'*operations;assert program['stdout']==expected
   programs.append(program);variants.append(observe_program_memory(target,len(seed),expected))
  assert mains[0]==mains[1] and not errors and len(posts)==3;context.close();browser.close()
 (tmp_path/'rbt-clear-main-review.json').write_text(json.dumps({'seed':seed,'actual_programs':programs,'memory_observer_variants':variants,'main_stable_reload':True,'reload_posts':0,'errors':errors,'instruction_UI_closure':False},indent=2))
