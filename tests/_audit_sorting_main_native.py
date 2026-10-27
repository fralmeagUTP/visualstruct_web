"""Native compile/ownership checks for bytes captured from actual sorting downloads."""
from __future__ import annotations
from pathlib import Path
import json,re,subprocess,shutil,hashlib
from test_graph_bfs_documentation import run_doxygen

OBSERVER=r'''#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
static void *ptrs[8192];static int live[8192],total,allocs,frees,attempts;
static void *track(void*p){if(p){assert(total<8192);ptrs[total]=p;live[total++]=1;allocs++;}return p;}
void *owned_malloc(size_t n){attempts++;return track(malloc(n));}
void *owned_calloc(size_t n,size_t z){attempts++;return track(calloc(n,z));}
void owned_free(void*p){if(p){int found=0;for(int i=0;i<total;i++){if(live[i]&&ptrs[i]==p){live[i]=0;found=1;break;}}assert(found);frees++;}free(p);}
static void ownership_done(void){for(int i=0;i<total;i++){assert(!live[i]);}assert(allocs==frees);printf("OWNERSHIP %d %d 0 ATTEMPTS %d\n",allocs,frees,attempts);}
int downloaded_main(void);
int main(void){int status=downloaded_main();ownership_done();return status;}
'''
HEADER='#include <stddef.h>\nvoid *owned_malloc(size_t);\nvoid *owned_calloc(size_t,size_t);\nvoid owned_free(void*);\n'

def audit_program(target: Path,expected: list[list[int]]) -> dict:
    """Compile captured download bytes and observe the unchanged caller via renamed main."""
    cc=shutil.which('gcc');assert cc
    command=[cc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'main.c'),str(target/'tad_ordenamiento.c'),'-o',str(target/'main.exe')]
    p=subprocess.run(command,capture_output=True,text=True,timeout=30);(target/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0 and not p.stderr,p.stderr
    p=subprocess.run([str(target/'main.exe')],capture_output=True,text=True,timeout=10);(target/'stdout.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    arrays=[json.loads(line) for line in p.stdout.splitlines() if line.startswith('[')];assert arrays==expected,(arrays,expected)
    source=(target/'main.c').read_text(encoding='utf-8');runs=source.count('printf("Run ')
    assert len(re.findall(r'^Run \d+: ordenar_',p.stdout,re.M))==runs
    run_doxygen(target,[target/'main.c',target/'tad_ordenamiento.c',target/'tad_ordenamiento.h'])
    (target/'ownership.h').write_text(HEADER);(target/'observer.c').write_text(OBSERVER)
    compile_obj=lambda extra,src,obj:subprocess.run([cc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',*extra,'-c',str(target/src),'-o',str(target/obj)],capture_output=True,text=True,timeout=30)
    p=compile_obj(['-include',str(target/'ownership.h'),'-Dmalloc=owned_malloc','-Dcalloc=owned_calloc','-Dfree=owned_free'],'tad_ordenamiento.c','sorting-owned.o');assert p.returncode==0,p.stderr
    p=compile_obj(['-Dmain=downloaded_main'],'main.c','caller-owned.o');assert p.returncode==0,p.stderr
    p=subprocess.run([cc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'observer.c'),str(target/'caller-owned.o'),str(target/'sorting-owned.o'),'-o',str(target/'owned.exe')],capture_output=True,text=True);assert p.returncode==0,p.stderr
    p=subprocess.run([str(target/'owned.exe')],capture_output=True,text=True,timeout=10);(target/'owned.stdout.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
    m=re.search(r'OWNERSHIP (\d+) (\d+) 0 ATTEMPTS (\d+)',p.stdout);assert m and m[1]==m[2]
    report={'actual_UI_download':True,'strict_C17':True,'doxygen_warnings':0,'successful_native_runs':runs,'arrays':arrays,'allocations':int(m[1]),'frees':int(m[2]),'live':0,'allocation_attempts':int(m[3]),'source_hashes':{name:hashlib.sha256((target/name).read_bytes()).hexdigest() for name in ['main.c','tad_ordenamiento.c','tad_ordenamiento.h']},'instruction_fidelity_proof':False}
    # Native failure probe only when the public method communicates status.
    if 'int estado_' in source:
        fault=OBSERVER.replace('return track(malloc(n));','if(attempts==1)return NULL;return track(malloc(n));').replace('return track(calloc(n,z));','if(attempts==1)return NULL;return track(calloc(n,z));')
        (target/'observer-fault.c').write_text(fault);p=subprocess.run([cc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(target/'observer-fault.c'),str(target/'caller-owned.o'),str(target/'sorting-owned.o'),'-o',str(target/'fault.exe')],capture_output=True,text=True);assert p.returncode==0,p.stderr
        p=subprocess.run([str(target/'fault.exe')],capture_output=True,text=True,timeout=10);(target/'fault.stdout.log').write_text(p.stdout+p.stderr);assert p.returncode==1 and 'El TAD reporto un fallo' in p.stderr
        m=re.search(r'OWNERSHIP (\d+) (\d+) 0 ATTEMPTS (\d+)',p.stdout);assert m and m[1]==m[2];report['first_allocation_failure']={'returncode':1,'allocations':int(m[1]),'frees':int(m[2]),'live':0,'no_success_array_after_failure':len([line for line in p.stdout.splitlines() if line.startswith('[')])==1};assert report['first_allocation_failure']['no_success_array_after_failure']
    (target/'native-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8');return report
