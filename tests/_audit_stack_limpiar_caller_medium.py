"""Original actual UI session mains C17/Doxygen/ownership and deterministic NULL faults."""
from pathlib import Path
import json,sys,subprocess,shutil,hashlib
R=Path.cwd();sys.path.insert(0,str(R));E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-limpiar-instructions-medium';L=E.parent/'visible-stack-limpiar-baseline-low';O=E/'caller-ownership';O.mkdir(exist_ok=True)
WRAPPER=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
static void*objects[64];static int alive[64],used,allocs,frees,attempts,fault;
static void report(void){int live=0;for(int i=0;i<used;i++)live+=alive[i];fprintf(stderr,"OWNERSHIP %d %d %d\n",allocs,frees,live);assert(live==0&&allocs==frees);}
void*audit_malloc(size_t n){if(attempts==0){const char*value=getenv("QA_NULL_POINT");fault=value?atoi(value):0;atexit(report);}attempts++;if(attempts==fault)return NULL;void*p=malloc(n);assert(p&&used<64);objects[used]=p;alive[used++]=1;allocs++;return p;}
void audit_free(void*p){if(!p)return;int found=-1;for(int i=0;i<used;i++)if(alive[i]&&objects[i]==p){found=i;break;}assert(found>=0);alive[found]=0;objects[found]=NULL;frees++;free(p);}
'''
(O/'ownership.c').write_text(WRAPPER,encoding='utf-8');(O/'ownership.h').write_text('#include <stddef.h>\nvoid*audit_malloc(size_t);\nvoid audit_free(void*);\n',encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror'];p=subprocess.run(flags+['-include',str(O/'ownership.h'),'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(L/'native/tad_pila.c'),'-o',str(O/'pila.o')],capture_output=True,text=True);(O/'compile-C.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
report=[]
for name,count in [('empty',0),('single',1),('multi',3),('reinsert',4)]:
 D=O/name;D.mkdir(exist_ok=True);main=E/'callers'/(name+'.c');shutil.copyfile(main,D/'main.c')
 for cmd,log in [(flags+['-I',str(L/'native'),str(main),str(L/'native/tad_pila.c'),'-o',str(D/'original.exe')],'compile-original.log'),(flags+['-I',str(L/'native'),str(main),str(O/'ownership.c'),str(O/'pila.o'),'-o',str(D/'ownership.exe')],'compile-ownership.log')]:
  p=subprocess.run(cmd,capture_output=True,text=True);(D/log).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
 original=subprocess.run([str(D/'original.exe')],capture_output=True,text=True);(D/'original.log').write_text(original.stdout+original.stderr,encoding='utf-8');assert original.returncode==0 and original.stdout.splitlines()[-1]=='state:[]'
 normal=subprocess.run([str(D/'ownership.exe')],capture_output=True,text=True);(D/'ownership.log').write_text(normal.stdout+normal.stderr,encoding='utf-8');assert normal.returncode==0 and normal.stdout==original.stdout
 if count:assert normal.stderr.strip()==f'OWNERSHIP {count} {count} 0'
 else:assert normal.stderr==''
 faults=[]
 import os
 for point in range(1,count+1):
  env=dict(os.environ);env['QA_NULL_POINT']=str(point);p=subprocess.run([str(D/'ownership.exe')],env=env,capture_output=True,text=True);(D/(f'fault-{point}.log')).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==1 and p.stderr.strip()==f'OWNERSHIP {point-1} {point-1} 0';faults.append({'point':point,'exit':1,'alloc_free_live':[point-1,point-1,0]})
 report.append({'case':name,'actual_product_main':True,'strict_C17_original':True,'sha256':hashlib.sha256(main.read_bytes()).hexdigest(),'alloc_free_live':[count,count,0],'original_output':original.stdout,'NULL_faults':faults})
from tests.test_graph_bfs_documentation import run_doxygen
D=E/'caller-doxygen';D.mkdir(exist_ok=True);run_doxygen(D,[L/'native/tad_pila.c',L/'native/tad_pila.h']+[O/r['case']/'main.c' for r in report]);(O/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8');(E/'caller-doxygen.json').write_text(json.dumps({'warnings':0,'exit':0,'inputs':6,'actual_mains':4}),encoding='utf-8');print(json.dumps({'actual_C17_mains':4,'alloc_free_live':[sum(r['alloc_free_live'][0] for r in report),sum(r['alloc_free_live'][1] for r in report),0],'NULL_fault_points':sum(len(r['NULL_faults']) for r in report),'Doxygen_warnings':0}))
