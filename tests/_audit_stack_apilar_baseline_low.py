"""Safe C push allocation/field masks versus API; no product corrections."""
from pathlib import Path
import sys,json,subprocess,shutil,hashlib
R=Path.cwd();sys.path.insert(0,str(R));sys.stdout.reconfigure(encoding='utf-8')
from app import create_app
E=R/'openspec/changes/audit-local-quality-and-unified-controls/evidence/visible-stack-apilar-baseline-low';N=E/'native';N.mkdir(exist_ok=True);app=create_app();app.config['TESTING']=True;c=app.test_client();downloads={}
for kind,ext in [('source','c'),('header','h')]:
 r=c.get('/help/source/stack/'+kind);assert r.status_code==200;data=r.data;p=N/('tad_pila.'+ext);p.write_bytes(data);assert data==(R/('docs/tads_C/tad_pila.'+ext)).read_bytes();downloads[kind]={'HTTP':200,'sha256':hashlib.sha256(data).hexdigest()}
C=(N/'tad_pila.c').read_text(encoding='utf-8-sig');start=C.index('void pila_apilar(');end=C.index('\n}',start)+2;body=C[start:end]
patched=body.replace('{\n','{\n    qa_event("entry",p,-1);\n',1).replace('if (p == NULL) {','if (qa_guard("root_guard",p,p == NULL)) {').replace('    ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));','    ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));\n    _Static_assert(_Generic(aux,ptrPila:1,default:0),"aux type");\n    qa_capture(aux);qa_event("aux_allocated",p,-1);').replace('if (aux == NULL) {','if (qa_guard("allocation_guard",p,aux == NULL)) {').replace('aux->nro = valor;','aux->nro = valor;qa_field(aux,1);qa_event("value_assigned",p,-1);').replace('aux->sgte = *p;','aux->sgte = *p;qa_field(aux,2);qa_event("link_assigned",p,-1);').replace('*p = aux;','*p = aux;qa_event("root_assigned",p,-1);').replace('        return;','        qa_event("return",p,-1);return;').replace('printf("Error: pila no inicializada.\\n");','printf("Error: pila no inicializada.\\n");qa_event("root_error_printf",p,-1);').replace('printf("Error: No se pudo asignar memoria.\\n");','printf("Error: No se pudo asignar memoria.\\n");qa_event("allocation_error_printf",p,-1);');patched=patched.replace('printf(', 'qa_printf(');patched=patched[:-1]+'    qa_event("return",p,-1);\n}';(N/'instrumented.c').write_text(C[:start]+patched+C[end:],encoding='utf-8')
(N/'hooks.h').write_text('#include <stddef.h>\nstruct NodoPila;\nvoid qa_event(const char*,struct NodoPila**,int);\nint qa_guard(const char*,struct NodoPila**,int);\nvoid qa_capture(struct NodoPila*);\nvoid qa_field(struct NodoPila*,int);\nvoid*qa_malloc(size_t);\nvoid qa_free(void*);\nint qa_printf(const char*,...);\n',encoding='utf-8')
DRIVER=r"""#include <assert.h>
#include <stdio.h>
#include <stdlib.h>
#include <stdarg.h>
#include <string.h>
#include <limits.h>
#include "tad_pila.h"
_Static_assert(_Generic(&pila_apilar,void(*)(ptrPila*,int):1,default:0),"push signature");
static void*obj[64];static int live[64],mask[64],used,allocs,frees,active,sid,aux_init,aux_id,fail_next;static ptrPila*root;static char console[256];
static int id(void*p){if(!p)return -1;for(int j=0;j<used;j++)if(live[j]&&obj[j]==p)return j;assert(0);return -1;}
static void string(const char*s){putchar('"');for(;*s;s++){if(*s=='\n')fputs("\\n",stdout);else if(*s=='"')fputs("\\\"",stdout);else if(*s=='\\')fputs("\\\\",stdout);else putchar(*s);}putchar('"');}
void qa_event(const char*e,ptrPila*p,int condition){if(!active)return;
 printf("{\"sample\":%d,\"event\":\"%s\",\"condition\":%d,\"root_argument_NULL\":%d,\"aux_initialized\":%d,\"aux_id\":%d,\"root_ids\":[",sid,e,condition,p==NULL,aux_init,aux_init?aux_id:-1);
 ptrPila n=p?*p:NULL;int comma=0;while(n){int j=id(n);assert(mask[j]==3);if(comma++)putchar(',');printf("%d",j);n=n->sgte;}fputs("],\"root_values\":[",stdout);n=p?*p:NULL;comma=0;while(n){assert(mask[id(n)]==3);if(comma++)putchar(',');printf("%d",n->nro);n=n->sgte;}fputs("],\"live\":[",stdout);comma=0;
 for(int j=0;j<used;j++)if(live[j]){if(comma++)putchar(',');ptrPila n=obj[j];printf("{\"id\":%d,\"mask\":%d,\"value\":",j,mask[j]);if(mask[j]&1)printf("%d",n->nro);else fputs("null",stdout);fputs(",\"next_id\":",stdout);if(mask[j]&2)printf("%d",id(n->sgte));else fputs("null",stdout);putchar('}');}
 fputs("],\"console\":",stdout);string(console);puts("}");}
int qa_guard(const char*e,ptrPila*p,int v){qa_event(e,p,v);return v;}
void qa_capture(ptrPila p){if(active){aux_init=1;aux_id=id(p);}}
void qa_field(ptrPila p,int bit){mask[id(p)]|=bit;}
void*qa_malloc(size_t size){qa_event("allocator_enter",root,-1);if(active&&fail_next){fail_next=0;qa_event("allocator_NULL_return",root,-1);return NULL;}void*p=malloc(size);assert(p&&used<64);obj[used]=p;live[used]=1;mask[used++]=0;allocs++;qa_event("allocator_success_return",root,-1);return p;}
void qa_free(void*p){if(!p)return;int j=id(p);live[j]=0;obj[j]=NULL;mask[j]=0;frees++;free(p);}
int qa_printf(const char*fmt,...){va_list args;va_start(args,fmt);int result=vsnprintf(console,sizeof(console),fmt,args);va_end(args);return result;}
static void sample(ptrPila*p,int value,int fault){aux_init=0;aux_id=-1;console[0]=0;root=p;fail_next=fault;active=1;pila_apilar(p,value);active=0;sid++;root=NULL;}
"""
CASES=[('empty',[],9),('single',[7],-1),('duplicate',[7],7),('bounds',[2147483647,-1],-2147483648)];main='int main(void){'
for name,seeds,value in CASES:
 main+='{ptrPila p=NULL;'
 for v in seeds:main+=f'pila_apilar(&p,{v});'
 literal='INT_MIN' if value==-2147483648 else str(value);main+=f'sample(&p,{literal},0);sample(&p,{literal},0);sample(&p,{literal},1);pila_destruir(&p);}}'
