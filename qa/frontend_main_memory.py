"""Count allocations in unchanged TADs linked to exact generated main programs."""
import json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];out=ROOT.parent/'qa_frontend_main';
SOURCES=dict(zip(['queue','priority_queue','linked_list','circular_list','sublist','abb','avl','red_black','binary_heap'],['tad_cola','tad_cola_prioridad','tad_lista','tad_lista_circular','tad_sublista','tad_abb','tad_avl','tad_rojo_negro','tad_monticulo_binario']))
shim=out/'allocation_observer.c'
shim.write_text('''#include <stdio.h>
#include <stddef.h>
void *__real_malloc(size_t); void *__real_calloc(size_t,size_t); void *__real_realloc(void *,size_t); void __real_free(void *); int __real_main(void);
static long live = 0;
void *__wrap_malloc(size_t n) { void *p = __real_malloc(n); if (p != NULL) ++live; return p; }
void *__wrap_calloc(size_t n, size_t s) { void *p = __real_calloc(n,s); if (p != NULL) ++live; return p; }
void *__wrap_realloc(void *p, size_t n) { int existed = p != NULL; void *q = __real_realloc(p,n); if (!existed && q != NULL) ++live; else if (existed && n == 0 && q == NULL) --live; return q; }
void __wrap_free(void *p) { if (p != NULL) --live; __real_free(p); }
int __wrap_main(void) { int code = __real_main(); fprintf(stderr,"QA_ALLOCATION_BALANCE=%ld\\n",live); return live == 0 ? code : 42; }
''')
results=[]
for id,source in SOURCES.items():
 exe=out/f'{id}-allocation-observed';cmd=['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-I',str(ROOT/'docs/tads_C'),str(out/f'{id}.c'),str(ROOT/'docs/tads_C'/f'{source}.c'),str(shim),'-Wl,--wrap=malloc,--wrap=calloc,--wrap=realloc,--wrap=free,--wrap=main','-o',str(exe)]
 subprocess.run(cmd,check=True,capture_output=True,text=True);r=subprocess.run([str(exe)],text=True,capture_output=True,timeout=5)
 results.append(dict(structure=id,exit_code=r.returncode,stderr=r.stderr,stdout=r.stdout));print(id,'PASS' if r.returncode==0 else 'FAIL',r.stderr.strip())
 if r.returncode != 0: raise RuntimeError(f'{id}: allocation observer failed: {r.stderr}')
(out/'allocation-results.json').write_text(json.dumps(results,ensure_ascii=False,indent=2))
# Change input only in a disposable QA copy: printed query values must change.
source=(out/'abb.c').read_text().replace('abb_insertar(arbol, 5)','abb_insertar(arbol, 50)')
variant=out/'abb_changed_input_qa_only.c';variant.write_text(source);exe=out/'abb-changed-input'
subprocess.run(['gcc','-std=c17','-Wall','-Wextra','-Werror','-pedantic','-I',str(ROOT/'docs/tads_C'),str(variant),str(ROOT/'docs/tads_C/tad_abb.c'),'-o',str(exe)],check=True)
r=subprocess.run([str(exe)],capture_output=True,text=True,check=True)
if 'MAXIMO: 50' not in r.stdout: raise RuntimeError(f'Dynamic query did not follow edited input: {r.stdout}')
print('PASS edited input in disposable QA main changes computed MAXIMO to 50')
(out/'dynamic-query-stdout.txt').write_text(r.stdout)
