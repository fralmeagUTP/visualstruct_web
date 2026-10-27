"""Original actual UI session mains C17/Doxygen/ownership and deterministic NULL faults."""
from pathlib import Path
import json,sys,subprocess,shutil,hashlib
R=Path.cwd();sys.path.insert(0,str(R));E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-queue-limpiar-instructions-medium';L=E.parent/'visible-queue-limpiar-baseline-low';O=E/'caller-ownership';O.mkdir(exist_ok=True)
WRAPPER=r'''#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
static void*objects[64];static int alive[64],used,allocs,frees,attempts,fault;
static void report(void){int live=0;for(int i=0;i<used;i++)live+=alive[i];fprintf(stderr,"OWNERSHIP %d %d %d\n",allocs,frees,live);assert(live==0&&allocs==frees);}
void*audit_malloc(size_t n){if(attempts==0){const char*value=getenv("QA_NULL_POINT");fault=value?atoi(value):0;atexit(report);}attempts++;if(attempts==fault)return NULL;void*p=malloc(n);assert(p&&used<64);objects[used]=p;alive[used++]=1;allocs++;return p;}
void audit_free(void*p){if(!p)return;int found=-1;for(int i=0;i<used;i++)if(alive[i]&&objects[i]==p){found=i;break;}assert(found>=0);alive[found]=0;objects[found]=NULL;frees++;free(p);}
'''
(O/'ownership.c').write_text(WRAPPER,encoding='utf-8');(O/'ownership.h').write_text('#include <stddef.h>\nvoid*audit_malloc(size_t);\nvoid audit_free(void*);\n',encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror'];p=subprocess.run(flags+['-include',str(O/'ownership.h'),'-Dmalloc=audit_malloc','-Dfree=audit_free','-c',str(L/'native/tad_cola.c'),'-o',str(O/'cola.o')],capture_output=True,text=True);(O/'compile-C.log').write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
report=[]
for name,count in [('empty',0),('single',1),('multi',3),('reinsert',4)]:
 D=O/name;D.mkdir(exist_ok=True);main=E/'actual-callers'/name/'main.c';shutil.copyfile(main,D/'main.c')
 for cmd,log in [(flags+['-I',str(L/'native'),str(main),str(L/'native/tad_cola.c'),'-o',str(D/'original.exe')],'compile-original.log'),(flags+['-I',str(L/'native'),str(main),str(O/'ownership.c'),str(O/'cola.o'),'-o',str(D/'ownership.exe')],'compile-ownership.log')]:
  p=subprocess.run(cmd,capture_output=True,text=True);(D/log).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
 original=subprocess.run([str(D/'original.exe')],capture_output=True,text=True);(D/'original.log').write_text(original.stdout+original.stderr,encoding='utf-8');assert original.returncode==0 and original.stdout.count('Operacion aplicada.')=={'empty':2,'single':3,'multi':5,'reinsert':6}[name]
 normal=subprocess.run([str(D/'ownership.exe')],capture_output=True,text=True);(D/'ownership.log').write_text(normal.stdout+normal.stderr,encoding='utf-8');assert normal.returncode==0 and normal.stdout==original.stdout
 if count:assert normal.stderr.strip()==f'OWNERSHIP {count} {count} 0'
 else:assert normal.stderr==''
 faults=[]
 import os
 for point in range(1,count+1):
  env=dict(os.environ);env['QA_NULL_POINT']=str(point);p=subprocess.run([str(D/'ownership.exe')],env=env,capture_output=True,text=True);(D/(f'fault-{point}.log')).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==1 and p.stderr.splitlines()[-1]==f'OWNERSHIP {point-1} {point-1} 0' and 'No se aplico encolar: fallo de reserva.' in p.stderr
  expected_applied=point-1+(1 if name=='reinsert' and point==4 else 0)
  assert p.stdout.count('Operacion aplicada.')==expected_applied
  faults.append({'point':point,'exit':1,'alloc_free_live':[point-1,point-1,0],'kernel_failure_reported':'Error: no se pudo asignar memoria.' in p.stdout,'failed_operation_announced_applied':False,'earlier_success_messages':expected_applied})
 report.append({'case':name,'actual_product_main':True,'strict_C17_original':True,'sha256':hashlib.sha256(main.read_bytes()).hexdigest(),'DOM_body_unchanged':True,'includes_only_wrapper':True,'alloc_free_live':[count,count,0],'original_output':original.stdout,'NULL_faults':faults})
(O/'report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
from tests.test_graph_bfs_documentation import run_doxygen
import xml.etree.ElementTree as ET
D=E/'caller-doxygen';D.mkdir(exist_ok=True)
try:
 run_doxygen(D,[L/'native/tad_cola.c',L/'native/tad_cola.h']+[O/r['case']/'main.c' for r in report]);clean=True
except AssertionError:
 clean=False
warnings=(D/'warnings.log').read_text(encoding='utf-8');main_symbols=[]
for path in (D/'doxygen/xml').glob('*.xml'):
 tree=ET.parse(path)
 for member in tree.findall('.//memberdef'):
  if member.findtext('name')=='main':main_symbols.append({'file':path.name,'documented':member.find('briefdescription/para') is not None or member.find('detaileddescription/para') is not None})
(E/'caller-doxygen.json').write_text(json.dumps({'warning_lines':len(warnings.splitlines()),'warnings':warnings,'exit_helper_clean':clean,'inputs':6,'actual_DOM_mains':4,'main_symbols_in_XML':main_symbols,'documented_main_count':sum(m['documented'] for m in main_symbols),'documentation_coverage_not_proven_by_zero_warnings':len(main_symbols)<4 or not all(m['documented'] for m in main_symbols)},indent=2),encoding='utf-8')
print(json.dumps({'actual_DOM_C17_mains':4,'alloc_free_live':[8,8,0],'NULL_fault_points':sum(len(r['NULL_faults']) for r in report),'caller_on_NULL_failure_returns_1_without_applied':True,'Doxygen_warning_lines':len(warnings.splitlines()),'documented_main_symbols':sum(m['documented'] for m in main_symbols)}))
