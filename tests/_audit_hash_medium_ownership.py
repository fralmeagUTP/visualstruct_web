"""Compile authentic browser/HTTP callers and observe cleanup under each malloc NULL."""
from pathlib import Path
import json,subprocess,shutil,sys
ROOT=Path.cwd();E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-hash-create-insert-instructions-medium';N=E/'caller-ownership';N.mkdir(exist_ok=True)
HEADER='#include <stddef.h>\nvoid *owned_malloc(size_t);\nvoid owned_free(void*);\n'
DRIVER=r'''#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
static void *objects[512];static int live[512],used,allocations,frees,attempts,fault;
void *owned_malloc(size_t size){attempts++;if(attempts==fault)return NULL;void*p=malloc(size);if(p){assert(used<512);objects[used]=p;live[used++]=1;allocations++;}return p;}
void owned_free(void*p){if(p){int found=0;for(int j=0;j<used;j++)if(live[j]&&objects[j]==p){live[j]=0;found=1;break;}assert(found);frees++;}free(p);}
int student_main(void);
int main(void){const char*s=getenv("HASH_QA_FAULT");fault=s?atoi(s):0;int result=student_main();for(int j=0;j<used;j++)assert(!live[j]);assert(allocations==frees);printf("OWNERSHIP %d %d 0 %d %d\n",allocations,frees,attempts,result);return 0;}
'''
(N/'ownership.h').write_text(HEADER);(N/'driver.c').write_text(DRIVER)
compiler=shutil.which('gcc');assert compiler
cmd=[compiler,'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']

def call(args,log):
 r=subprocess.run(args,capture_output=True,text=True,timeout=30);log.write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0,r.stderr;return r
call(cmd+['-I',str(E/'downloads'),'-include',str(N/'ownership.h'),'-Dmalloc=owned_malloc','-Dfree=owned_free','-c',str(E/'downloads/tad_tabla_hash.c'),'-o',str(N/'hash.o')],N/'hash-compile.log')
sources=[Path(arg) for arg in sys.argv[1:]] if sys.argv[1:] else [E/'downloads/main.c']+list((E/'browser').glob('*/main.c'));reports=json.loads((N/'report.json').read_text(encoding='utf-8')) if sys.argv[1:] else []
for i,source in enumerate(sources,start=len(reports)):
 directory=N/str(i);directory.mkdir(exist_ok=True);shutil.copyfile(source,directory/'main.c')
 call(cmd+['-I',str(E/'downloads'),str(directory/'main.c'),str(E/'downloads/tad_tabla_hash.c'),'-o',str(directory/'original.exe')],directory/'original-compile.log');normal=call([str(directory/'original.exe')],directory/'original-run.log')
 call(cmd+['-I',str(E/'downloads'),'-Dmain=student_main','-c',str(directory/'main.c'),'-o',str(directory/'main.o')],directory/'main-observed-compile.log')
 call(cmd+[str(directory/'main.o'),str(N/'hash.o'),str(N/'driver.c'),'-o',str(directory/'observed.exe')],directory/'observed-compile.log')
 run=call([str(directory/'observed.exe')],directory/'observed-run.log');tail=run.stdout.splitlines()[-1].split();attempts=int(tail[-2]);assert tail[-1]=='0';faults=[]
 for point in range(1,attempts+1):
  import os
  env={**os.environ,'HASH_QA_FAULT':str(point)};r=subprocess.run([str(directory/'observed.exe')],capture_output=True,text=True,env=env,timeout=10);(directory/f'fault-{point}.log').write_text(r.stdout+r.stderr,encoding='utf-8');assert r.returncode==0;last=r.stdout.splitlines()[-1].split();assert last[-1]=='1' and last[1]==last[2];faults.append({'point':point,'allocations':int(last[1]),'frees':int(last[2]),'live':0,'caller_status':1})
 reports.append({'source':str(source.relative_to(ROOT)),'strict_c17_original':True,'allocations':int(tail[1]),'frees':int(tail[2]),'live':0,'faults':faults,'stdout':normal.stdout})
(N/'report.json').write_text(json.dumps(reports,indent=2),encoding='utf-8');print(json.dumps(reports))