main+=r'sample(NULL,9,0);assert(allocs==frees);for(int j=0;j<used;j++)assert(!live[j]);fprintf(stderr,"OWNERSHIP %d %d 0\n",allocs,frees);return 0;}'
(N/'driver.c').write_text(DRIVER+main,encoding='utf-8');flags=[shutil.which('gcc'),'-std=c17','-O2','-Wall','-Wextra','-Wpedantic','-Werror']
for cmd,log in [(flags+['-include',str(N/'hooks.h'),'-Dmalloc=qa_malloc','-Dfree=qa_free','-c',str(N/'instrumented.c'),'-o',str(N/'pila.o')],'compile-source.log'),(flags+[str(N/'driver.c'),str(N/'pila.o'),'-o',str(N/'driver.exe')],'compile-driver.log')]:
 p=subprocess.run(cmd,capture_output=True,text=True);(N/log).write_text(p.stdout+p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr
p=subprocess.run([str(N/'driver.exe')],capture_output=True,text=True);(N/'events.jsonl').write_text(p.stdout,encoding='utf-8');(N/'stderr.log').write_text(p.stderr,encoding='utf-8');assert p.returncode==0,p.stderr;native=[json.loads(x) for x in p.stdout.splitlines()]
rows=[];sid=0
for name,seeds,value in CASES:
 c=app.test_client()
 for v in seeds:assert c.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':v}}).get_json()['success']
 for repeat in [1,2]:
  r=c.post('/sequential/stack/operate',json={'operation':'apilar','payload':{'value':value}});d=r.get_json();assert r.status_code==200 and d['success'];ns=[n for n in native if n['sample']==sid];matches=[]
  for token,line in [('aux_allocated','ptrPila aux = (ptrPila) malloc(sizeof(struct NodoPila));'),('value_assigned','aux->nro = valor;'),('link_assigned','aux->sgte = *p;'),('root_assigned','*p = aux;')]:
   n=next(n for n in ns if n['event']==token);f=next(f for f in d['execution_trace']['steps'] if f['line_text'].strip()==line);values=[i['value'] for i in f['state_after']['items']];matches.append({'event':token,'root_values_match':values==n['root_values'],'native_root_values':n['root_values'],'trace_root_values':values,'native_heap_count':len(n['live']),'trace_heap_count':len(f['pedagogy']['heap_objects'])})
  assert [i['value'] for i in d['visual_state']['items']]==ns[-1]['root_values'];rows.append({'case':name,'seeds':seeds,'value':value,'repeat':repeat,'native_sample':sid,'native_events':ns,'observations':matches,'C_API_final_match':True,'data':d});sid+=1
 sid+=1
(E/'report.json').write_text(json.dumps(rows,indent=2),encoding='utf-8');(E/'native-report.json').write_text(json.dumps(native,indent=2),encoding='utf-8');(E/'downloads.json').write_text(json.dumps(downloads,indent=2),encoding='utf-8');print(json.dumps({'C_calls':len({n['sample'] for n in native}),'events':len(native),'conditions':sum(n['condition']!=-1 for n in native),'API_calls':8,'observations':sum(len(r['observations']) for r in rows),'value_divergences':sum(not o['root_values_match'] for r in rows for o in r['observations']),'ownership':p.stderr.strip(),'faults_native':4,'NULL_native':1,'no_uninitialized_fields_or_retired_pointers_read':True}))
