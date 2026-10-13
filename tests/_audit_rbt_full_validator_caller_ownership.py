"""Measure actual DOM callers using kernel-only malloc/free wrappers."""
import json,subprocess,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];E=ROOT/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-red-black-full-validator-implementation-medium';O=E/'caller-ownership'
hooks=r'''#include <stdlib.h>
#include <stdio.h>
static void *live[128];static int allocations,frees;
void *rnqa_malloc(size_t n){void *p=malloc(n);if(p){allocations++;for(int i=0;i<128;i++)if(!live[i]){live[i]=p;return p;}exit(93);}return p;}
void rnqa_free(void *p){if(p){int found=0;for(int i=0;i<128;i++)if(live[i]==p){live[i]=NULL;found=1;break;}if(!found)exit(94);frees++;}free(p);}
static void report(void){int alive=0;for(int i=0;i<128;i++)if(live[i])alive++;printf("QA_OWNER %d %d %d\n",allocations,frees,alive);}
static void __attribute__((constructor)) init(void){atexit(report);}
'''
(O/'hooks.c').write_text(hooks,encoding='utf-8');rows=[]
for case,p in enumerate(sorted((E/'main-browser').rglob('before/main.c'))):
 target=O/str(case);target.mkdir(exist_ok=True)
 for file in ['main.c','tad_rojo_negro.h']:(target/file).write_bytes((p.parent/file).read_bytes())
 (target/'tad_rojo_negro.c').write_bytes((ROOT/'docs/tads_C/tad_rojo_negro.c').read_bytes())
 kernel=['gcc','-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror','-Dmalloc=rnqa_malloc','-Dfree=rnqa_free','-c',str(target/'tad_rojo_negro.c'),'-o',str(target/'kernel.o')];b=subprocess.run(kernel,capture_output=True,text=True,timeout=30);assert b.returncode==0,b.stderr
 cmd=['gcc','-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'main.c'),str(target/'kernel.o'),str(O/'hooks.c'),'-o',str(target/'main.exe')];b=subprocess.run(cmd,capture_output=True,text=True,timeout=30);(target/'compile.log').write_text(b.stdout+b.stderr,encoding='utf-8');assert b.returncode==0,b.stderr
 r=subprocess.run([str((target/'main.exe').resolve())],capture_output=True,text=True,timeout=5);assert r.returncode==0,r.stderr;(target/'stdout.log').write_text(r.stdout,encoding='utf-8');vals=list(map(int,r.stdout.split('QA_OWNER ')[1].split()));assert vals[0]==vals[1] and vals[2]==0;rows.append(dict(case=str(p.parent),allocations=vals[0],frees=vals[1],alive=vals[2],main_sha256=hashlib.sha256(p.read_bytes()).hexdigest()))
assert len(rows)==4,len(rows);(O/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');print('Caller kernel ownership',sum(r['allocations'] for r in rows),sum(r['frees'] for r in rows),'alive0')
