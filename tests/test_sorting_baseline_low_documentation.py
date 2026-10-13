"""Actual sorting HTTP docs and independent allocation observer over110recorded native calls."""
from pathlib import Path
import re,json,subprocess,shutil
from test_graph_bfs_documentation import run_doxygen
from app.domain.sorting.pedagogy import theory_profile

def test_download_docs_complexity_and_native_ownership(client,tmp_path):
 root=Path(__file__).resolve().parents[1];files=[]
 for kind,ext in [('source','c'),('header','h')]:
  r=client.get('/help/source/sorting_array/'+kind);assert r.status_code==200;p=tmp_path/('tad_ordenamiento.'+ext);p.write_bytes(r.data);files.append(p)
  s=p.read_text(encoding='utf-8-sig');assert s.count('@note Arreglo NULL o n==0')==11
  assert 'heapify recursivo usa pila O(log n)' in s and 'inversion final del grupo negativo' in s and 'Delegacion exacta a Counting Sort' in s
 run_doxygen(tmp_path,files)
 assert theory_profile('radixsort')['stable'] is False
 assert 'pila' in theory_profile('heapsort')['memory'] and 'peor' in theory_profile('quicksort')['memory']
 before=root/'openspec/changes/archive/2026-10-13-audit-local-quality-and-unified-controls/evidence/visible-sorting-baseline-low/native-api-before'
 strip=lambda s:re.sub(r'/\*.*?\*/|//[^\n]*','',s,flags=re.S)
 assert strip((before/'tad_ordenamiento.c').read_text(encoding='utf-8-sig'))==strip((tmp_path/'tad_ordenamiento.c').read_text(encoding='utf-8-sig'))
 original=(before/'observed-main.c').read_text(encoding='utf-8');assert original.count('printf("CASE ')==110
 (tmp_path/'ownership.h').write_text('#include <stddef.h>\nvoid *owned_malloc(size_t);\nvoid *owned_calloc(size_t,size_t);\nvoid owned_free(void*);\nvoid ownership_done(void);\n',encoding='utf-8')
 observer=r"""#include <stdlib.h>
#include <stdio.h>
#include <assert.h>
static void *ptrs[4096];static int live[4096],total,allocs,frees;
static void *track(void*p){if(p){assert(total<4096);ptrs[total]=p;live[total++]=1;allocs++;}return p;}
void *owned_malloc(size_t n){return track(malloc(n));}
void *owned_calloc(size_t n,size_t z){return track(calloc(n,z));}
void owned_free(void*p){if(p){int found=0;for(int i=0;i<total;i++){if(live[i]&&ptrs[i]==p){live[i]=0;found=1;break;}}assert(found);frees++;}free(p);}
void ownership_done(void){for(int i=0;i<total;i++)assert(live[i]==0);assert(allocs==frees);printf("OWNERSHIP %d %d 0\n",allocs,frees);}
"""
 (tmp_path/'observer.c').write_text(observer,encoding='utf-8');main='#include "ownership.h"\n'+original.replace('return 0;}','ownership_done();return 0;}');(tmp_path/'owned-main.c').write_text(main,encoding='utf-8');cc=shutil.which('gcc');assert cc
 obj=tmp_path/'sorting.o';p=subprocess.run([cc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror','-include',str(tmp_path/'ownership.h'),'-Dmalloc=owned_malloc','-Dcalloc=owned_calloc','-Dfree=owned_free','-c',str(tmp_path/'tad_ordenamiento.c'),'-o',str(obj)],capture_output=True,text=True,timeout=30);assert p.returncode==0 and not p.stderr,p.stderr
 exe=tmp_path/'owned.exe';p=subprocess.run([cc,'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(tmp_path/'owned-main.c'),str(tmp_path/'observer.c'),str(obj),'-o',str(exe)],capture_output=True,text=True,timeout=30);assert p.returncode==0 and not p.stderr,p.stderr
 p=subprocess.run([str(exe)],capture_output=True,text=True,timeout=15);assert p.returncode==0,p.stderr;(tmp_path/'owned.stdout.log').write_text(p.stdout,encoding='utf-8');m=re.search(r'OWNERSHIP (\d+) (\d+) 0',p.stdout);assert m and m[1]==m[2]
 (tmp_path/'doc-ownership-report.json').write_text(json.dumps({'native_calls':110,'original_actual_ui_main':False,'equivalent_native_harness':True,'allocations':int(m[1]),'frees':int(m[2]),'live':0,'doxygen_warnings':0,'normal_allocation_only':True},indent=2),encoding='utf-8')
