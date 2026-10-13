"""Compare actual DOM versus HTTP stack callers; fault evidence cannot assume clean exit."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib,os,re
R=Path.cwd();sys.path.insert(0,str(R))
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-apilar-baseline-low';N=E/'native';O=E/'caller-ownership';O.mkdir(exist_ok=True)
WRAPPER=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
static void*objects[64];static int alive[64],used,allocs,frees,attempts,fault;
static void report(void){int live=0;for(int i=0;i<used;i++)live+=alive[i];fprintf(stderr,"OWNERSHIP %d %d %d\n",allocs,frees,live);}
void*audit_malloc(size_t n){if(attempts==0){const char*value=getenv("QA_NULL_POINT");fault=value?atoi(value):0;atexit(report);}attempts++;if(attempts==fault)return NULL;void*p=malloc(n);assert(p&&used<64);objects[used]=p;alive[used++]=1;allocs++;return p;}
void audit_free(void*p){if(!p)return;int found=-1;for(int i=0;i<used;i++)if(alive[i]&&objects[i]==p){found=i;break;}assert(found>=0);alive[found]=0;objects[found]=NULL;frees++;free(p);}
'''
(O/'ownership.c').write_text(WRAPPER,encoding='utf-8');(O/'ownership.h').write_text('#include <stddef.h>\nvoid*audit_malloc(size_t);\nvoid audit_free(void*);\n',encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
p=subprocess.run(flags+['-include',str(O/'ownership.h'),'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(N/'tad_pila.c'),'-o',str(O/'pila.o')],capture_output=True,text=True);(O/'compile-C.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
report=[]
for surface in ['DOM','HTTP']:
 for name,count in [('empty',2),('single',3),('duplicate',3),('bounds',4)]:
  D=O/surface/name;D.mkdir(parents=True,exist_ok=True);actual=E/'actual-callers'/name/('main.c' if surface=='DOM' else 'HTTP-main.c');main=D/'main.c';shutil.copyfile(actual,main)
  for cmd,log in [(flags+['-I',str(N),str(main),str(N/'tad_pila.c'),'-o',str(D/'original.exe')],'compile-original.log'),(flags+['-I',str(N),str(main),str(O/'ownership.c'),str(O/'pila.o'),'-o',str(D/'ownership.exe')],'compile-ownership.log')]:
   p=subprocess.run(cmd,capture_output=True,text=True);(D/log).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
  original=subprocess.run([str(D/'original.exe')],capture_output=True,text=True);normal=subprocess.run([str(D/'ownership.exe')],capture_output=True,text=True);(D/'original.log').write_text(original.stdout+original.stderr,encoding='utf-8');(D/'ownership.log').write_text(normal.stdout+normal.stderr,encoding='utf-8');assert original.returncode==normal.returncode==0 and normal.stdout==original.stdout
  ledger=[int(v) for v in re.search(r'OWNERSHIP (\d+) (\d+) (\d+)',normal.stderr).groups()];assert ledger==([count,0,count] if surface=='DOM' else [count,count,0])
  faults=[]
  for point in range(1,count+1):
   env=dict(os.environ);env['QA_NULL_POINT']=str(point);p=subprocess.run([str(D/'ownership.exe')],env=env,capture_output=True,text=True);(D/f'fault-{point}.log').write_text(p.stdout+p.stderr,encoding='utf-8');ledger_fault=[int(v) for v in re.search(r'OWNERSHIP (\d+) (\d+) (\d+)',p.stderr).groups()]
   assert p.returncode==(0 if surface=='DOM' else 1) and ledger_fault==([count-1,0,count-1] if surface=='DOM' else [point-1,point-1,0])
   assert 'Error: No se pudo asignar memoria.' in p.stdout
   applied=p.stdout.count('Operacion aplicada.') if surface=='DOM' else p.stdout.count('push:')
   assert applied==(count if surface=='DOM' else point-1)
   faults.append({'point':point,'exit':p.returncode,'alloc_free_live':ledger_fault,'kernel_diagnostic':True,'failed_push_falsely_applied':surface=='DOM','success_messages':applied})
  report.append({'case':name,'surface':surface,'actual_product_main':True,'strict_C17':True,'sha256':hashlib.sha256(actual.read_bytes()).hexdigest(),'body_unchanged_from_actual_product':True,'normal_alloc_free_live':ledger,'NULL_faults':faults,'normal_stdout':original.stdout})
(O/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
from tests.test_graph_bfs_documentation import run_doxygen
import xml.etree.ElementTree as ET
dox=[]
for surface in ['DOM','HTTP']:
 D=E/('doxygen-'+surface);D.mkdir(exist_ok=True);run_doxygen(D,[N/'tad_pila.c',N/'tad_pila.h']+[O/surface/name/'main.c' for name in ['empty','single','duplicate','bounds']]);symbols=[]
 for path in (D/'doxygen/xml').glob('*.xml'):
  tree=ET.parse(path)
  for member in tree.findall('.//memberdef'):
   if member.findtext('name')=='main':symbols.append({'file':path.name,'documented':member.find('briefdescription/para') is not None or member.find('detaileddescription/para') is not None})
 dox.append({'surface':surface,'inputs_C_H_actual_mains':6,'warnings':0,'main_symbols':symbols,'documented':sum(s['documented'] for s in symbols)})
(E/'caller-doxygen.json').write_text(json.dumps(dox,indent=2),encoding='utf-8');print(json.dumps({'histories':4,'caller_surfaces':2,'DOM':{'C17':4,'normal_alloc_free_live':[12,0,12],'NULL_faults':12,'exit_on_fault':0,'false_success':True},'HTTP':{'C17':4,'normal_alloc_free_live':[12,12,0],'NULL_faults':12,'exit_on_fault':1,'false_success':False},'distinct_fault_positions_each_surface':12,'not_24_independent_fixtures':True,'Doxygen':dox}))
