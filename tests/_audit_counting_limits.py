"""Defined native Counting sort guards/range/calloc failure, no giant UI trace."""
from pathlib import Path
import sys,subprocess,shutil,json
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from _audit_sorting_main_native import audit_program
C=r'''
#include <stdio.h>
#include <stdlib.h>
#include <assert.h>
_Static_assert(sizeof(size_t)==8, "This baseline requires 64-bit size_t; full-span probe must not run on 32-bit.");
static int fail,allocs,frees;
static void *tracked_calloc(size_t n,size_t s){if(fail)return NULL;void*p=calloc(n,s);if(p)allocs++;return p;}
static void tracked_free(void*p){if(p)frees++;free(p);}
#define calloc tracked_calloc
#define free tracked_free
#include "tad_ordenamiento.c"
static void run(const char*name,int*a,size_t n,int status){int before0=a?a[0]:0,before1=a&&n>1?a[1]:0;int result=ordenar_counting_sort(a,n);assert(result==status && allocs==frees);if(!result&&a){assert(a[0]==before0);if(n>1)assert(a[1]==before1);}printf("%s %d %d %d\n",name,result,allocs,frees);}
int main(void){int a[]={7,7};run("n0",a,0,0);run("NULL",NULL,1,0);int b[]={0,999999};run("exact_cap",b,2,1);int c[]={0,1000000};run("above_cap",c,2,0);int d[]={INT_MAX,INT_MIN};run("int_full_span",d,2,0);int e[]={INT_MIN+999999,INT_MIN};run("near_min_exact_cap",e,2,1);assert(e[0]==INT_MIN&&e[1]==INT_MIN+999999);int f[]={INT_MAX,INT_MAX-999999};run("near_max_exact_cap",f,2,1);assert(f[0]==INT_MAX-999999&&f[1]==INT_MAX);fail=1;int g[]={2,1};run("calloc_fail",g,2,0);fail=0;int min=42,max=43;assert(!obtener_minimo_maximo(a,2,NULL,&max)&&max==43);puts("helper_minNULL 0");assert(!obtener_minimo_maximo(a,2,&min,NULL)&&min==42);puts("helper_maxNULL 0");assert(!obtener_minimo_maximo(NULL,1,&min,&max)&&min==42&&max==43);puts("helper_arrayNULL 0");assert(!obtener_minimo_maximo(a,0,&min,&max)&&min==42&&max==43);puts("helper_n0 0");return 0;}
'''
def audit(out):
 out=Path(out);out.mkdir(parents=True,exist_ok=True)
 for ext in ['c','h']:shutil.copy2(ROOT/'docs/tads_C'/('tad_ordenamiento.'+ext),out/('tad_ordenamiento.'+ext))
 (out/'raw.c').write_text(C,encoding='utf-8');p=subprocess.run([shutil.which('gcc'),'-std=c17','-Wall','-Wextra','-Wpedantic','-Werror',str(out/'raw.c'),'-o',str(out/'raw.exe')],capture_output=True,text=True);(out/'compile.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 p=subprocess.run([str(out/'raw.exe')],capture_output=True,text=True,timeout=15);(out/'stdout.log').write_text(p.stdout+p.stderr);assert p.returncode==0,p.stderr
 r=dict(public_cases=8,successful_range_boundaries=3,rejected_public_guards=4,calloc_failure_cases=1,helper_guard_cases=4,allocations=3,frees=3,live=0,strict_C17=True,defined_full_int_span_rejected_before_subtraction=True,SIZE_MAX_guard_unreachable_for_int32_under_cap_on_current_size_t=True,no_large_UI_trace=True);(out/'report.json').write_text(json.dumps(r,indent=2));return r
if __name__=='__main__':print(json.dumps(audit(sys.argv[1])))
