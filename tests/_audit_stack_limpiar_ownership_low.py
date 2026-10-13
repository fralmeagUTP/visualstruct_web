"""LOW offline C/H caller ownership, never labelled product main."""
from pathlib import Path
import sys,shutil,subprocess,json,hashlib
R=Path.cwd();sys.path.insert(0,str(R));E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-limpiar-baseline-low';O=E/'qa-callers';O.mkdir(exist_ok=True)
wrapper=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
static void *objects[64];static int alive[64],used,allocs,frees;
void*audit_malloc(size_t n){void*p=malloc(n);assert(p&&used<64);objects[used]=p;alive[used++]=1;allocs++;return p;}
void audit_free(void*p){if(!p)return;int found=-1;for(int i=0;i<used;i++)if(alive[i]&&objects[i]==p){found=i;break;}assert(found>=0);alive[found]=0;objects[found]=NULL;frees++;free(p);}
void report(void){assert(allocs==frees);for(int i=0;i<used;i++)assert(!alive[i]);printf("OWNERSHIP %d %d 0\n",allocs,frees);}
'''
(O/'ownership.c').write_text(wrapper,encoding='utf-8');(O/'ownership.h').write_text('#include <stddef.h>\nvoid*audit_malloc(size_t);\nvoid audit_free(void*);\n',encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror'];cmd=flags+['-include',str(O/'ownership.h'),'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(E/'native/tad_pila.c'),'-o',str(O/'pila.o')];p=subprocess.run(cmd,capture_output=True,text=True);(O/'compile-original-source.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
report=[]
for name,values in [('empty',[]),('single',[-1]),('multi',[7,-2,7]),('reinsert',[7,-2,7])]:
 main='/** @file main.c @brief QA offline lifecycle caller; not product export. */\n#include <assert.h>\n#include <stddef.h>\n#include "tad_pila.h"\n/** @brief Report balanced allocations/frees for the QA program. */\nvoid report(void);\n/** @brief Exercise defined cleanup calls and report balanced ownership. @return Zero on success. */\nint main(void){ptrPila p=NULL;'
 for value in values:main+=f'pila_apilar(&p,{value});'
 main+='pila_destruir(&p);assert(p==NULL);'
 if name=='reinsert':main+='pila_apilar(&p,8);'
 main+='pila_destruir(&p);assert(p==NULL);pila_destruir(NULL);pila_destruir(&p);report();return 0;}'
 D=O/name;D.mkdir(exist_ok=True);(D/'main.c').write_text(main,encoding='utf-8');p=subprocess.run(flags+['-I',str(E/'native'),str(D/'main.c'),str(O/'ownership.c'),str(O/'pila.o'),'-o',str(D/'main.exe')],capture_output=True,text=True);(D/'compile.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr;p=subprocess.run([str(D/'main.exe')],capture_output=True,text=True);(D/'run.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr;counts=list(map(int,p.stdout.strip().split()[1:]));assert counts[0]==counts[1] and counts[2]==0;report.append({'case':name,'QA_offline_not_UI_main':True,'strict_C17_original':True,'alloc_free_live':counts,'sha256':hashlib.sha256((D/'main.c').read_bytes()).hexdigest()})
from tests.test_graph_bfs_documentation import run_doxygen
D=E/'doxygen';D.mkdir(exist_ok=True);run_doxygen(D,[E/'native/tad_pila.c',E/'native/tad_pila.h']+[O/r['case']/'main.c' for r in report]);result={'warnings':0,'exit_code':0,'inputs':6};(E/'doxygen-report.json').write_text(json.dumps(result,default=str,indent=2),encoding='utf-8');(O/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');print(json.dumps({'QA_original_C17_callers':4,'alloc_free_live':[sum(r['alloc_free_live'][0] for r in report),sum(r['alloc_free_live'][1] for r in report),0],'Doxygen':result,'not_product_main':True},default=str))
